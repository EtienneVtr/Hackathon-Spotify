from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score
import xgboost as xgb
import pandas as pd
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import numpy as np

# Charger les données
musics = pd.read_csv("data/data_w_clusters.csv")

def train_with_cross_validation(musics, n_splits=5):
    # Sélectionner les caractéristiques et la cible
    X = musics[['mode', 'acousticness', 'danceability', 'duration_ms', 'energy',
                'instrumentalness', 'liveness', 'loudness', 'speechiness',
                'tempo', 'valence', 'popularity', 'key']]
    y = musics['cluster']

    unique_labels = y.unique()
    print(f"Labels uniques : {unique_labels}")

    # Normalisation des données
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Initialisation du Stratified KFold
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    # Liste pour stocker les scores de chaque fold
    fold_accuracies = []
    evals_results = []  # Liste pour garder les résultats d'évaluation

    # Boucle sur les folds pour effectuer la validation croisée
    for fold, (train_index, val_index) in enumerate(skf.split(X_scaled, y)):
        X_train, X_val = X_scaled[train_index], X_scaled[val_index]
        y_train, y_val = y[train_index], y[val_index]
        
        print(f"Entraînement du modèle pour le fold {fold + 1} / {n_splits}...")  # Affiche le fold actuel
        
        # Création des DMatrix pour XGBoost
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dval = xgb.DMatrix(X_val, label=y_val)

        # Paramètres pour l'entraînement
        params = {
            'objective': 'multi:softmax',  # Classification multiclasses
            'num_class': len(y.unique()),  # Nombre de classes
            'eval_metric': ['merror', 'mlogloss'],  # Métriques à suivre
            'max_depth': 6,
            'learning_rate': 0.1,
            'random_state': 42
        }

        # Dictionnaire pour stocker les résultats de l'entraînement
        evals_result = {}

        # Entraînement du modèle XGBoost avec affichage de la progression
        model = xgb.train(params, dtrain, num_boost_round=100, 
                          evals=[(dtrain, 'train'), (dval, 'val')],
                          evals_result=evals_result, verbose_eval=10)  # Affiche toutes les 10 itérations

        # Suivi des performances
        evals_results.append(evals_result)  # Ajout des résultats du fold

        # Prédictions sur les données de validation
        y_pred = model.predict(dval)

        # Calcul de l'accuracy pour ce fold
        accuracy = accuracy_score(y_val, y_pred)
        fold_accuracies.append(accuracy)

        # Sauvegarder le modèle à la fin de chaque fold (optionnel)
        # model.save_model(f'./src/cluster_prediction/models/model_fold_{fold}.model')

    # Affichage des résultats
    print(f"Accuracy moyenne sur {n_splits} folds: {sum(fold_accuracies) / n_splits:.4f}")
    print(f"Écart-type de l'accuracy: {pd.Series(fold_accuracies).std():.4f}")

    # Affichage de l'évolution des métriques pour chaque fold
    plot_metrics(evals_results, save_path='src/cluster_prediction/models/metrics_plot.png')
    
    # Retourner le modèle final
    return model, n_splits

def plot_metrics(evals_results, save_path=None):
    """
    Fonction pour afficher et sauvegarder les courbes d'évolution des métriques pendant l'entraînement.
    """
    epochs = len(evals_results[0]['train']['merror'])  # Nombre d'époques

    # Création de la figure et des sous-graphiques
    fig, axs = plt.subplots(1, 2, figsize=(15, 6))

    # Calcul des moyennes des métriques sur tous les folds
    train_errors = [evals_result['train']['merror'] for evals_result in evals_results]
    test_errors = [evals_result['val']['merror'] for evals_result in evals_results]
    
    # Calcul des moyennes des Log-Loss sur tous les folds
    train_logloss = [evals_result['train']['mlogloss'] for evals_result in evals_results]
    test_logloss = [evals_result['val']['mlogloss'] for evals_result in evals_results]

    # Courbe de l'erreur (MError)
    axs[0].plot(range(epochs), np.mean(train_errors, axis=0), label='Train M-Error')
    axs[0].plot(range(epochs), np.mean(test_errors, axis=0), label='Test M-Error')
    axs[0].set_title('M-Error')
    axs[0].set_xlabel('Époque')
    axs[0].set_ylabel('M-Error')
    axs[0].legend()

    # Courbe de M-Log-Loss
    axs[1].plot(range(epochs), np.mean(train_logloss, axis=0), label='Train M-Log-Loss')
    axs[1].plot(range(epochs), np.mean(test_logloss, axis=0), label='Test M-Log-Loss')
    axs[1].set_title('M-Log-Loss')
    axs[1].set_xlabel('Époque')
    axs[1].set_ylabel('M-Log-Loss')
    axs[1].legend()

    # Affichage des graphiques
    plt.tight_layout()

    # Sauvegarde des graphiques si un chemin est fourni
    if save_path:
        plt.savefig(save_path)
        print(f"Graphiques sauvegardés à {save_path}")
    else:
        plt.show()

# Appel de la fonction
model, n_splits = train_with_cross_validation(musics, n_splits=10)

# Sauvegarde du modèle final
model.save_model(f'src/cluster_prediction/models/xgboost_model_10splits.model')