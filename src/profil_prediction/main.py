import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.multioutput import MultiOutputRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
import joblib

# Charger le fichier CSV
file_path = './data/cleaned_profils.csv'  # Remplace par ton fichier
data = pd.read_csv(file_path)

# Définir les caractéristiques et les cibles
categorical_columns = ['gender', 'education', 'smoking', 'alcohol', 'internet_usage', 'village_town']
numerical_columns = ['age']
target_columns = ['music', 'slow_songs', 'dance', 'folk', 'country', 'classical',
                  'musical', 'pop', 'rock', 'metal_hardrock', 'punk', 'hiphop_rap',
                  'reggae_ska', 'swing_jazz', 'rock_n_roll', 'alternative', 'latino',
                  'techno_trance', 'opera']

X = data[categorical_columns + numerical_columns]
y = data[target_columns]

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
X_train, X_test, y_train, y_test = train_test_split(X_preprocessed, y, test_size=0.2, random_state=42)

# Modèle unique : Ridge Regression
model_name = "Ridge Regression"
model = MultiOutputRegressor(Ridge(alpha=1.0))

# Entraînement du modèle
print(f"Entraînement du modèle {model_name}...")
model.fit(X_train, y_train)

# Prédictions
y_pred = model.predict(X_test)

# Évaluation du modèle
mse = mean_squared_error(y_test, y_pred, multioutput='raw_values')
print(f"{model_name} - MSE moyenne : {mse.mean()}")

# Sauvegarder le modèle
joblib.dump(model, f'./src/profil_prediction/models/{model_name}_model.pkl')
joblib.dump(preprocessor, './src/profil_prediction/models/preprocessor.pkl')

print(f"Modèle sauvegardé : {model_name}")

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
    'village_town': 'city'
}])

# Prétraiter les données
X_new = preprocessor.transform(new_user)

# Prédire les préférences
predicted_preferences = model.predict(X_new)
print("Préférences prédites :", predicted_preferences)
'''
