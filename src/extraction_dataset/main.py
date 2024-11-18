import sys
import os

# Ajoute le répertoire 'src' au chemin de recherche des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'src')))
from audio_search.main import get_youtube_url, API_KEY
from feature_vector.main import extract_audio_features
import csv


def read_id_and_name(file_path):
    """Lire le fichier CSV contenant les identifiants et noms de musiques."""
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            # Vérifier si les colonnes "id" et "name" existent
            if 'id' not in reader.fieldnames or 'name' not in reader.fieldnames or 'year' not in reader.fieldnames:
                raise ValueError("Les colonnes 'id' et 'name' et 'year' sont absentes du fichier CSV.")

            # Lire les colonnes 'id' et 'name'
            data = [{"id": row['id'], "name": row['name'],"year":row['year']} for row in reader]
            data.sort(key=lambda x: x['year'], reverse=True)
 
            return data
    except FileNotFoundError:
        print(f"Le fichier '{file_path}' est introuvable.")
        return None
    except Exception as e:
        print("Une erreur s'est produite :", e)
        return None


def save_features_to_csv(features, output_file):
    """Sauvegarder les features extraits dans un fichier CSV."""
    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'name', 'tempo', 'chroma_mean', 'spectral_contrast_mean', 'mfcc_mean', 'rms_mean']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for feature in features:
            writer.writerow(feature)


def main():
    # Chemin du fichier CSV avec les ID et les noms des musiques
    input_csv = "./data/data.csv"
    output_csv = "./data/features_output.csv"

    # Lire les données des musiques
    result = read_id_and_name(input_csv)
    if result is None:
        print("Erreur lors de la lecture du fichier CSV d'entrée.")
        return

    # Limiter à 5 musiques pour le test
    result = result[:5]
    features_list = []

    # Traiter chaque musique
    for music in result:
        music_id = music['id']
        music_name = music['name']
        print(f"Traitement de {music_name}...")

        # Chercher l'URL YouTube pour cette musique
        youtube_url = get_youtube_url(music_name, API_KEY)
        if youtube_url:
            print(f"Téléchargement de l'audio de {music_name}...")
            download_audio_from_youtube(youtube_url)

            # Extraire les caractéristiques audio à partir du fichier téléchargé
            # Le fichier audio téléchargé sera dans ./data/audios/
            audio_file_path = f"./data/audios/{music_name}.mp3"
            try:
                feature_vector = extract_audio_features(audio_file_path)
                feature_vector['id'] = music_id
                feature_vector['name'] = music_name
                features_list.append(feature_vector)
            except Exception as e:
                print(f"Erreur lors de l'extraction des caractéristiques pour {music_name}: {e}")
        else:
            print(f"Musique {music_name} non trouvée sur YouTube.")

    # Sauvegarder les features extraits dans un fichier CSV
    save_features_to_csv(features_list, output_csv)
    print(f"Les caractéristiques ont été sauvegardées dans {output_csv}")


if __name__ == "__main__":
    main()