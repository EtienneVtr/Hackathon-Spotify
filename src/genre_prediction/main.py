import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

# Chargement des données
def load_data():
    musics = pd.read_csv("data/data.csv") # dataset with musics
    clusters = pd.read_csv("data/cluster_characteristics.csv") # dataset with clusters and their characteristics
    genres = pd.read_csv("data/genres_clusters.csv") # dataset with genres and their clusters
    artists = pd.read_csv("data/data_w_genres.csv") # dataset with artists and their genres
    return musics, clusters, genres, artists

# Préparation des données
def data_preparation(musics):
    # On ne garde que mode,acousticness,danceability,duration_ms,energy,instrumentalness,liveness,loudness,speechiness,tempo,valence,popularity,key
    X = musics[['mode','acousticness','danceability','duration_ms','energy',
                'instrumentalness','liveness','loudness','speechiness','tempo',
                'valence','popularity','key']]
    
    # On ajoute une colonne genre au dataset
    musics['genre'] = -1
    y = musics['genre']

def main():
    musics, clusters, genres, artists = load_data()

main()