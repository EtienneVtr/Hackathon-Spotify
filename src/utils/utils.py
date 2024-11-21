# CE FICHIER EST DESTINE A CONTENIR LES FONCTIONS UTILISEES DANS L'APPLICATION WEB

# Importation des librairies
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import StandardScaler
import joblib
import json
import requests
import random
import string

# FONCTIONS

# Fonction pour donner une liste de recommandations à partir d'une musique
def get_recommandations_from_music(id_music, n_recommandations, option):
    # Chargement des données
    data = pd.read_csv('data/genred_data.csv')

    # On récupère le cluster de la musique
    cluster = data[data['id'] == id_music]['cluster'].values[0]
    
    if option == "cluster":
        # On récupère les musiques du même cluster
        musics = data[data['cluster'] == cluster]

    elif option == "horscluster":
        musics = data[data['cluster'] != cluster]

    else: 
        #cas de base
        musics = data
    
    # On cherche les n_recommandations musiques les plus proches
    # On calcule la distance entre les musiques à l'aide des attributs 'danceability', 'energy', 'loudness', 'speechiness', 'acousticness',
    #                                                                  'instrumentalness', 'liveness', 'valence', 'tempo'
    # On utilise la distance euclidienne
    
    # Extraire les colonnes pertinentes pour le calcul des distances
    feature_columns = ['danceability', 'year', 'energy', 'loudness', 'speechiness', 
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

    for x in recommandations:
        music_genre = musics.loc[musics['id'] == x[0], 'cluster'].values[0]
        print(f"ID: {x[0]}, Distance: {x[1]:.4f}, Cluster: {music_genre}")
    
    # On retourne les id des musiques recommandées
    return [x[0] for x in recommandations]

# Fonction pour donner une liste de recommandations à partir d'une playlist
def get_recommandations_from_playlist(list_id_music, n_recommandations):
    # Chargement des données
    data = pd.read_csv('data/genred_data.csv')
    
    # On récupère les clusters des musiques de la playlist
    clusters = data[data['id'].isin(list_id_music)]['cluster'].values
    
    # On calcule le "centre" des musiques dans leur cluster respectif à l'aide des attributs 'danceability', 'energy', 'loudness', 'speechiness', 'acousticness',
    #                                                                  'instrumentalness', 'liveness', 'valence', 'tempo'
    centers = {}
    feature_columns = ['danceability', 'year', 'energy', 'loudness', 'speechiness', 
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
def save_json_data(file_path, data):
    # Convertir les clés en types compatibles avec JSON
    def convert_keys(obj):
        if isinstance(obj, dict):
            return {str(k): convert_keys(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_keys(i) for i in obj]
        elif isinstance(obj, np.integer):  # Conversion des int64
            return int(obj)
        elif isinstance(obj, np.floating):  # Conversion des float64
            return float(obj)
        elif isinstance(obj, np.ndarray):  # Conversion des tableaux numpy en listes
            return obj.tolist()
        return obj

    data = convert_keys(data)

    # Sauvegarder le fichier JSON
    with open(file_path, 'w') as json_file:
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


# Colonnes pour les caractéristiques
feature_columns = [
    'mode', 'year', 'acousticness', 'danceability', 'duration_ms', 
    'energy', 'instrumentalness', 'liveness', 'loudness', 
    'speechiness', 'tempo', 'valence', 'popularity', 'key'
]
genre_columns = [
    'Ambient', 'Fusion Beat', 'Fusion Hardcore', 'Metal', 'Jazz', 'Rock',
    'World & Electronic Music', 'Punk', 'Folk', 'Traditional Music', 'Indie',
    'Blues, Soul & Country', 'Hip Hop', 'Classical', 'Comedy, Literature & Cultural Narratives',
    'Pop', 'Rap'
]

# Fonction principale mise à jour
def get_recommandations_hors_cluster_adapt(id_music, n_recommandations, feature_weights, genre_weights):
    """
    Recommande des musiques hors cluster avec pondération adaptative.

    - id_music : ID de la musique cible.
    - n_recommandations : Nombre de recommandations souhaitées.
    - feature_weights : Poids pour les caractéristiques des musiques.
    - genre_weights : Poids pour les genres musicaux.
    """
    # Chargement des données
    musics = pd.read_csv('/data/genred_data.csv')

    # Vérification de la colonne 'cluster' dans le dataset
    if 'cluster' not in musics.columns:
        print("Erreur : La colonne 'cluster' n'est pas présente dans le dataset.")
        return []

    # Trouver les caractéristiques de la musique cible
    target_music_features = musics.loc[musics['id'] == id_music, feature_columns].values
    if target_music_features.shape[0] == 0:
        raise ValueError(f"La musique avec l'ID {id_music} est introuvable dans le dataset.")

    # Trouver le genre (cluster) de la musique cible
    target_music_cluster = musics.loc[musics['id'] == id_music, 'cluster'].values[0]

    # Filtrer les autres musiques
    other_musics = musics[musics['id'] != id_music]
    other_features = other_musics[feature_columns].values
    other_clusters = other_musics['cluster'].values  # Récupérer les clusters des autres musiques

    # Standardisation des caractéristiques
    standardized_features = StandardScaler().fit_transform(np.vstack([target_music_features, other_features]))
    target_music_features = standardized_features[0]
    other_features = standardized_features[1:]

    # Application des poids
    weighted_target_features = target_music_features * feature_weights
    weighted_other_features = other_features * feature_weights

    # Calcul des distances pondérées pour les caractéristiques
    feature_distances = euclidean_distances(
        weighted_target_features.reshape(1, -1), weighted_other_features
    ).flatten()

    # Trier les recommandations par distance (les plus proches en premier)
    recommandations = list(zip(other_musics['id'].values, feature_distances))
    recommandations.sort(key=lambda x: x[1])
    recommandations = recommandations[:min(n_recommandations, len(recommandations))]

    # Affichage des recommandations et mise à jour des poids
    print("Recommandations :")
    for rec in recommandations:
        music_name = musics.loc[musics['id'] == rec[0], 'name'].values[0]
        music_genre = musics.loc[musics['id'] == rec[0], 'cluster'].values[0]
        print(f"ID: {rec[0]}, Name: {music_name}, Distance: {rec[1]:.4f}, Cluster: {music_genre}")

        # Demander à l'utilisateur si la musique est aimée
        #liked = input(f"Avez-vous aimé la musique {music_name} (oui/non) ? ").strip().lower() == 'oui'
        liked = np.random.choice([True, False])
        print(liked)
        
        # Mettre à jour les poids
        music_id = rec[0]
        recommended_features = musics.loc[musics['id'] == music_id, feature_columns].values.flatten()
        recommended_cluster = musics.loc[musics['id'] == music_id, 'cluster'].values[0]

        # Le genre est l'indice du cluster dans genre_columns
        recommended_genres = np.zeros(len(genre_columns))
        recommended_genres[recommended_cluster] = 1

        # Mettre à jour les poids des caractéristiques et des genres
        feature_weights = update_weights(feature_weights, recommended_features, liked)
        genre_weights = update_weights(genre_weights, recommended_genres, liked)

        # Afficher les nouveaux poids
        #print("Nouveaux poids des caractéristiques : ", feature_weights)
        #print("Nouveaux poids des genres : ", genre_weights)

    # Retourner les IDs des musiques recommandées
    return [x[0] for x in recommandations]

# Fonction pour mettre à jour les poids en fonction des retours utilisateur
def update_weights(weights, target, liked, learning_rate=0.1):
    """
    Met à jour les poids en fonction des retours utilisateur.

    - weights : Poids actuels (caractéristiques ou genres).
    - target : Valeurs associées à la musique cible (caractéristiques ou genres).
    - liked : Booléen indiquant si l'utilisateur a aimé la recommandation.
    - learning_rate : Taux d'apprentissage.
    """
    factor = 1 if liked else -1
    weights += factor * learning_rate * target
    return np.clip(weights, 0, 1)  # Conserver les poids entre 0 et 1

# Fonction qui renvoit le nom d'un cluster à partir de son ID
def get_cluster_name(cluster_id):
    # Ouverture du fichier CSV des clusters
    clusters = pd.read_csv('data/cluster_characteristics.csv')
    
    # Récupération du nom du cluster
    cluster_name = clusters.loc[clusters['cluster'] == cluster_id, 'name'].values[0]
    
    return cluster_name


# Fonction qui renvoit la première musique pour le flow
def get_first_flow(user_id):
    # Charger la liste des sessions
    sessions = load_json_data('application web/base_de_données/sessions.json')
    
    # Trouver la session de l'utilisateur
    user_session = next((s for s in sessions.get('sessions', []) if s['id'] == user_id), None)

    # Si la session n'existe pas, retourner une erreur
    if user_session is None:
        return {'error': 'Session introuvable.'}
    
    # Vider la liste des musiques déjà vues
    user_session['music_seen'] = []
    
    # Remettre tous les poids des clusters à 1
    user_session['genres_weights'] = [1] * 17
    
    # Récupérer une musique aléatoire de music_flow et la supprimer de la liste
    if user_session['music_flow']:
        music_id = user_session['music_flow'].pop(random.randint(0, len(user_session['music_flow']) - 1))
        user_session['music_seen'].append(music_id)
        save_json_data('application web/base_de_données/sessions.json', sessions)
        
        # Renvoyer l'id de la musique
        return music_id
    else:
        # Si la liste est vide, la remplir avec get_recommandations_from_playlist
        # Récupérer les musiques associées à l'utilisateur
        with open('application web/base_de_données/data.json', 'r') as file:
            data = json.load(file)
            
        # Chercher les musiques associées à l'utilisateur
        user_music = next((p['music'] for p in data.get('profiles', []) if p['id'] == user_id), None)
        
        # Créer une liste de recommandations
        recommendations = get_recommandations_from_playlist(user_music, 100)
        
        # Ajouter les recommandations à la session
        user_session['music_flow'] = recommendations
        
        # Sauvegarder les changements
        save_json_data('application web/base_de_données/sessions.json', sessions)
        
        # Récupérer une musique aléatoire de music_flow et la supprimer de la liste
        if user_session['music_flow']:
            music_id = user_session['music_flow'].pop(random.randint(0, len(user_session['music_flow']) - 1))
            user_session['music_seen'].append(music_id)
            save_json_data('application web/base_de_données/sessions.json', sessions)
            
            # Renvoyer l'id de la musique
            return music_id
        else:
            return {'error': 'Aucune musique disponible.'}

def get_next_flow(user_id, music_id, like=None):
    # Charger la session de l'utilisateur
    sessions = load_json_data('application web/base_de_données/sessions.json')
    user_session = next((s for s in sessions.get('sessions', []) if s['id'] == user_id), None)
    
    if user_session is None:
        return {'error': 'Session introuvable.'}

    # Vérifier si genres_weights est une liste et l'utiliser comme telle
    if isinstance(user_session['genres_weights'], list):
        # Rien à changer, genres_weights est déjà une liste
        pass
    elif not isinstance(user_session['genres_weights'], list):
        user_session['genres_weights'] = [1] * 17  # Liste par défaut avec 17 valeurs à 1

    # Charger les données des musiques
    data = pd.read_csv('data/genred_data.csv')

    if music_id not in data['id'].values:
        return {'error': 'Musique introuvable.'}

    # Récupérer le cluster de la musique (assurez-vous que cluster est un entier)
    cluster = int(data.loc[data['id'] == music_id, 'cluster'].values[0])

    # Mettre à jour les poids des clusters dans la liste
    if like is True:
        # Décrémenter le poids pour le cluster et éviter qu'il ne devienne inférieur à 0.1
        user_session['genres_weights'][cluster] = max(0.1, user_session['genres_weights'][cluster] - 0.1)
    elif like is False:
        # Incrémenter le poids pour le cluster et éviter qu'il ne dépasse 2
        user_session['genres_weights'][cluster] = min(2, user_session['genres_weights'][cluster] + 0.1)

    print("Poids des genres : ", user_session['genres_weights'])

    # Récupérer les caractéristiques de la musique
    feature_columns = ['danceability', 'year', 'energy', 'loudness', 'speechiness', 
                       'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
    features = data.loc[data['id'] == music_id, feature_columns].values[0]

    # Calculer les distances euclidiennes
    distances = euclidean_distances(features.reshape(1, -1), data[feature_columns].values).flatten()

    # Obtenir les clusters des musiques
    clusters = data['cluster'].values
    # Utiliser les poids des genres de la liste pour pondérer les distances
    genres_weights = np.array([user_session['genres_weights'][int(c)] for c in clusters])
    weighted_distances = distances * genres_weights

    # Trier les musiques en fonction des distances pondérées
    sorted_indices = np.argsort(weighted_distances)
    recommended_music = data.iloc[sorted_indices]
    recommended_music = recommended_music[~recommended_music['id'].isin(user_session['music_seen'])]

    if recommended_music.empty:
        return {'error': 'Aucune musique recommandée disponible.'}

    # Sélectionner la musique suivante
    next_music_id = recommended_music.iloc[0]['id']
    user_session['music_seen'].append(next_music_id)

    # Sauvegarder les modifications
    save_json_data('application web/base_de_données/sessions.json', sessions)

    return next_music_id

# Fonction pour mettre à jour, au besoin, la base de données des sessions du profil actuel
def maj_db_sessions(user_id):
    # Charger les profils et les sessions existantes
    with open('application web/base_de_données/data.json', 'r') as file:
        data = json.load(file)
    
    with open('application web/base_de_données/sessions.json', 'r') as file:
        sessions_db = json.load(file)
    
    # Vérifier si l'utilisateur est déjà dans la base de données
    if user_id not in [p['id'] for p in data['profiles']]:
        return {'error': 'Utilisateur introuvable.'}
    
    # Si l'utilisateur n'est pas encore dans la base de données des sessions, l'ajouter
    if user_id not in [s['id'] for s in sessions_db['sessions']]:
        # Récupérer les musiques du profil utilisateur
        user_music = next((p['music'] for p in data['profiles'] if p['id'] == user_id), None)
        
        # Donner des recommandations à l'utilisateur
        if user_music:
            recommendations = get_recommandations_from_playlist(user_music, 100)
        else:
            recommendations = []
        
        # Créer une nouvelle session pour l'utilisateur
        new_session = {
            'id': user_id,
            'musics': user_music,
            'music_flow': recommendations,
            'music_seen': [],
            'genres_weights': [1] * 17
        }
        
        # Ajouter la nouvelle session à la base de données
        sessions_db['sessions'].append(new_session)
        
        # Sauvegarder les modifications
        save_json_data('application web/base_de_données/sessions.json', sessions_db)
        
        print("Session ajoutée avec succès.")
        
    # Comparer la liste des musiques du profil avec la session actuelle
    # Récupérer la session de l'utilisateur
    user_session = next((s for s in sessions_db['sessions'] if s['id'] == user_id), None)
    
    if user_session is None:
        return {'error': 'Session introuvable.'}
    
    # Vérifier si la liste des musiques du profil a changé
    user_music = next((p['music'] for p in data['profiles'] if p['id'] == user_id), None)
    
    if user_music != user_session['musics']:
        # Mettre à jour la session avec les nouvelles recommandations
        if user_music:
            recommendations = get_recommandations_from_playlist(user_music, 100)
        else:
            recommendations = []
        
        # Mettre à jour la session
        user_session['musics'] = user_music
        user_session['music_flow'] = recommendations
        user_session['music_seen'] = []
        
        # Sauvegarder les modifications
        save_json_data('application web/base_de_données/sessions.json', sessions_db)
        
        print("Session mise à jour avec succès.")
    
    


'''# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser les poids (tous égaux à 1 au départ)
    feature_weights = np.ones(13)  # 13 colonnes de caractéristiques
    genre_weights = np.ones(17)    # 17 genres musicaux

    # ID de la musique cible
    id_music = random_id  # Remplacez par un ID valide de votre dataset

    # Obtenir des recommandations
    recommandations = get_recommandations_hors_cluster_adapt(
        id_music, n_recommandations=5, feature_weights=feature_weights, genre_weights=genre_weights
    )'''
