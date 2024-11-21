import sys
import os

# Ajoute le répertoire 'src' au chemin de recherche des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.utils import get_recommandations_from_music, get_recommandations_from_playlist, get_genres_from_user_profile

def test_get_recommandations_from_music():
    print("Test de la fonction get_recommandations")
    id_music = "7xPhfUan2yNtyFG0cUWkt8"
    n_recommandations = 20
    recommandations = get_recommandations_from_music(id_music, n_recommandations)
    print(recommandations)
    
def test_get_recommandations_from_playlist():
    print("Test de la fonction get_recommandations_from_playlist")
    list_id_music = ["7xPhfUan2yNtyFG0cUWkt8", "1o6I8BglA6ylDMrIELygv1", "0NFeJgmTAV1kDfzSQNK41Z"]
    n_recommandations = 2
    recommandations = get_recommandations_from_playlist(list_id_music, n_recommandations)
    print(recommandations)
    
def test_get_genres_from_user_profile():
    print("Test de la fonction get_genres_from_user_profile")
    user_profile = {
        "id": 1,
        "firstname": "John",
        "lastname": "Doe",
        "identifiant": "johndoe",
        "password": "password123",
        "age": 19,
        "gender": "female",
        "education": "masters degree",
        "smoking": "never smoked",
        "alcohol": "social drinker",
        "internet_usage": "few hours a day",
        "village_town": "city",
        "music_consumption": 3,
        "music": []
    }
    n_genres = 5
    genres = get_genres_from_user_profile(user_profile, n_genres)
    print(genres)    

def main(): 
    # Mettre en commentaire les tests que vous ne voulez pas exécuter
    # test_get_recommandations_from_music()
    # test_get_recommandations_from_playlist()
    test_get_genres_from_user_profile()
    
if __name__ == "__main__":
    main()