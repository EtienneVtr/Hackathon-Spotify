import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import time

# Chargement des données
def load_data():
    musics = pd.read_csv("data/data.csv") # dataset with musics
    clusters = pd.read_csv("data/cluster_characteristics.csv") # dataset with clusters and their characteristics
    genres = pd.read_csv("data/genres_clusters.csv") # dataset with genres and their clusters
    artists = pd.read_csv("data/data_w_genres.csv") # dataset with artists and their genres
    return musics, clusters, genres, artists

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

import time
import numpy as np

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
    
    # Initialisation du compteur et du temps de départ
    start_time = time.time()
    last_update_time = start_time  # Temps pour actualiser la vitesse
    
    # Pour chaque musique, on cherche le cluster qui lui correspond
    for i in range(len(musics)):
        # On récupère les caractéristiques de la musique i
        music = musics.loc[i, columns_to_compare]
        
        # On initialise la distance minimale à l'infini
        min_dist = np.inf
        
        # On parcourt les clusters pour trouver le cluster qui minimise la distance
        for j in range(len(clusters)):
            cluster = clusters.loc[j, columns_to_compare]
            dist = np.linalg.norm(music - cluster)
            if dist < min_dist:
                min_dist = dist
                cluster_id = clusters.loc[j, 'cluster']
                
        # On associe la musique i au cluster cluster_id
        musics.loc[i, 'cluster'] = cluster_id
        
        # Calcul du temps écoulé
        elapsed_time = time.time() - start_time
        
        # Calcul du nombre de musiques traitées par seconde
        musiques_par_seconde = (i + 1) / elapsed_time
        
        # Actualisation de la vitesse toutes les secondes
        if time.time() - last_update_time >= 1:
            # Calcul du temps restant
            time_remaining_seconds = (len(musics) - i - 1) / musiques_par_seconde
            
            # Conversion en heures, minutes et secondes
            hours = int(time_remaining_seconds // 3600)
            minutes = int((time_remaining_seconds % 3600) // 60)
            seconds = int(time_remaining_seconds % 60)
            
            # Affichage de la progression, de la vitesse et du temps restant
            print(f"\rProgression : {i}/{len(musics)} | {musiques_par_seconde:.2f} musiques/seconde | Temps restant : {hours:02}:{minutes:02}:{seconds:02}", end='', flush=True)
            
            # Mise à jour du temps de dernière actualisation
            last_update_time = time.time()
        
    # On enregistre le dataset musics avec la colonne cluster
    musics.to_csv("data/data_w_clusters.csv", index=False)
    
    # Affiche une ligne vide pour terminer proprement l'affichage
    print()
    
    return musics


def main():
    musics, clusters, genres, artists = load_data()
    musics = data_clustering(musics, clusters)

main()