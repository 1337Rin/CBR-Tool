import re
import requests
from bs4 import BeautifulSoup
import argparse
import sys
import json
from urllib.parse import urlparse
import os

# cli arguments
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", help="url of host")
parser.add_argument("-w", "--wordlist", help="wordlist to use")

args = parser.parse_args()
url = args.url
wordlist = args.wordlist
domain = urlparse(url).netloc


# check supplied arguments
word_args = ["-w", "--wordlist", "--w", "-wordlist"]
url_args = ["-u", "--u", "-url", "--url"]



# determine givin flags
def param_parse():
    global word_args
    global url_args

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
def mode_deter():
    global mode
    if url_args == True and word_args == True:
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
                    print("wordlist not completed")


    elif url_args == True and word_args == False:
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



    print(f"[+] using {mode} mode")

param_parse()
mode_deter()

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
        crawl_out(links, directorys, emails)
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
                directorys.append(href)
                clean_list(directorys)
            elif check_href != domain:
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

    directorys_json = json.dumps(directorys, indent = 6)
    emails_json = json.dumps(emails, indent = 6)
    links_json = json.dumps(links, indent = 6)

    output_file = open(f"{domain}.crawl.json", "w")

    output_file.write(f"directorys = {directorys_json}\n")
    output_file.write("\n")
    output_file.write(f"emails = {emails_json}\n")
    output_file.write("\n")
    output_file.write(f"links = {links_json}\n")
    output_file.write("\n")

# crawl discovered web pages
def decend(directorys):

    length = len(directorys[0])
    for href in directorys:

        if domain in href:
            new_url = f"{href}"

            print(f'{new_url: <{length}}', end="\r")
            clean_list(directorys)
            main_crawl(new_url)

            length=(len(new_url))

        else:
            new_url = f"{url}{href}"

            print(f'{new_url: <{length}}', end="\r")
            clean_list(directorys)
            main_crawl(new_url)

            length=(len(new_url))

    output_file = open(f"{domain}.crawl.json", "a")
    output_file.write("crawl_finished = 1\n\n")
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
    if mode == "crawl":
        last_char = (url[-1])
        if last_char == "/":
            url = (url[0:-1])
    elif mode == "brute":
        if url[-1] != '/':
            url = url + '/'

if mode == "crawl":

    lvl = 0

    url_fix(mode)
    exceptions(url, mode)
    main_crawl(url)
    decend(directorys)
    crawl_out(links, directorys, emails)

elif mode == "brute":
    url_fix(mode)
    exceptions(url, mode)

    with open(wordlist) as wordlist:
        length = len((wordlist.readline()))

    main_brute(length, words, url)
    
exit()
