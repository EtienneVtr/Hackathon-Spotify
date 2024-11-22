# Hackaton Spotify - **TN Flow**

## Membres du groupe : 
- **Christophe HOYAU**
- **Guilhem BARBIER SAINT HILAIRE**
- **Etienne VATRY**

## Lien du projet Kaggle : https://www.kaggle.com/code/vatsalmavani/music-recommendation-system-using-spotify-dataset/notebook 

## Objectifs du projet :

Ce projet s'est organisé autour d'une semaine d'Hackathon. L'objectif était de créer un système de recommandation de musique à partir d'un dataset de Spotify. Nous nous sommes organisés comme suit :
- Exploration et préparation des données
- Clusterisation des genres de musique
- Création de bases de données pour les utilisateurs et les musiques
- Création d'une base de données pour les sessions utilisateurs
- Création d'un système de recommandation de musique :
  - Basé sur les genres de musique
  - Basé sur les utilisateurs
  - Basé sur les sessions utilisateurs
  - Basé sur les caractéristiques des musiques

## Description des fichiers :

- **README.md** : Fichier de description du projet
- **data** : Dossier contenant les données
- **EDA** : Dossier contenant les notebooks de travail pour le nettoyage et l'exploration des données
- **src** : Dossier contenant les scripts de création des bases de données et du système de recommandation
- **application_web** : Dossier contenant les fichiers pour l'application web
- **tests** : Dossier contenant les tests unitaires
- **requirements.txt** : Fichier contenant les dépendances du projet

## Installation des dépendances :

Pour installer les dépendances du projet, il suffit de lancer la commande suivante :
```bash
pip install -r requirements.txt
```

## Lancement des tests unitaires :

Pour lancer les tests unitaires, il faut ouvrir le fichier `tests\test.py`, décommenter les lignes de tests à lancer et lancer le fichier.

## Lancement de l'application web :

Pour lancer l'application web, il suffit de lancer le fichier `application_web\app.py`

## Description des bases de données :

- **data.json** : Base de données contenant les données des musiques et des utilisateurs
- **sessions.json** : Base de données contenant les sessions utilisateurs

## Description des fonctonnalités de l'application web :

- **Recommandation de musique** :
  - **Recommandation de musique par rapport à une musique** : L'utilisateur peut renseigner le nom d'une musique et obtenir des recommandations de musiques similaires.
  - **Recommandation de musique par rapport à une playlist** : L'utilisateur peut sélectionner les musiques présentes dans sa playlist et obtenir des recommandations de musiques similaires. L'utilisateur peut ajouter des musiques à son profil avant de tester cette fonctionnalité.
  - **Recommandation de musique par rapport à un profil utilisateur** : L'utilisateur obtient des genres susceptibles de lui plaire en fonction de son profil. Un modèle de prédiction par rapport à un dataset d'un papier de recherche Slovaque est utilisé pour obtenir ces recommandations.
  - **Flow** : L'utilisateur obtient une musique de départ à partir de sa playlist personnelle et peut choisir s'il l'aime ou non. Cela met à jour les poids de recherche des musiques pour proposer des recommandations plus pertinentes. On utilise ici du *Reinforcement Learning* pour mettre à jour les poids de recherche des musiques. Plus l'utilisateur a ajouté de musiques à son profil et plus la recommandation sera adaptée.

- **Création de compte utilisateur**
- **Connexion à un compte Spotify**
- **Ajout / suppression de musiques à sa playlist personnelle**
- **Mise en mémoire de la session pour la gestion du Flow**