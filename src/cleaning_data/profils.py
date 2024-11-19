import pandas as pd

# Charger les données
df = pd.read_csv("data/profils.csv")

# Ne garder que les colonnes utiles : 
# 'Age', 'Gender', 'Education', 'Smoking', 'Alcohol', 'Internet usage', 
# "Music","Slow songs or fast songs","Dance","Folk","Country","Classical music","Musical","Pop","Rock",
# "Metal or Hardrock","Punk","Hiphop, Rap","Reggae, Ska","Swing, Jazz","Rock n roll","Alternative","Latino",
# "Techno, Trance","Opera"
df = df[[
        'Age', 'Gender', 'Education', 'Smoking', 'Alcohol', 'Internet usage',
         'Music', 'Slow songs or fast songs', 'Dance', 'Folk', 'Country', 'Classical music', 'Musical', 'Pop', 'Rock',
            'Metal or Hardrock', 'Punk', 'Hiphop, Rap', 'Reggae, Ska', 'Swing, Jazz', 'Rock n roll', 'Alternative', 'Latino',
            'Techno, Trance', 'Opera']]

# Renommer les colonnes
df.columns = ['age', 'gender', 'education', 'smoking', 'alcohol', 'internet_usage',
            'music', 'slow_songs', 'dance', 'folk', 'country', 'classical', 'musical', 'pop', 'rock',
                'metal_hardrock', 'punk', 'hiphop_rap', 'reggae_ska', 'swing_jazz', 'rock_n_roll', 'alternative', 'latino',
                'techno_trance', 'opera']

# Remplacer les valeurs manquantes par la valeur la plus fréquente
df = df.apply(lambda x: x.fillna(x.value_counts().index[0]))

# Sauvegarder les données
df.to_csv("data/cleaned_profils.csv", index=False)