# CE FICHIER EST DESTINE A CONTENIR LES FONCTIONS UTILISEES DANS L'APPLICATION WEB

# Importation des librairies
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances

# FONCTIONS

# Fonction pour donner une liste de recommandations à partir d'une musique
def get_recommandations_from_music(id_music, n_recommandations):
    # Chargement des données
    data = pd.read_csv('data/data_w_clusters.csv')

    # On récupère le cluster de la musique
    cluster = data[data['id'] == id_music]['cluster'].values[0]
    
    # On récupère les musiques du même cluster
    musics = data[data['cluster'] == cluster]
    
    # On cherche les n_recommandations musiques les plus proches
    # On calcule la distance entre les musiques à l'aide des attributs 'danceability', 'energy', 'loudness', 'speechiness', 'acousticness',
    #                                                                  'instrumentalness', 'liveness', 'valence', 'tempo'
    # On utilise la distance euclidienne
    
    # Extraire les colonnes pertinentes pour le calcul des distances
    feature_columns = ['danceability', 'energy', 'loudness', 'speechiness', 
                       'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
    
    # Trouver les attributs de la musique cible
    target_music_features = data.loc[data['id'] == id_music, feature_columns].values
    
    # Filtrer les musiques autres que celle ciblée
    other_musics = musics[musics['id'] != id_music]
    
    # Calculer les distances euclidiennes en masse
    other_features = other_musics[feature_columns].values
    distances = euclidean_distances(target_music_features, other_features).flatten()
    
    # Associer les distances aux IDs
    recommandations = list(zip(other_musics['id'].values, distances))
    
    # Trier les recommandations par distance
    recommandations.sort(key=lambda x: x[1])
    recommandations = recommandations[:min(n_recommandations, len(recommandations))]
    
    # On retourne les id des musiques recommandées
    return [x[0] for x in recommandations]

# Fonction pour donner une liste de recommandations à partir d'une playlist
def get_recommandations_from_playlist(list_id_music, n_recommandations):
    # Chargement des données
    data = pd.read_csv('data/data_w_clusters.csv')
    
    # On récupère les clusters des musiques de la playlist
    clusters = data[data['id'].isin(list_id_music)]['cluster'].values
    
    # On calcule le "centre" des musiques dans leur cluster respectif à l'aide des attributs 'danceability', 'energy', 'loudness', 'speechiness', 'acousticness',
    #                                                                  'instrumentalness', 'liveness', 'valence', 'tempo'
    centers = {}
    feature_columns = ['danceability', 'energy', 'loudness', 'speechiness', 
                        'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
    for cluster in clusters:
        musics = data[(data['cluster'] == cluster) & (data['id'].isin(list_id_music))]
        center = musics[feature_columns].mean()
        centers[cluster] = center
        
    # On récupère les musiques de chaque cluster dans des tableaux différents
    musics = {}
    for cluster in clusters:
        musics[cluster] = data[(data['cluster'] == cluster) & (~data['id'].isin(list_id_music))]
        
    # On cherche les n_recommandations musiques les plus proches
    # Pour cela, on commence par calculer la distance entre les musiques des clusters par rapport aux centres calculés
    # On calcule la distance entre les musiques à l'aide des attributs 'danceability', 'energy', 'loudness', 'speechiness', 'acousticness',
    #                                                                  'instrumentalness', 'liveness', 'valence', 'tempo'
    # On utilise la distance euclidienne
    
    # On calcule les distances euclidiennes et les associe aux IDs
    recommandations = []
    for cluster in clusters:
        # Features du centre
        center_features = centers[cluster].values.reshape(1, -1)
        
        # Musiques dans le cluster
        other_musics = musics[cluster]
        other_features = other_musics[feature_columns].values
        
        # Distances euclidiennes
        distances = euclidean_distances(center_features, other_features).flatten()
        
        # Associer ID et distances
        cluster_recommandations = list(zip(other_musics['id'].values, distances))
        
        # Trier par distance (plus proche en premier) et garder les `n_recommandations` meilleures
        cluster_recommandations = sorted(cluster_recommandations, key=lambda x: x[1])[:min(n_recommandations, len(cluster_recommandations))]
        recommandations.extend(cluster_recommandations)
    
    # Retourner les recommandations triées par distance globale et garder les `n_recommandations` meilleures
    recommandations = sorted(recommandations, key=lambda x: x[1])
    recommandations = recommandations[:min(n_recommandations, len(recommandations))]
    return [x[0] for x in recommandations]
    