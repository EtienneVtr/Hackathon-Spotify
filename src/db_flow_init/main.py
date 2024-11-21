import sys
import os

# Ajoute le répertoire 'src' au chemin de recherche des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.utils import get_recommandations_from_playlist

import json


def init_db_sessions():
    # Charger les profils à partir du fichier JSON existant
    with open('application web/base_de_données/data.json', 'r') as file:
        data = json.load(file)
    
    # Initialiser la structure des sessions
    sessions = []
    
    # Parcourir chaque profil et générer des sessions
    for profile in data.get('profiles', []):
        profile_id = profile['id']
        list_id_music = profile.get('music', [])  # Musiques associées au profil
        
        if list_id_music:  # Si le profil a des musiques
            # Obtenir les recommandations pour le profil
            recommendations = get_recommandations_from_playlist(list_id_music, 100)
        else:
            recommendations = []  # Pas de recommandations si pas de musiques associées
            
        # Initialise une liste de poids à 1 pour chaque genre = faire une liste de 17 éléments à 1
        genres_weights = [1] * 17
        
        # Ajouter une session pour ce profil
        sessions.append({
            "id": profile_id,
            "music_flow": recommendations,
            "music_seen": [],
            "genres_weights": genres_weights
        })
    
    # Créer le fichier JSON des sessions
    sessions_db = {"sessions": sessions}
    with open('application web/base_de_données/sessions.json', 'w') as file:
        json.dump(sessions_db, file, indent=4)
    
    print("Base de données des sessions créée avec succès.")

init_db_sessions()