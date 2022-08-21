# CBR-Tool
Simple website crawler and directory brute forcer for website enumeration. Creates output files in easy to read json using the sites domain name and enumeration mode used, for example `127.0.0.1.brute.json` and `127.0.0.1.crawl.json`. `brute.json` tracks whats wordlists have been used and in what percentage in addition to the enumerated directorys. `crawl.json` stores all crawled href tags and sorts them into appropriate lists.

## Usage
```shell
usage: cbrtool.py.1 [-h] [-u URL] [-w WORDLIST]

CBRTool is a directory bruteforcer and website crawling tool that utilizes
progress tracking in clean and easy to read json output

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     url of host
  -w WORDLIST, --wordlist WORDLIST
                        wordlist to use
```

