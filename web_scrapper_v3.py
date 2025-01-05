import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from tqdm import tqdm
import time
from collections import Counter
import pandas as pd
import streamlit as st
from streamlit_lottie import st_lottie
import sys
import json

def load_lottiefile(filepath: str):
    with open(filepath, 'r') as f:
        return json.load(f)

# Load the Lottie animation file
# lottie_coding = load_lottiefile('Animation_loading.json')

# Custom CSS for the Lottie container
css = """
<style>
    .custom-lottie-container {
        width: 100%; /* Full width of the container */
        height: 300px; /* Adjust height as needed */
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 20px; /* Space above the animation */
    }
</style>
"""

# Inject the CSS
st.markdown(css, unsafe_allow_html=True)
# st.title("SITE SEEKER")
# Larger Text Element
st.markdown('<h1 style="font-size:64px;color:hsl(120, 100%, 50%);"> >> SITE SEEKER APP <<</h1>', unsafe_allow_html=True)
# Form section
with st.form(key='my_form'):
    title = st.text_input(label='Search Here')
    submit_button = st.form_submit_button(label='Submit')

# Display Lottie animation if the submit button is clicked
if submit_button:
    # st.markdown('<div class="custom-lottie-container">', unsafe_allow_html=True)
    # st_lottie(lottie_coding, width=500, loop=True)  # Adjust width as needed
    # st.markdown('</div>', unsafe_allow_html=True)
    st.write(f"You searched for: {title}")

st.set_option('deprecation.showPyplotGlobalUse', False)

search_text = [title]
search_query = search_text
st.write(search_query)                   

split_elements = [[item.strip() for item in string.split(',')] for string in search_query]
search_query = split_elements[0]
sites_to_remove = ['www.youtube.com','amazon.com','amazon.in','Flipkart.com','support.google.com']
final_sites=[]
for x in sites_to_remove:
    ss='-site:'+str(x)
    final_sites.append(ss)
concatenated_text = ' '.join(final_sites)
search_query = ' or '.join(search_query)

print(search_query + " " + concatenated_text)

SEARCH_QUERY = search_query
RESULTS_PER_PAGE = 10  # Number of results per page
NUM_PAGES = 1  # Number of pages to scrape
BASE_URL = "https://www.google.com/search"

url_lists=[]
for page in tqdm(range(NUM_PAGES)):
    params = {
        'q': SEARCH_QUERY,
        'start': page * RESULTS_PER_PAGE
    }
    
    response = requests.get(BASE_URL, params=params)
    time.sleep(7)
    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href.startswith("/url?q="):
            url_lists.append(href[7:].split('&')[0])    

len(url_lists)

import re

actual_list = url_lists
removal_substrings = ['support.google.com','accounts.google.com','/search%3Fq','youtube.com']

removal_patterns = [re.compile(re.escape(substring)) for substring in removal_substrings]

def should_remove(s):
    return any(pattern.search(s) for pattern in removal_patterns)

filtered_list = [s for s in actual_list if not should_remove(s)]
print(len(filtered_list))

len(filtered_list)

filtered_list

url_list = filtered_list
headings_list = []
ex_dict={}
for url in url_list:
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

        headings_text = [heading.get_text() for heading in headings]
        headings_list.append(headings_text)
        ex_dict.update({url: headings_text})
        print(f"Headings extracted from {url}: {headings_text}")
    except requests.exceptions.Timeout:
        print(f"Request for {url}: {'20 seconds'}")
    except requests.exceptions.RequestException as e:
        print(f"Error requesting {url}: {e}")

from collections import Counter

def filter_number_listings(text_lines):
    filtered_lines = []
    if re.match(r'^\d+\.\s', text_lines):
        filtered_lines.append(text_lines)
    return filtered_lines

final_output=[]
for sub_lists in headings_list:
    for suber in sub_lists:
        x=filter_number_listings(suber)
        final_output.append(x)

filtered_nested_lists = [sublist for sublist in final_output if sublist]

flat_list = [item for sublist in filtered_nested_lists for item in sublist]

def clean_text_(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    word = '\xa0'
    text = text.lower()
    text = re.sub(re.escape(word), '', text)
    text = re.sub(r'\d+\s', '', text)
    
    return text

visual = []
for words in flat_list:
    texts=clean_text_(words)
    visual.append(texts)

text_lines = visual  

line_counter = Counter(text_lines)
sorted_lines_counts = sorted(line_counter.items(), key=lambda x: x[1], reverse=True)

# Limit the number of lines to consider
TOP_N_LINES = 10  # Change this value to your desired limit

sorted_lines_counts = sorted_lines_counts[:TOP_N_LINES]
lines, counts = zip(*sorted_lines_counts)

plt.figure(figsize=(10, 40))
plt.barh(lines, counts, color='skyblue')
plt.xlabel('Counts')
plt.ylabel('Lines of Text')
plt.title('Most Repeated Lines of Text')
plt.gca().invert_yaxis()
for i, count in enumerate(counts):
    plt.text(count + 0.2, i, str(count), va='center', color='black')
plt.show()
st.pyplot(plt.show())
