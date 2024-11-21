import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer les fonctions de l'application
from src.utils.utils import *

# Importer les modules Flask et les librairies nécessaires
from flask import Flask, render_template, g, request, redirect, url_for, session, flash, jsonify
import requests
from datetime import datetime
import time

# Variables globales
CLIENT_ID = '27e6e375a4e1446ab580670055e248fe'  # Remplace par ton client_id Spotify
CLIENT_SECRET = 'e79258ab68124cac9d66bcd43bfd19c2'  # Remplace par ton client_secret Spotify
REDIRECT_URI = 'http://127.0.0.1:5000/spotify_callback'
SCOPE = 'user-read-private user-read-email user-read-playback-state user-modify-playback-state'
STATE_KEY = "spotify_auth_state"

access_token = None
page_actuelle = None

# Charger les données depuis le JSON
DATA_FILE = 'application web/base_de_données/data.json'
data = load_json_data(DATA_FILE)

app = Flask(__name__)
app.secret_key = "HACKATHON"
app.config['SECRET_KEY'] = "HACKATHON"


# Middleware pour vérifier si l'utilisateur est connecté
@app.before_request
def check_logged_in_user():
    if 'username' in session:
        g.user = session['username']
    else:
        g.user = None
        

# Route pour la page d'accueil
@app.route('/', methods=['GET', 'POST'])
def acceuil_projet():
    return render_template('acceuil_projet.html')


# Route pour la page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        for profile in data.get('profiles', []):
            if profile['identifiant'] == username and profile['password'] == password:
                session['username'] = profile['identifiant']
                session['user_id'] = profile['id']
                session['firstname'] = profile['firstname']
                session['lastname'] = profile['lastname']
                return redirect(url_for('profile'))

        flash("Identifiants incorrects.")
        return redirect(url_for('login'))
    
    return render_template('login.html')
##recommandationsmultiples utilise get_recommandations_from_playlist, il prend en paramètre une liste d'id de playlist et un nombre de recommandations à retourner ici 10
## il retourne une liste de musique
## pour récupérer la liste de musique il faut utiliser get_music_details sur les "music" dans "profiles" dans le .json


@app.route('/recommandationsmultiples', methods=['GET', 'POST'])
def recommandationsmultiples():
    recommendations = []
    global page_actuelle
    page_actuelle = 'recommandationsmultiples'
    
    if not g.user:
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    user = next((u for u in data['profiles'] if u['id'] == user_id), None)

    if not user:
        return redirect(url_for('logout'))

    # Récupérer les musiques du profil de l'utilisateur
    user_music_ids = user.get('music', [])

    if request.method == 'POST':
        # Obtenir les IDs de playlist sélectionnés
        playlist_ids = request.form.getlist('playlist_ids')  # Récupérer une liste d'IDs de playlists
        num_recommendations = 10  # Nombre de recommandations à retourner

        # Obtenir les recommandations à partir des playlists
        recommendations = get_recommandations_from_playlist(playlist_ids, num_recommendations)

    # Récupérer les détails des musiques avec leurs couvertures d'albums
    user_music_details = []
    spotify_token = session.get('spotify_access_token')  # Récupérer le token Spotify

    for music_id in recommendations:
        music_detail = get_music_details(music_id, data)
        if music_detail:
            # Ajouter l'URL de la couverture d'album
            cover_url = get_album_cover(music_id, spotify_token)
            music_detail['cover_url'] = cover_url
            user_music_details.append(music_detail)

    # Récupérer les playlists de l'utilisateur
    user_playlists = [music for music in data['musics'] if music['music_id'] in user_music_ids]

    return render_template(
        'recommandationsmultiples.html',
        recommandations=user_music_details,
        playlists=user_playlists  # Passer les playlists de l'utilisateur au template
    )

    
