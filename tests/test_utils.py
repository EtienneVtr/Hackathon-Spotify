import sys
import os

# Ajoute le répertoire 'src' au chemin de recherche des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from utils.utils import get_recommandations_from_music

def test_get_recommandations_from_music():
    print("Test de la fonction get_recommandations")
    id_music = "7xPhfUan2yNtyFG0cUWkt8"
    n_recommandations = 20
    recommandations = get_recommandations_from_music(id_music, n_recommandations)
    print(recommandations)

def main():
    test_get_recommandations_from_music()
    
if __name__ == "__main__":
    main()