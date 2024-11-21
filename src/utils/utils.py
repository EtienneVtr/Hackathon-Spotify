# CE FICHIER EST DESTINE A CONTENIR LES FONCTIONS UTILISEES DANS L'APPLICATION WEB

# Importation des librairies
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances
import joblib
import json
import requests
import random
import string

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

# Fonction pour proposer des genres musicaux à un utilisateur en fonction de son profil
def get_genres_from_user_profile(user_profile, n_genres):
    # Charger le modèle et le préprocesseur
    model = joblib.load('./src/profil_prediction/models/ridge_model.pkl')
    preprocessor = joblib.load('./src/profil_prediction/models/preprocessor.pkl')
    
    # Convertir le profil utilisateur en DataFrame
    user_df = pd.DataFrame([user_profile])
    
    # Enlever les champs inutiles avant transformation
    user_df = user_df.drop(columns=['id', 'firstname', 'lastname', 'identifiant', 'password', 'music'])
    
    # Prétraiter les données
    X_new = preprocessor.transform(user_df)
    
    # Prédire les préférences 
    predicted_preferences = model.predict(X_new)
    
    # Associer les préférences aux genres musicaux
    genres = ['Ambient', 'Fusion Beat', 'Fusion Hardcore', 'Metal', 'Jazz', 'Rock', 'World & Electronic Music', 'Punk', 
              'Folk', 'Traditional Music', 'Indie', 'Blues, Soul & Country', 'Hip Hop', 'Classical', 
              'Comedy, Literature & Cultural Narratives', 'Pop', 'Rap']
    
    # Associer les préférences aux genres
    genres_preferences = list(zip(genres, predicted_preferences[0]))
    
    # Trier les genres par préférence
    genres_preferences.sort(key=lambda x: x[1], reverse=True)
    
    # Garder les `n_genres` meilleurs genres
    genres_preferences = genres_preferences[:min(n_genres, len(genres_preferences))]
    
    # Retourner les genres
    return genres_preferences

# Fonction pour ajouter une musique au dataset
def add_music_to_dataset(music):
    pass

# Charger les données JSON
def load_json_data(filename):
    with open(filename, 'r') as json_file:
        return json.load(json_file)

# Sauvegarder les données JSON
def save_json_data(filename, data):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)
        
# Fonction pour renvoyer les appareils disponibles pour la lecture
def get_devices(spotify_token):
    url = 'https://api.spotify.com/v1/me/player/devices'
    headers = {
        'Authorization': f'Bearer {spotify_token}'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        devices = response.json().get('devices', [])
        return devices
    else:
        return None

# Fonction pour démarrer la lecture d'une piste
def start_playback(spotify_token, device_id, track_uri):
    url = f'https://api.spotify.com/v1/me/player/play?device_id={device_id}'
    headers = {
        'Authorization': f'Bearer {spotify_token}'
    }
    
    # Ajout du préfixe si ce n'est pas déjà une URI complète
    if not track_uri.startswith("spotify:track:"):
        track_uri = f"spotify:track:{track_uri}"
        
    payload = {
        'uris': [track_uri]  # Liste contenant l'URI de la piste
    }
    
    response = requests.put(url, headers=headers, json=payload)
    
    if response.status_code == 204:
        return {'message': 'Lecture démarrée avec succès.'}
    else:
        try:
            error_message = response.json().get('error', {}).get('message', 'Unknown error')
        except ValueError:
            error_message = "Aucune information d'erreur disponible."
        return {'error': error_message, 'status': response.status_code}
    
# Fonction pour obtenir la pochette d'un album
def get_album_cover(music_id, access_token):
    url = f"https://api.spotify.com/v1/tracks/{music_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        track_data = response.json()
        album_images = track_data.get('album', {}).get('images', [])
        if album_images:
            return album_images[0]['url']  # URL de la meilleure résolution
    return None

# Fonction pour générer un `state` aléatoire
def generate_state():
    """Génère un `state` aléatoire pour prévenir les attaques CSRF."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

# Fonction pour obtenir les détails d'une musique
def get_music_details(music_id, data):
    music = next((m for m in data.get('musics', []) if m['music_id'] == music_id), None)
    if music:
        return {
            "title": music['title'],
            "artists": music['artists'],
            "music_id": music_id
        }
    return None