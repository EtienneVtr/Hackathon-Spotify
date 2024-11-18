import sys
import os

# Ajoute le répertoire 'src' au chemin de recherche des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from audio_search.main import get_youtube_url, API_KEY

import pandas as pd

def test_get_youtube_url():
    # Import the CSV in "./data/data.csv" 
    df = pd.read_csv("./data/data.csv")
    
    # Only keep the row "name"
    df = df["name"]
    
    # Get the numer of rows
    n_rows = len(df)
    
    # For each name, try to get the URL
    entries_found = 0
    counter = 0
    for name in df:
        url = get_youtube_url(name, API_KEY)
        if url:
            entries_found += 1
        counter += 1
        if counter % 10 == 0:
            print(f"Progress: {counter}/{n_rows}")
            
    # Print the number of entries found
    print(f"Entries found: {entries_found}/{n_rows}")

test_get_youtube_url()