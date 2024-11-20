from flask import Flask, render_template, g, request, redirect, url_for, session, flash, jsonify
import json

# Charger les données JSON
def load_json_data(filename):
    with open(filename, 'r') as json_file:
        return json.load(json_file)

# Sauvegarder les données JSON
def save_json_data(filename, data):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Charger les données depuis le JSON
DATA_FILE = 'base_de_données/data.json'
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

# Route pour la page de profil
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not g.user:
        return redirect(url_for('login'))
    
    # Récupérer l'utilisateur connecté
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
    
    # Passer les données nécessaires au template
    return render_template('profile.html', user=user, musics=data.get('musics', []))

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
# Route pour la déconnexion
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
