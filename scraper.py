#!/usr/bin/python
import urllib2
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re

keywords = ["telecom", "telecoms", "telecommunications", "telco", "email", "AT&T", "Verizon", "Sprint", "T-Mobile", "Huawei", "Vodafone", "Telefonica", "Deutsche", "Telekom", "NTT", "Softbank", "Orange", "BT", "CenturyLink", "Telstra", "KT", "LG", "Ericsson", "Nokia", "acquisition", "merger", "partnership", "operator", "operators", "strategic", "digital", "measures", "measure", "Russia", "China", "US", "UK", "Japan", "Korea", "response", "responses", "provider", "IXP", "ISP", "submarine", "cable", "latency", "latencies", "sensitive", "patent"]

high_keywords = ["security", "cybersecurity", "cyber-security", "cyber", "secure", "resiliency", "resilient", "vulnerable", "vulnerabilities", "vulnerability", "threat", "threats", "defend", "phishing", "spoofing", "spoofed", "outage", "cryptography", "hacking", "hacked", "hackers", "malicious", "cyberdefence", "attack", "attacks", "attacked", "attacker", "attackers", "cyber-attack", "cyber-defence", "defence", "defense", "encrypted", "encryption", "encrypted", "SSL", "DNS", "protect", "privacy", "law", "regulation", "regulator", "critical", "failure", "breach", "intelligence", "legislation", "leak", "leaked", "risk", "DDoS", "malware", "backdoor"]

urls = ["http://www.google.com/search?q=telecom+services+brought+down+cyberattack", "http://www.google.com/search?q=telecom+cyber+security+mitigate+risk", "http://telecoms.com/497227/orange-drops-e515-million-on-yet-another-cybersecurity-acquisition/", "https://www.lightreading.com/carrier-security.asp", "http://www.computerweekly.com/news/252459155/Malaysia-takes-broad-base-approach-to-5G-security", "http://www.computerweekly.com/news/252450417/Optus-to-acquire-Hivint-in-cyber-security-deal", "http://www.upguard.com/blog/how-secure-is-your-cell-phone-provider"]

blacklist_strings = ["http://www.allaboutcookies", "http://twitter", "http://jobs", "http://servedby", "http://shop.vodafone", "http://www.vodafone", "http://translate.google.com"]

def formatUrl(new_url):
    headers = {'User-Agent':'Mozilla 5.10'}
    request = urllib2.Request(new_url, None, headers)
    return request

def start():
    df_count = 0
    df = pd.DataFrame(columns=["url","score"])
    
    # add headers to urls, mark them as unchecked
    links = {}
    for url in urls:
        links[formatUrl(url)] = 0

    while df_count < 30:
        # get the top page and pop it off list of links
        if not links:
            print("Links dict is empty")
            break
        start_page = ""
        # get an element in dict if checked field = 0
        for x in links: 
            if not links[x]:
                start_page = x
                start_page_url = start_page.get_full_url()
                links[x] = 1
                break
        if not start_page: 
            print("Links dict is all checked")
            break
        print("trying to open " + start_page_url)
        try: 
            page = urllib2.urlopen(start_page)
        except:
            print("Could not open start_page")
            continue

        # parse html
        soup = BeautifulSoup(page, 'html.parser')

        # get words in title
        try:
            title_list = soup.title.string.split()
        except:
            print("Could not parse title")
            continue

        # get words of meta tags
        tag_list = getMeta(soup)

        # check relevance and rank URL according to score, return score
        score = 0
        score += checkRelevance(tag_list) 
        score += checkRelevance(title_list)


        # appends url to df if score > 0, can adjust criteria later
        if score >= 3:
            df.loc[df_count] = [start_page_url, score]
            df_count += 1
            df.sort_values("score")
            print df
            export_csv = df.to_csv(r'/Users/joycesin/Documents/crawler/urls.csv', index = None, header=True)

        # update list of links without duplicates, even for urls that weren't added to df cause they might be search result pages etc
        new_links = getLinks(soup)
        new_links.update(links)
        links = new_links
    




# get a list of meta tags
def getMeta(soup):
    tag_list = set()
    tags = soup.find_all("meta", property="article:tag")
    for tag in tags:
        tag_list.add(tag.get("content", None))
    return tag_list


# expects a list of words to check against list of keywords, scores out of 10 matches
def checkRelevance(tags):
    score = 0
    for tag in tags:
        if tag in keywords:
            print("Keyword found: " + tag)
            score += 1
        if tag in high_keywords:
            print("High Keyword found: " + tag)
            score += 2            
    return score

def check_blacklist(new_link):
    for blacklist in blacklist_strings:
        if new_link.startswith(blacklist):
            return True
    return False
# returns dict with keys as urls and values as 0 -- unchecked
def getLinks(soup):
    new_links = {}

    for link in soup.findAll('a', attrs={'href': re.compile("^http://")}):
        # filter out twitter, other junk pages
        new_link = link.get('href')
        if check_blacklist(new_link):
            continue
        new_links[formatUrl(link.get('href'))] = 0
    #print new_links
    return new_links


start()
    

