import re
import requests
from bs4 import BeautifulSoup
import argparse
import sys
import json
from urllib.parse import urlparse
import os


parser = argparse.ArgumentParser(
    description="Crawler/brute forcing tool",
    epilog="Contributions are welcome: https://github.com/1337Rin/CBR-Tool")
parser.add_argument("-v", "--verbose", action="store_true", help="enable talkative mode")
parser.add_argument("-q", "--quiet", action="store_true", help="don't print additional information")
parser.add_argument("-w", "--wordlist", help="wordlist to use")
parser.add_argument("url", metavar="URL", help="url of host")

args = parser.parse_args()
url = args.url
wordlist = args.wordlist
domain = urlparse(url).netloc

# if user is a poopyhead, disable both flags
if args.verbose and args.quiet:
    args.verbose = False
    args.quiet = False

word_args = (wordlist!=None)

# determine mode
def mode_deter():
    global mode
    if word_args:
        mode = ("brute")
        output_file = f"{domain}.brute.json"
        output_exists = os.path.exists(output_file)

        if output_exists:
            string = open(f"{domain}.brute.json", "r")
            string = string.read()

            if args.wordlist in string:
                percent = string.find("%")
                percent = percent - 2
                percent = int(string[percent:string.find("%")])

                if percent == 00:
                    yesno = input(f"{args.wordlist} has already been completed are you sure you want to use it[y/N]: ")
                    yesno = yesno.lower()
                    yesno = yesno.strip()
                    yesno = yesno.strip("abcdefghijklmopqrstuvwxz")
                    
                    if yesno == "n":
                        exit()
                    elif yesno == "y":
                        pass
                    else:
                        print("invalid input")
                        exit()
                        
                elif percent < 100:
                    if not args.quiet: print("wordlist not completed")

    else:
        mode = ("crawl")
        output_file = f"{domain}.crawl.json"
        output_exists = os.path.exists(output_file)

        if output_exists:
            string = open(f"{domain}.crawl.json", "r")
            string = string.read()

        if "crawl_finished = 1" in string:
            yesno = input("This domain has already been crawled to completion are you sure you want to crawl it again[y/N]: ")
            yesno = yesno.lower()
            yesno = yesno.strip()
            yesno = yesno.strip("abcdefghijklmopqrstuvwxz")

            if yesno == "n":
                exit()
            elif yesno == "y":
                pass
            else:
                print("invalid input")
                exit()

    if not args.quiet: print(f"[+] using {mode} mode")

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
    global directories
    global lvl

    if lvl == 0:
        emails = []
        links = []
        directories = []
        urls = []
        place_holder = []
        lvl = lvl + 1

    elif lvl != 0:
        lvl = lvl + 1
    
    try:
        reqs = requests.get(url)
    except requests.ConnectionError:
        print("\n")
        print("[-] Lost Connection to Host")
        print("[-] Exiting...")
        output_file = open(f"{domain}.crawl.json", "a")
        output_file.write("crawl_finished = 0\n\n")
        crawl_out(links, directories, emails)
        exit()
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')

        if href == "#":
            pass
        elif href == None:
            pass

        elif "mailto" in href:
            emails.append(href)
            clean_list(emails)
        elif "@" in href:
            emails.append(href)
            clean_list(emails)

        elif re.search("http*", href) != None:
            check_href = urlparse(href).netloc
            if check_href == domain:
                directories.append(href)
                clean_list(directories)
            elif check_href != domain:
                links.append(href)
                clean_list(links)
        else:
            slash = re.search("^/", href)
            if slash:
                directories.append(href)
                clean_list(directories)
            else:
                href = "/" + href
                directories.append(href)
                clean_list(directories)

    directories_json = json.dumps(directories, indent = 6)
    emails_json = json.dumps(emails, indent = 6)
    links_json = json.dumps(links, indent = 6)

    output_file = open(f"{domain}.crawl.json", "w")

    output_file.write(f"directories = {directories_json}\n")
    output_file.write("\n")
    output_file.write(f"emails = {emails_json}\n")
    output_file.write("\n")
    output_file.write(f"links = {links_json}\n")
    output_file.write("\n")

# crawl discovered web pages
def decend(directories):

    length = len(directories[0])
    for href in directories:

        if domain in href:
            new_url = f"{href}"

            print(f'{new_url: <{length}}', end="\r")
            clean_list(directories)
            main_crawl(new_url)

            length=(len(new_url))

        else:
            new_url = f"{url}{href}"

            print(f'{new_url: <{length}}', end="\r")
            clean_list(directories)
            main_crawl(new_url)

            length=(len(new_url))
    output_file = open(f"{domain}.crawl.json", "a")
    output_file.write("crawl_finished = 1\n\n")
    if not args.quiet: print("\n[+] finished crawl")

# print crawled output
def crawl_out(links, directories, emails):
    if not args.quiet:
        n = len(links)
        print( "[+] links")
        print(f"[+] count: {n}")
    for x in links:
        print(x)

    print()
    if not args.quiet:
        n = len(directories)
        print( "[+] directories")
        print(f"[+] count: {n}")
    for x in directories:
        print(x)

    print()
    if not args.quiet:
        n = len(emails)
        print( "[+] emails")
        print(f"[+] count: {n}")
    for x in emails:
        print(x)

# brute force mode main function
def main_brute(length, words, url):
    brute_forced_dirs = []
    count = 0
    for directory in words:
        directory = directory.replace('\n', '')
        test_url = (url + directory)
        req_url = requests.get(test_url)
        count = count + 1

        if req_url.status_code != 404:
            brute_forced_dirs.append(test_url)
            print(f"[{req_url.status_code}] {req_url.url}")

        else:
            print(f'{test_url: <{length}}', end="\r")
            length=len(test_url)

    print("\n")

    brute_forced_dirs = json.dumps(brute_forced_dirs, indent = 6)
    output_file = open(f"{domain}.brute.json", "a")
    line_sum = sum(1 for line in open(args.wordlist))
    decimal = count/line_sum
    decimal = int(decimal * 100)
    output_file.write(f"wordlist = {args.wordlist} {decimal}% Completed\nbrute_forced_dirs = {brute_forced_dirs}\n")
    output_file.write("\n")

# edit user supplied url to avoid errors
def url_fix(mode):
    global url
    match mode:
        case "crawl":
            last_char = (url[-1])
            if last_char == "/":
                url = (url[0:-1])
        case "brute":
            if url[-1] != '/':
                url += '/'


mode_deter()
match mode:
    case "crawl":
    
        lvl = 0
    
        url_fix(mode)
        exceptions(url, mode)
        main_crawl(url)
        decend(directories)
        crawl_out(links, directories, emails)
    
    case "brute":
        url_fix(mode)
        exceptions(url, mode)
    
        with open(wordlist) as wordlist:
            length = len((wordlist.readline()))
    
        main_brute(length, words, url)
    
exit()
