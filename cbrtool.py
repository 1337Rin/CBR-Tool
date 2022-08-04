import re
import requests
from bs4 import BeautifulSoup
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", help="url of host")
parser.add_argument("-w", "--wordlist", help="wordlist to use")

word_args = ["-w", "--wordlist", "--w", "-wordlist"]
url_args = ["-u", "--u", "-url", "--url"]

args = parser.parse_args()
url = args.url
file = args.wordlist

if not len(sys.argv) > 1:
    parser.print_help(sys.stderr)
    exit()

for x in word_args:
    if x in sys.argv:
        word_args = True
if word_args != True:
    word_args = False

for x in url_args:
    if x in sys.argv:
        url_args = True
if url_args != True:
    url_args = False

if url_args == True and word_args == True:
    mode = ("brute")
    try:
        filename = (file)
        values = open(file, "r")
    except FileNotFoundError:
        print(f"[-] FileNotFoundError: {filename}\n")
        exit()
    with open(filename) as file:
        length = len((file.readline()))
elif url_args == True and word_args == False:
    mode = ("crawl")

print(f"[+] using {mode} mode")


lvl = 0
count = 0

def exceptions(url):
    try:
        requests.get(url)
    except requests.ConnectionError:
        print("[-] ConnectionError")
        print("[-] Exiting...")
        exit()
    except requests.Timeout:
        print("[-] TimeoutError")
        print("[-] Exiting...")
        exit()
    except requests.RequestException:
        print("[-] RequestException")
        print("[-] Exiting...")
        exit()

def clean_list(clean):
    clean[:] = clean = list(dict.fromkeys(clean))

def main_crawl(url):
    global emails
    global links
    global urls
    global directorys
    global lvl
    if lvl == 0:
        emails = []
        links = []
        directorys = []
        urls = []
        lvl = lvl + 1
    elif lvl != 0:
        lvl = lvl + 1
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')

        if href == "#":
            pass
        elif href == None:
            pass
        elif re.search("mailto*", href) != None:
            emails.append(href)
            clean_list(emails)
        elif re.search("http*", href) != None:
            links.append(href)
            clean_list(links)
        else:
            slash = re.search("^/", href)
            if slash:
                directorys.append(href)
                clean_list(directorys)
            else:
                href = "/" + href
                directorys.append(href)
                clean_list(directorys)

if mode == "crawl":
    exceptions(url)
    main_crawl(url)

    def decend(directorys=directorys,count=count):
        length = len(directorys[0])
        for x in directorys:
            test = f"{url}{x}"
            count = int(count) + 1
            print(f'{test: <{length}}', end="\r")
            length=(len(test))
            clean_list(directorys)
            main_crawl(test)
        print("\n[+] finished crawl")
    decend()

    def crawl_out(links=links, directorys=directorys, emails=emails):
        lists = [links, directorys, emails]
        for x in lists:
            if x == links:
                print("")
                print("[+] links")
                n = len(links)
                print(f"[+] count: {n}")
            elif x == directorys:
                print("")
                print("[+] directorys")
                n = len(directorys)
                print(f"[+] count: {n}")
            elif x == emails:
                print("")
                print("[+] emails")
                n = len(emails)
                print(f"[+] count: {n}")
            for y in x:
                print(y)

    crawl_out()


elif mode == "brute":
    exceptions(url)
    if url[-1] != '/':
        url = url + '/'
    for i in values:
        x = i.replace('\n', '')
        y = (url + x)
        z = requests.get(y)
        if z.status_code != 404:
            print(f"[{z.status_code}] {z.url}")
        else:
            print(f'{y: <{length}}', end="\r")
            length=len(y)

    print("\n")