#!/usr/bin/python
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import requests

keywords = ["telecom", "telecoms", "telecommunications", "telco", "AT&T", "Verizon", "Sprint", "T-Mobile", "Huawei", "Vodafone", "Telefonica", "Deutsche", "Telekom", "NTT", "Softbank", "Orange", "BT", "CenturyLink", "Telstra", "KT", "LG", "Ericsson", "Nokia", "operator", "operators", "digital", "provider", "ISP", "cable", "broadband", "attack", "attacks"]

high_keywords = ["security", "cybersecurity", "cyber-security", "cyber", "secure", "resiliency", "resilient", "vulnerable", "vulnerabilities", "vulnerability", "threat", "threats", "defend", "phishing", "spoofing", "spoofed", "outage", "cryptography", "hacking", "hacked", "hackers", "malicious", "cyberdefence", "attack", "attacks", "attacked", "attacker", "attackers", "cyber-attack", "cyberattack", "cyberattacks", "cyber-attacks", "cyberdefence", "cyber-defence", "defence", "defense", "encrypted", "encryption", "encrypted", "SSL", "DNS", "protect", "privacy", "law", "regulation", "regulator", "critical", "failure", "breach", "intelligence", "leak", "leaked", "risk", "DDoS", "malware", "backdoor"]

# SEED URLS
urls = ["http://www.google.com/search?q=telecom+services+brought+down+cyberattack", "http://www.google.com/search?q=telecom+cyber+security+mitigate+risk"]

def start():
    df_count = 0
    df = pd.DataFrame(columns=["url","score"])
    
    # mark urls as unchecked
    links = {}
    for url in urls:
        links[url] = 0

    while df_count < 100:
        # get the top page and pop it off list of links
        if not links:
            print("Links dictionary is empty")
            break
        start_page = ""
        new_links = {}
        # get an element in dict if checked field = 0
        for x in links: 
            if not links[x]:
                start_page = x
                links[x] = 1
                break
        if not start_page: 
            print("Links dictionary is all checked")
            break

        try: 
            page = requests.get(start_page, headers={'User-Agent':'Mozilla 5.10'})
            print("opened " + start_page)
        except:
            print("Could not open page")
            continue

        # parse html
        try: 
            soup = BeautifulSoup(page.text, "html.parser")
        except:
            print("Could not make soup")
            continue

        # handle google search cases
        if start_page.startswith("http://www.google"):
            for link in soup.find_all('a'):
                try:
                    new_link = link.get('href').split("/url?q=")[1].split("&sa=")[0]
                    new_links[new_link] = 0
                except:
                    continue
 
        else:
            # get words in title
            title_list = []
            try:
                title_list = soup.title.string.split()
            except:
                print("Could not parse title")
                continue

            # get words of meta tags
            tag_list = getMeta(soup)
            for title_word in title_list:
	            tag_list.add(title_word)

            # check relevance and rank URL according to score, return score
            score = 0
            score += checkRelevance(tag_list) 

            # only non-google search results will affect score
            # appends url to df if score > 0, can adjust criteria later
            if score >= 3:
                df.loc[df_count] = [start_page, score]
                df_count += 1
                df.sort_values("score")
                print df
                # TARGET CSV LOCATION on local machine
                export_csv = df.to_csv(r'/Users/joycesin/Documents/crawler/urls.csv', index = None, header=True)
                # only populates new links from seed urls above certain score
                new_links = getLinks(soup)

        # update overall links dict with new_links, avoiding duplicates
        new_links.update(links)
        links = new_links

# get a list of meta tags
def getMeta(soup):
    tag_list = set()

    tags = soup.find_all("meta", property="article:tag")
    tags.extend(soup.find_all("meta", itemprop="keywords"))
    tags.extend(soup.find_all("meta", itemprop="specialty"))
    tags.extend(soup.select("meta", name="keywords"))
    for tag in tags:
        tag_list.add(tag.get("content", None))
    return tag_list

# expects a list of words to check against list of keywords, gives a score
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

# returns dict with keys as urls and values as 0 -- unchecked
def getLinks(soup):
    new_links = {}

    for link in soup.findAll('a', attrs={'href': re.compile("^https://")}):
        # filter out twitter, other junk pages
        new_link = link.get('href')
        new_links[new_link] = 0
    return new_links

start()