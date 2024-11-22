import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
import joblib
from sklearn.model_selection import cross_val_score

# Charger le fichier CSV
file_path = './data/genred_profils.csv'  # Remplace par ton fichier
data = pd.read_csv(file_path)

# Changer le nom de la colonne 'music' en 'music_consumption'
data.rename(columns={'music': 'music_consumption'}, inplace=True)

# Définir les caractéristiques et les cibles
categorical_columns = ['gender', 'education', 'smoking', 'alcohol', 'internet_usage', 'village_town']
numerical_columns = ['age']
target_columns = ['Ambient', 'Fusion Beat', 'Fusion Hardcore', 'Metal', 'Jazz', 'Rock',
    'World & Electronic Music', 'Punk', 'Folk', 'Traditional Music', 'Indie',
    'Blues, Soul & Country', 'Classical', 'Comedy, Literature & Cultural Narratives',
    'Pop', 'Rap']

# La colonne 'music' sera utilisée comme poids
weights_column = 'music_consumption'

X = data[categorical_columns + numerical_columns]
y = data[target_columns]
weights = data[weights_column]

# Prétraitement : Encodage et normalisation
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_columns),
        ('cat', OneHotEncoder(), categorical_columns)
    ]
)

# Transformer les données
X_preprocessed = preprocessor.fit_transform(X)

# Division des données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test, weights_train, weights_test = train_test_split(
    X_preprocessed, y, weights, test_size=0.2, random_state=42
)

# Entraînement Ridge Regression avec recherche d'hyperparamètre alpha
alphas = [0.1, 1, 10, 100, 1000]
best_alpha = None
best_mse = float('inf')
mse_scores = {}

# Recherche de l'alpha optimal
for alpha in alphas:
    model = Ridge(alpha=alpha)
    model.fit(X_train, y_train, sample_weight=weights_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred, multioutput='raw_values').mean()
    mse_scores[alpha] = mse
    if mse < best_mse:
        best_mse = mse
        best_alpha = alpha

print(f"Meilleur alpha pour Ridge Regression : {best_alpha}")

# Réentraînement avec le meilleur alpha
final_model = Ridge(alpha=best_alpha)
final_model.fit(X_train, y_train, sample_weight=weights_train)
y_pred = final_model.predict(X_test)
# Validation croisée pour évaluer le modèle
cv_scores = cross_val_score(final_model, X_train, y_train, cv=5, scoring='neg_mean_squared_error', fit_params={'sample_weight': weights_train})
cv_mse_scores = -cv_scores
print("Scores MSE de la validation croisée :", cv_mse_scores)
print("MSE moyenne de la validation croisée :", cv_mse_scores.mean())

# Évaluation finale
mse_per_genre = mean_squared_error(y_test, y_pred, multioutput='raw_values')
mae_per_genre = mean_absolute_error(y_test, y_pred)
print("MSE pour chaque genre :", mse_per_genre)
print("MSE moyenne :", mse_per_genre.mean())
print("MAE pour chaque genre :", mae_per_genre)
print("MAE moyenne :", mae_per_genre.mean())

# Graphiques des performances
plt.figure(figsize=(12, 6))
genres = target_columns

'''# MSE par genre
plt.bar(genres, mse_per_genre, color='lightcoral', alpha=0.7, label='MSE')
plt.bar(genres, mae_per_genre, color='skyblue', alpha=0.7, label='MAE')
plt.xticks(rotation=45)
plt.ylabel('Erreur')
plt.title('Performances par genre musical')
plt.legend()
plt.tight_layout()
plt.show()'''

# Sauvegarde du modèle
joblib.dump(final_model, './src/profil_prediction/models/ridge_model.pkl')
joblib.dump(preprocessor, './src/profil_prediction/models/preprocessor.pkl')
print("Modèle final et préprocesseur sauvegardés.")


'''
Exemple d'utilisation du modèle sauvegardé :
# Charger le modèle et le préprocesseur
model = joblib.load('./src/cluster_prediction/models/Ridge Regression_model.pkl')
preprocessor = joblib.load('./src/cluster_prediction/models/preprocessor.pkl')

# Exemple de nouvel utilisateur
new_user = pd.DataFrame([{
    'age': 25,
    'gender': 'male',
    'education': 'college/bachelor degree',
    'smoking': 'never smoked',
    'alcohol': 'drink a lot',
    'internet_usage': 'few hours a day',
    'village_town': 'city',
    'music_consumption': 4.0 # Poids pour la musique
}])

# Prétraiter les données
X_new = preprocessor.transform(new_user)

# Prédire les préférences
predicted_preferences = model.predict(X_new)
print("Préférences prédites :", predicted_preferences)
'''
