import pandas as pd
import joblib

# Charger le modèle et le préprocesseur
model = joblib.load('./src/profil_prediction/models/ridge_model.pkl')
preprocessor = joblib.load('./src/profil_prediction/models/preprocessor.pkl')

new_user = pd.DataFrame([{
    'age': 19,
    'gender': 'male',
    'education': 'college/bachelor degree',
    'smoking': 'never smoked',
    'alcohol': 'drink a lot',
    'internet_usage': 'few hours a day',
    'village_town': 'city',
    'music': 5.0 # Poids pour la musique
}])

# Prétraiter les données
X_new = preprocessor.transform(new_user)

# Prédire les préférences
predicted_preferences = model.predict(X_new)
print("Préférences prédites :", predicted_preferences)