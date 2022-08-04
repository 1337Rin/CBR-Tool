import re
import requests
from bs4 import BeautifulSoup
import argparse
import sys

# cli arguments
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", help="url of host")
parser.add_argument("-w", "--wordlist", help="wordlist to use")

args = parser.parse_args()
url = args.url
wordlist = args.wordlist


# check supplied arguments
word_args = ["-w", "--wordlist", "--w", "-wordlist"]
url_args = ["-u", "--u", "-url", "--url"]

if not len(sys.argv) > 1:
    parser.print_help(sys.stderr)
    exit()

for param in word_args:
    if param in sys.argv:
        word_args = True

if word_args != True:
    word_args = False

for param in url_args:
    if param in sys.argv:
        url_args = True

if url_args != True:
    url_args = False


# determine mode
if url_args == True and word_args == True:
    mode = ("brute")

elif url_args == True and word_args == False:
    mode = ("crawl")

print(f"[+] using {mode} mode")


# error handling
def exceptions(url, mode):
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
    if mode == ("brute"):
        try:
            global words
            words = open(wordlist, "r")
        except FileNotFoundError:
            print(f"[-] FileNotFoundError: {wordlist}\n")
            exit()


# remove duplicates from crawled directory list
def clean_list(clean):
    clean[:] = clean = list(dict.fromkeys(clean))

# parse all hrefs from page and add to list
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

# crawl discovered web pages
def decend(directorys, count):

    length = len(directorys[0])

    for href in directorys:

        new_url = f"{url}{href}"
        count = int(count) + 1

        print(f'{new_url: <{length}}', end="\r")
        clean_list(directorys)
        main_crawl(new_url)

        length=(len(new_url))

    print("\n[+] finished crawl")

# print crawled output
def crawl_out(links, directorys, emails):
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

# brute force mode main function
def main_brute(length, words, url):
    for directory in words:

        directory = directory.replace('\n', '')
        test_url = (url + directory)
        req_url = requests.get(test_url)

        if req_url.status_code != 404:
            print(f"[{req_url.status_code}] {req_url.url}")
        else:
            print(f'{test_url: <{length}}', end="\r")
            length=len(test_url)

    print("\n")


if mode == "crawl":

    lvl = 0
    count = 0

    exceptions(url, mode)
    main_crawl(url)
    decend(directorys,count)
    crawl_out(links, directorys, emails)


elif mode == "brute":

    exceptions(url, mode)

    with open(wordlist) as wordlist:
        length = len((wordlist.readline()))

    if url[-1] != '/':
        url = url + '/'

    main_brute(length, words, url)
    
exit()