@app.route('/recommandationsuniques', methods=['GET', 'POST'])
def recommandationsuniques():
    recommendations = []
    global page_actuelle
    page_actuelle = 'recommandationsuniques'
    if request.method == 'POST':
        music_name = request.form.get('music_name')
        user_id = session.get('user_id')
        user = next((u for u in data['profiles'] if u['id'] == user_id), None)
        
        if user:
            # Rechercher la musique par son titre
            matching_musics = [
                music for music in data.get('musics', [])
                if music_name.lower() in music['title'].lower()
            ]
            
            if matching_musics:
                # Prendre le premier résultat trouvé
                selected_music_id = matching_musics[0]['music_id']
                recommendations = get_recommandations_from_music(selected_music_id, 5)
            else:
                flash("Aucune musique trouvée avec ce nom.")
    
    # Récupérer les détails des musiques et la couverture de l'album
    user_music_details = []
    spotify_token = session.get('spotify_access_token')  # Récupérer le token Spotify
    
    for music_id in recommendations:
        music_detail = get_music_details(music_id, data)
        if music_detail:
            # Ajouter l'URL de la couverture d'album pour chaque musique
            cover_url = get_album_cover(music_id, spotify_token)
            music_detail['cover_url'] = cover_url
            user_music_details.append(music_detail)

    return render_template(
        'recommandationsuniques.html', 
        recommandations=user_music_details,
        music_name=request.form.get('music_name', '')  # Renvoyer la valeur recherchée
    )


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    global page_actuelle
    global access_token
    
    access_token = session.get('spotify_access_token')
    page_actuelle = 'profile'
    
    if not g.user:
        return redirect(url_for('login'))
    
    spotify_user = session.get('spotify_user')
    
    if spotify_user:
        spotify_username = spotify_user.get('display_name', 'Utilisateur Spotify')
    else:
        spotify_username = None
        
    spotify_token = session.get('spotify_access_token')
    
    user_id = session.get('user_id')
    user = next((u for u in data['profiles'] if u['id'] == user_id), None)
    if not user:
        return redirect(url_for('logout'))
    
    if request.method == 'POST':
        # Mettre à jour les informations utilisateur
        user['firstname'] = request.form.get('firstname')
        user['lastname'] = request.form.get('lastname')
        user['age'] = request.form.get('age')
        user['gender'] = request.form.get('gender')
        user['education'] = request.form.get('education')
        user['smoking'] = request.form.get('smoking')
        user['alcohol'] = request.form.get('alcohol')
        user['internet_usage'] = request.form.get('internet_usage')
        user['village_town'] = request.form.get('village_town')
        user['music_consumption'] = request.form.get('music_consumption')

        save_json_data(DATA_FILE, data)
        flash("Profil mis à jour avec succès.")
        return redirect(url_for('profile'))
    
    # Calculer le temps restant pour le token
    token_expires_at = session.get('spotify_token_expires_at')
    if token_expires_at:
        expires_at = datetime.fromtimestamp(token_expires_at)
        time_left = (expires_at - datetime.now()).total_seconds()
        if time_left < 0:
            time_left = 0
    else:
        time_left = 0

    # Récupérer les détails des musiques et la couverture de l'album
    user_music_details = []
    for music_id in user['music']:
        music_detail = get_music_details(music_id, data)
        if music_detail:
            # Récupérer l'URL de la couverture d'album pour chaque musique
            cover_url = get_album_cover(music_id, spotify_token)  # Utilisez votre fonction ici pour récupérer l'URL
            music_detail['cover_url'] = cover_url
            user_music_details.append(music_detail)

    return render_template('profile.html', 
                           user=user, 
                           spotify_username=spotify_username, 
                           musics=data.get('musics', []), 
                           user_music_details=user_music_details, 
                           spotify_token=spotify_token, 
                           token_time_left=time_left)


