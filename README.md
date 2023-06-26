# SearchEngine


## Installation
First, ensure [Python](https://www.python.org/downloads/) (version 3.8 and greater) and [pip](https://pip.pypa.io/en/stable/) are installed.

Then, install the following dependencies using pip. In the terminal, run each of the following commands individually.
```
pip3 install bs4
pip3 install lxml
pip3 install pandas
pip3 install nltk
```

Then, open up a terminal-level Python interpreter. (i.e. Python Idle)
Run the following commands:

```
import nltk
nltk.download("punkt")
```

This is necessary for the tokenizer and stemmer to function as intended.

## Usage
Use the following command from inside the SearchEngine directory to build the index:
`python3 indexer.py <path-to-dataset>`

Depending on the size of the dataset, this can take a while. The current average speed is 1GB/7min.
The indexes will be created in `SearchEngine/indexes/*.csv`
All indexes with a number attached can be safely deleted after completion of the program.

Yay! Now we can run queries.

To run queries, use the following command from inside the SearchEngine directory:

`python3 modified_search_gui.py`

Then, enter your query into the terminal and hit enter
A list of the top 5 results will be presented along with the time it took to run the query.
Type `:quit:` to exit the program.
