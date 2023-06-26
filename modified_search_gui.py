from flask import Flask, request, render_template
import math
from collections import Counter, defaultdict
import time
import heapq
from pathlib import Path
from nltk.tokenize import word_tokenize as tokenize
from nltk.stem.porter import * 

INDEX_LOCATION = Path('indexes')
TOTAL_FILES = 55393
app = Flask(__name__)

# Tokenize and stem the query
def preprocess_text(text):
    stemmer = PorterStemmer()
    all_tokens = tokenize(text)
    tokens = []
    for token in all_tokens:
        if len(token) > 1: # and checkalnum(token):
            tokens.append(stemmer.stem(token[:15]))

    return tokens


def get_postings(word):
    index_file = f'{INDEX_LOCATION}/{word[0]}.csv'
    with open(index_file, 'r') as f:
        for line in f:
            starter = word + ','
            if line.startswith(starter):                
                line = line.split(',')
                line = line[1:]
                urls = line[::2]
                tfs = line[1::2]
                df = TOTAL_FILES / len(urls)
                postings= {}
                for i in range(len(urls)):
                    postings[urls[i]] = tfidf(tfs[i], df)
                return postings

            else:
                continue
    return None
                

def tfidf(tf, df):
    try:
        tr = (1 + math.log(float(tf))) * math.log(TOTAL_FILES / (float(df)+1))
        return tr
    except:
        return -1 


def compute_query_vector(query_tokens):
    token_postings = {}
    for token in query_tokens:
        token_postings[token] = get_postings(token)

    relevant_docs = set()
    
    try:
        first = True
        for token in query_tokens:
            if first:
                relevant_docs = set(token_postings[token].keys())
                first = False
            else:
                relevant_docs = relevant_docs & set(token_postings[token].keys())
    except:
        return []

    
    relevant = defaultdict(float)
    for doc in relevant_docs:
        for token in query_tokens:
            if doc in token_postings[token]:
                relevant[doc] += token_postings[token][doc]
                
    ss = sorted([(score, doc) for doc, score in relevant.items()], reverse=True)
    ss = ss[:5]
    return [doc for score, doc in ss]

    # return relevant_docs


# Change the inverted index data structure
# The key will be the token, the value will be a list of tuples, where each tuple contains a doc_id and the tf-idf score of that document for the token

# def compute_document_scores(query_vector, query_length, inverted_index):
#     document_scores = defaultdict(float)
#     for token, query_tf_idf in query_vector.items():
#         for doc_id, doc_tf_idf in inverted_index.get(token, []):
#             document_scores[doc_id] += query_tf_idf * doc_tf_idf

#     for doc_id, score in document_scores.items():
#         score /= query_length
#         document_scores[doc_id] = score

#     return document_scores

def search(query):
    query_tokens = preprocess_text(query)
    urls = compute_query_vector(query_tokens)
    print("Look into these urls: ")
    if len(urls) == 0:
        print("No relevant results found")
        return []
    for url in urls:
        print(url.replace('"', ''))
    # print(urls)
    return urls
    # query_vector, query_length = compute_query_vector(query_tokens, inverted_index)
    # document_scores = compute_document_scores(query_vector, query_length, inverted_index)
    # # Use a heap to keep the top results
    # top_docs = heapq.nlargest(10, document_scores.items(), key=lambda x: x[1])
    # return [doc_id for doc_id, _ in top_docs]

# @app.route('/', methods=['GET', 'POST'])
# def home():
#     if request.method == 'POST':
#         query = request.form['query']

#         # time each search
#         start_time = time.process_time()
#         results = search(query)
#         end_time = time.process_time()
#         execution_time = end_time - start_time
#         print(f"Search execution time: {execution_time} seconds")

#         return render_template('results.html', results=results, query=query)
#     return render_template('index.html')


if __name__ == '__main__':
    while True:
        inp = input("\nSearch: ")
        if inp.strip() == ':quit:':
            break
        start_time = time.process_time()
        search(inp)
        end_time = time.process_time()
        print(f'Execution time for query: {end_time - start_time} seconds')

    # app.run()

