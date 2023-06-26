To run the program, first install the depenencies.
To do so, run the following lines of code one at a time in the repository:

pip3 install bs4
pip3 install lxml
pip3 install pandas
pip3 install nltk

Then, open up a terminal-level python interpreter.
Run the following commands:

import nltk
nltk.download("punkt")

This is necessary for the tokenizer and stemmer to funtion as intended.

Now, we can run the program
Use the following command from inside the SearchEngine directory to build the index:
python3 indexer.py <path to dataset> 

The indexes will be created in SearchEngine/indexes/*.csv
All indexes with a number attatched can be ignored, only the letter to letter ones matter.

!YAY! Now we can run queries.

To run queries, use the following command from inside the SearchEngine directory:

python3 modified_search_gui.py

Then, enter your query into the terminal and hit enter
A list of the top 5 results will be presented along with the time it took to run the query.
Enter " :quit: " to exit the program.