import sys
import os

# Ajoute le répertoire 'src' au chemin de recherche des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
import json
import ast

from src.utils.utils import get_cluster_name

def init_db_artists():
    # Charger le fichier CSV contenant les artistes
    data_artist = pd.read_csv('data/data_by_artist.csv')
    
    # Initialiser un ensemble pour les artistes afin d'éviter les doublons
    artists_set = set()

    for index, row in data_artist.iterrows():
        artist = row['artists'].strip('"')  # Supprimer les guillemets
        artists_set.add(artist)  # Ajouter l'artiste à l'ensemble

    # Convertir l'ensemble d'artistes en liste de dictionnaires
    artists_list = [{"name": artist} for artist in artists_set]
    
    return artists_list


def init_db_musics():
    # Charger le fichier CSV contenant les musiques
    data_music = pd.read_csv('data/data_w_clusters.csv')
    
    # Initialiser une liste pour les musiques
    musics_list = []
    
    # Extraire les musiques
    for index, row in data_music.iterrows():
        # Vérifier que les colonnes essentielles ne sont pas vides
        if pd.isnull(row['id']) or pd.isnull(row['name']):
            print(f"Problème avec la ligne {index}: ID ou nom manquant")
            continue  # Passer à la ligne suivante si les données sont manquantes
        
        try:
            artists_list = ast.literal_eval(row['artists']) if isinstance(row['artists'], str) else []
        except (ValueError, SyntaxError) as e:
            print(f"Erreur lors de l'évaluation de la colonne 'artists' pour l'index {index}: {e}")
            artists_list = []  # Si l'évaluation échoue, laisser une liste vide
        
        # Créer un dictionnaire pour la musique
        music_entry = {
            "music_id": row['id'],  # ID de la musique
            "title": row['name'],    # Titre de la musique
            "artists": [artist.strip() for artist in artists_list],  # Liste des artistes
            "annee": row['year'],
            "cluster": get_cluster_name(row['cluster'])  # Utiliser le nom du cluster
        }
        
        musics_list.append(music_entry)
    
    return musics_list


def init_db():
    # Récupérer l'ancien fichier JSON
    with open('application web/base_de_données/data.json', 'r') as json_file:
        old_data = json.load(json_file)
        
    # Supprimer les bases de données 'artists' et 'musics' du fichier JSON
    del old_data['artists']
    del old_data['musics']
    
    # Initialiser les bases de données 'artists' et 'musics'
    artists_list = init_db_artists()
    musics_list = init_db_musics()
    
    # Ajouter les nouvelles bases de données 'artists' et 'musics' au fichier JSON
    old_data['artists'] = artists_list
    old_data['musics'] = musics_list
    
    # Écrire le fichier JSON
    with open('application web/base_de_données/data.json', 'w') as json_file:
        json.dump(old_data, json_file, indent=4)
        
    print("Le fichier JSON a été mis à jour avec succès.")
    
init_db()

'''# Comparer les deux fichiers JSON avec les tailles des bases de données 'artists' et 'musics' pour vérifier que les données ont bien été mises à jour
with open('application web/base_de_données/data.json', 'r') as json_file:
    old_data = json.load(json_file)
with open('src/init_db/data.json', 'r') as json_file:
    new_data = json.load(json_file)
    
print("Taille de la base de données 'artists' avant la mise à jour:", len(old_data['artists']))
print("Taille de la base de données 'artists' après la mise à jour:", len(new_data['artists']))
print("Taille de la base de données 'musics' avant la mise à jour:", len(old_data['musics']))
print("Taille de la base de données 'musics' après la mise à jour:", len(new_data['musics']))'''