# Route pour la page de connexion à Spotify
@app.route('/spotify_callback')
def profile_callback():
    code = request.args.get('code')
    state = request.args.get('state')

    # Vérifie le state (facultatif, selon ton implémentation)
    stored_state = session.get('state')
    if not state or state != stored_state:
        return "Erreur : le state ne correspond pas.", 400

    # Échange le code contre un token d'accès
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    response = requests.post(token_url, headers=headers, data=payload)

    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info['access_token']
        refresh_token = token_info['refresh_token']
        expires_in = token_info['expires_in']

        # Calculer l'heure d'expiration
        token_expires_at = int(time.time()) + expires_in

        # Sauvegarder les tokens dans la session
        session['spotify_access_token'] = access_token
        session['spotify_refresh_token'] = refresh_token
        session['spotify_token_expires_at'] = token_expires_at

        # Récupérer les informations de l'utilisateur depuis l'API Spotify
        user_info_url = 'https://api.spotify.com/v1/me'
        user_headers = {
            'Authorization': f'Bearer {access_token}'
        }
        user_response = requests.get(user_info_url, headers=user_headers)

        if user_response.status_code == 200:
            user_info = user_response.json()

            # Sauvegarder les informations de l'utilisateur Spotify dans la session
            session['spotify_user'] = user_info

            # Affiche un message de succès et redirige l'utilisateur vers le profil
            return redirect(url_for('profile'))
        else:
            return "Erreur lors de la récupération des informations utilisateur.", 400
    else:
        return "Erreur lors de la récupération du token.", 400


# Route pour ajouter une musique au profil
@app.route('/add_music', methods=['POST'])
def add_music():
    if not g.user:
        return redirect(url_for('login'))
    
    music_name = request.form.get('music_name')
    user_id = session.get('user_id')
    user = next((u for u in data['profiles'] if u['id'] == user_id), None)
    
    if not user:
        return redirect(url_for('logout'))
    
    # Rechercher la musique par son titre
    matching_musics = [
        music for music in data.get('musics', [])
        if music_name.lower() in music['title'].lower()
    ]
    
    if matching_musics:
        # Ajouter la première musique trouvée (ou affiner la logique)
        selected_music_id = matching_musics[0]['music_id']
        if selected_music_id not in user['music']:
            user['music'].append(selected_music_id)
            save_json_data(DATA_FILE, data)
            flash(f"Musique '{matching_musics[0]['title']}' ajoutée à votre profil.")
        else:
            flash("Cette musique est déjà dans votre profil.")
    else:
        flash("Aucune musique trouvée avec ce nom.")
    
    return redirect(url_for('profile'))


# Route pour rechercher une musique
@app.route('/search_music', methods=['POST'])
def search_music():
    if not g.user:
        return redirect(url_for('login'))
    
    music_name = request.form.get('music_name')
    matching_musics = [
        music for music in data.get('musics', [])
        if music_name.lower() in music['title'].lower()
    ]
    
    if not matching_musics:
        flash("Aucune musique trouvée avec ce nom.")
        return redirect(url_for('profile'))
    
    return render_template('select_music.html', musics=matching_musics)


# Route pour ajouter la musique sélectionnée
@app.route('/add_selected_music/<music_id>', methods=['POST'])
def add_selected_music(music_id):
    if not g.user:
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    user = next((u for u in data['profiles'] if u['id'] == user_id), None)
    
    if not user:
        return redirect(url_for('logout'))
    
    if music_id not in user['music']:
        user['music'].append(music_id)
        save_json_data(DATA_FILE, data)
        flash("Musique ajoutée à votre profil.")
    else:
        flash("Cette musique est déjà dans votre profil.")
    
    return redirect(url_for('profile'))


@app.route('/api/search_music', methods=['GET'])
def api_search_music():
    query = request.args.get('query', '').lower()
    matching_musics = [
        {"title": music['title'], "artists": music['artists'], "music_id": music['music_id']}
        for music in data.get('musics', [])
        if music['title'].lower().startswith(query)  # Utiliser startswith pour les préfixes
    ]
    matching_musics.sort(key=lambda x: x['title'])  # Trier par ordre alphabétique
    limited_musics = matching_musics[:15]  # Limiter à 15 résultats
    return jsonify(limited_musics)


@app.route('/remove_music', methods=['POST'])
def remove_music():
    if not g.user:
        return jsonify({"success": False, "message": "Utilisateur non connecté."}), 401
    
    data_json = request.get_json()
    if not data_json or 'music_id' not in data_json:
        return jsonify({"success": False, "message": "Données JSON invalides."}), 400
    
    music_id = data_json['music_id']
    user_id = session.get('user_id')
    user = next((u for u in data['profiles'] if u['id'] == user_id), None)
    
    if not user:
        return jsonify({"success": False, "message": "Utilisateur introuvable."}), 404
    
    if not isinstance(user.get('music', []), list):
        return jsonify({"success": False, "message": "Erreur interne dans la liste des musiques."}), 500
    
    if music_id in user['music']:
        user['music'].remove(music_id)
        save_json_data(DATA_FILE, data)
        return jsonify({"success": True, "message": "Musique supprimée avec succès.", "music_id": music_id})
    else:
        return jsonify({"success": False, "message": "Musique introuvable dans le profil."}), 400


