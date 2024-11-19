import pandas as pd
import json
import ast

# Charger le fichier CSV contenant les artistes
data_artist = pd.read_csv('../../data/data_by_artist.csv')

# Initialiser un ensemble pour les artistes afin d'éviter les doublons
artists_set = set()

for index, row in data_artist.iterrows():
    artist = row['artists'].strip('"')  # Supprimer les guillemets
    artists_set.add(artist)  # Ajouter l'artiste à l'ensemble

# Convertir l'ensemble d'artistes en liste de dictionnaires
artists_list = [{"name": artist} for artist in artists_set]

# Charger le fichier CSV contenant les musiques
data_music = pd.read_csv('../../data/data.csv')

# Initialiser une liste pour les musiques
musics_list = []

# Extraire les musiques
for index, row in data_music.iterrows():
    # Créer un dictionnaire pour la musique
    music_entry = {
        "music_id": row['id'],  # ID de la musique
        "title": row['name'],    # Titre de la musique
        "artists": [artist.strip() for artist in ast.literal_eval(row['artists'])]  # Liste des artistes
    }
    musics_list.append(music_entry)

# Créer la structure finale pour le JSON
final_data = {
    "profiles": [],  # Vous pouvez ajouter des profils ici si nécessaire
    "artists": artists_list,
    "musics": musics_list
}

# Écrire le fichier JSON
with open('../../application web/base_de_données/data.json', 'w') as json_file:
    json.dump(final_data, json_file, indent=4)

print("Le fichier JSON a été créé avec succès.")