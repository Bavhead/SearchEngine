# 15890 MS to build index from 55393 files

from bs4 import BeautifulSoup as bs
import lxml.html
import lxml.etree
from nltk.tokenize import word_tokenize as tokenize
from nltk.stem.porter import *
import pandas as pd

from pathlib import Path
import json
import csv
import heapq
import contextlib
from collections import defaultdict
import time
import sys


INDEX_FOLDER = Path("indexes")
MAX_INDEX_SIZE = 5 * 1024 * 1024 # 10MB

stemmer = PorterStemmer()
STRONG_TAG_WEIGHTS = {"title": 15,
                      "b":      2, 
                      "strong": 3, 
                      "h1":     10, 
                      "h2":     8, 
                      "h3":     6, 
                      "h4":     5, 
                      "h5":     4, 
                      "h6":     3}



def strongTokens(soupified: bs) -> dict[str, int]:
    strong_tokens = defaultdict(int)

    # for each strong tag, add its weight to the token's weight
    for imp_tag in STRONG_TAG_WEIGHTS.keys():
        for tag in soupified.find_all(imp_tag):
            tokens = tokenize(tag.get_text())
            stemmedTokens = [stemmer.stem(token) for token in tokens]
            for token in stemmedTokens:
                if len(token) > 1:
                    strong_tokens[token] += STRONG_TAG_WEIGHTS[imp_tag]

    return strong_tokens


def readJSON(path: str) -> tuple[str, dict[str, int]]:
    path = Path(path)
    url = None

    # extract url and content from json file
    with open(path, "r", encoding="utf-8", errors="ignore") as file:
        data = json.load(file)
        try:
            url = data["url"]
        except:
            return (None, None)
        
    # get webpage content
    soupified = None
    try:
        soupified = bs(data["content"], features="lxml")
    except:
        return (None, None)
    
    # tokenize and stem content
    all_tokens = tokenize(soupified.get_text())
    total_words = len(all_tokens)
    tokens = []
    for token in all_tokens:
        if len(token) > 1: 
            tokens.append(stemmer.stem(token[:15]))

    # count term frequencies
    tf = defaultdict(int)
    for token in tokens:
        tf[token] += 1

    # add strong tag weights to term frequencies
    for token, weight in strongTokens(soupified).items():
        tf[token] += weight

    # normalize term frequencies
    # for token in tf.keys():
    #     tf[token] /= total_words

    # print(f'READ the following URL: "{url}" from this document: "{path.name}"')
    return (url, tf)


def writeIndex(index, index_num: int) -> None:
    header = ["token", "postings"]
    file_loc = f"{INDEX_FOLDER}/index{index_num}.csv"
    with open(file_loc, "w", encoding="utf8", newline='') as indexfile:
        writer = csv.writer(indexfile)
        writer.writerow(header)
        for token, postings in index.items():
            localpost = ''
            for posting in postings:
                localpost += posting["id"] + ',' + str(posting['tf']) + ','
            writer.writerow([token, localpost[:-1]])

    df = pd.read_csv(file_loc)
    sorted_df = df.sort_values(by=["token"], ascending=True)
    sorted_df.to_csv(file_loc, index=False)
    

def createIndex(start) -> None:
    files = INDEX_FOLDER.glob("index*.csv")
    info = defaultdict(list)

    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            f.readline()    # skip header
            for line in f:
                line = line.split(',')
                token = line[0]
                if token.isalnum() and token[0] in start:
                    urls = line[1::2]
                    tfs = line[2::2]
                    for url, tf in zip(urls, tfs):
                        info[token].append({"id": url, "tf": tf})

    with open(f"{INDEX_FOLDER}/{start}.csv", "w", encoding="utf8", newline='') as indexfile:
        writer = csv.writer(indexfile)
        for token, postings in info.items():
            localpost = ''
            for posting in postings:
                localpost += posting["id"].replace('"', '') + ',' + str(posting['tf']).replace('"', '') + ','
            writer.writerow([token, localpost[:-1]])


def mergeIndexes() -> None:
    s1 = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'}

    for s in s1:
        createIndex(s)


def buildIndex(data_folder: str) -> None: 
    data_folder = Path(data_folder)
    print(f'---------- Building index from data in folder: "{data_folder.resolve()}" ----------')
    index = defaultdict(list)
    nindex = 0
    nfile = 0
    nfileskept = 0

    # for each json file in data folder, read its contents and add to index, then write index to file if exceeds MAX_INDEX_SIZE
    for path in data_folder.glob("**/*.json"):
        nfile += 1
        url, localTF = readJSON(path)
        if url is None or localTF is None:
            continue

        # add url and its term frequencies to local index
        nfileskept += 1
        for (token, freq) in localTF.items():
            index[token].append({"id": url, "tf": freq})

        # write index to file if it exceeds MAX_INDEX_SIZE
        if sys.getsizeof(index) > MAX_INDEX_SIZE:
            nindex += 1
            writeIndex(index, nindex)
            index.clear()    # reset local index


    # write remaining index to file
    if len(index) > 0:
        nindex += 1
        writeIndex(index, nindex)
        
    mergeIndexes()
    print(f'\n---------- Index has been built. ----------')
    print(f'Processed {nfileskept} files of {nfile} files found and wrote {nindex} index files.')
    print(f'Main index file is located at: "{INDEX_FOLDER.resolve()}\index.csv"')


if __name__ == "__main__":
    start_time = time.process_time()
    start_time2 = time.time()
    print()

    buildIndex(sys.argv[1])
 
    end_time2 = time.time()
    end_time = time.process_time()
    print()
    
    print()
    print(f"CPU Time elapsed to index data:  {end_time - start_time} seconds.")
    print(f"Wall Time elapsed to index data: {end_time2 - start_time2} seconds.")
    