# Route pour la page d'inscription
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        password = request.form['password']

        # Vérifier si l'utilisateur existe déjà
        if any(profile['identifiant'] == username for profile in data.get('profiles', [])):
            flash("Ce nom d'utilisateur est déjà pris.")
            return redirect(url_for('signup'))

        # Créer un nouvel utilisateur
        new_user = {
            'id': len(data['profiles']) + 1,  # Assurez-vous que l'ID est unique
            'firstname': firstname,
            'lastname': lastname,
            'identifiant': username,
            'password': password,
            'music': []  # Initialiser la liste des musiques
        }

        # Ajouter le nouvel utilisateur à la base de données
        data['profiles'].append(new_user)
        save_json_data(DATA_FILE, data)

        flash("Inscription réussie ! Vous pouvez maintenant vous connecter.")
        return redirect(url_for('login'))

    return render_template('signup.html')


# Route pour initier la connexion à Spotify
@app.route('/spotify_login')
def spotify_login():
    # Générer un `state` aléatoire et le stocker dans la session
    state = generate_state()
    session['state'] = state
    
    # URL d'autorisation Spotify
    auth_url = (
        f"https://accounts.spotify.com/authorize?response_type=code"
        f"&client_id={CLIENT_ID}&scope={SCOPE}&redirect_uri={REDIRECT_URI}"
        f"&state={state}"
    )
    return redirect(auth_url)


# Route pour la déconnexion de Spotify
@app.route('/spotify_logout')
def spotify_logout():
    session.pop('spotify_access_token', None)
    session.pop('spotify_user', None)
    session.pop('spotify_token_expires_at', None)
    return redirect(url_for('profile'))


# Route pour la déconnexion
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# Route pour la lecture de musique
@app.route('/play_music', methods=['POST'])
def play_music():
    spotify_token = session.get('spotify_access_token')
    if not spotify_token:
        return jsonify({'error': 'Utilisateur non authentifié'}), 401
    
    track_uri = request.json.get('track_uri')  # URI de la musique
    device_id = request.json.get('device_id')  # ID de l'appareil

    # Récupérer les appareils disponibles
    devices = get_devices(spotify_token)
    
    if not devices:
        return jsonify({'error': 'Aucun appareil disponible pour la lecture.'}), 400

    # Si aucun device_id n'est spécifié, utiliser le premier appareil disponible
    if not device_id:
        device_id = devices[0]['id']

    # Vérifier si l'appareil est déjà actif
    active_device = next((device for device in devices if device['id'] == device_id and device['is_active']), None)

    if not active_device:
        # Si l'appareil n'est pas actif, on lance la lecture pour l'activer
        result = start_playback(spotify_token, device_id, track_uri)
        if result.get('error'):
            return jsonify(result), 400

    # Démarrer la lecture sur l'appareil spécifié
    result = start_playback(spotify_token, device_id, track_uri)
    return jsonify(result)


@app.route('/stop_music', methods=['POST'])
def stop_music():
    spotify_token = session.get('spotify_access_token')
    if not spotify_token:
        return jsonify({'error': 'Not authenticated'}), 401
    
    url = 'https://api.spotify.com/v1/me/player/pause'
    headers = {'Authorization': f'Bearer {spotify_token}'}
    
    response = requests.put(url, headers=headers)
    
    if response.status_code in [200, 204]:
        return jsonify({'message': 'Playback stopped successfully'})
    else:
        try:
            error_message = response.json().get('error', {}).get('message', 'Unknown error')
        except ValueError:
            error_message = "Aucune information d'erreur disponible."
        return jsonify({'error': error_message}), response.status_code


if __name__ == '__main__':
    app.run()
