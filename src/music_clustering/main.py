import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

# Chargement des données
def load_data():
    musics = pd.read_csv("data/data.csv") # dataset with musics
    clusters = pd.read_csv("data/cluster_characteristics.csv") # dataset with clusters and their characteristics
    return musics, clusters

# Fonction pour standardiser les données
def standardize_data(data, columns_to_standardize):
    """
    Standardise les colonnes spécifiées du DataFrame en utilisant un StandardScaler.
    
    Args:
        data (pd.DataFrame): Le DataFrame à standardiser.
        columns_to_standardize (list): Les colonnes à standardiser.
    
    Returns:
        pd.DataFrame: Le DataFrame avec les colonnes standardisées.
    """
    scaler = StandardScaler()
    # Standardiser les colonnes spécifiées
    data[columns_to_standardize] = scaler.fit_transform(data[columns_to_standardize])
    return data

# Association des musiques à un cluster suivant leurs caractéristiques
def data_clustering(musics, clusters):
    # Colonnes à comparer
    columns_to_compare = ['mode', 'acousticness', 'danceability', 'duration_ms', 'energy',
                          'instrumentalness', 'liveness', 'loudness', 'speechiness',
                          'tempo', 'valence', 'popularity', 'key']
    
    # Standardisation des données
    musics = standardize_data(musics, columns_to_compare)
    clusters = standardize_data(clusters, columns_to_compare)
    
    # Création d'une colonne cluster dans le dataset musics
    musics['cluster'] = -1
    
    # Conversion des données en numpy arrays pour plus d'efficacité
    musics_data = musics[columns_to_compare].values
    clusters_data = clusters[columns_to_compare].values
    
    # Calcul des distances entre chaque musique et chaque cluster
    distances = np.linalg.norm(musics_data[:, np.newaxis] - clusters_data, axis=2)
    
    # Trouver l'indice du cluster le plus proche pour chaque musique
    cluster_ids = clusters['cluster'].values
    closest_clusters = np.argmin(distances, axis=1)
    
    # Assigner les clusters aux musiques
    musics['cluster'] = cluster_ids[closest_clusters]
        
    # On enregistre le dataset musics avec la colonne cluster
    musics.to_csv("data/data_w_clusters.csv", index=False)
    
    return musics

def main():
    musics, clusters = load_data()
    musics = data_clustering(musics, clusters)

main()