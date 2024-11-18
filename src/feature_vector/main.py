import librosa
import numpy as np

def extract_audio_features(file_path):
    # Charger le fichier audio
    y, sr = librosa.load(file_path, sr=None)
    
    # Extraction des caractéristiques
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)  # Tempo (battements par minute)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)  # Chromagramme (tonalité)
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)  # Contraste spectral
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)  # MFCC (coefficients cepstraux)
    rms = librosa.feature.rms(y=y)  # Root Mean Square (énergie moyenne)
    
    # Calculer les moyennes et variances pour obtenir un vecteur compact
    feature_vector = {
        "tempo": tempo,
        "chroma_mean": np.mean(chroma, axis=1).tolist(),
        "spectral_contrast_mean": np.mean(spectral_contrast, axis=1).tolist(),
        "mfcc_mean": np.mean(mfcc, axis=1).tolist(),
        "rms_mean": np.mean(rms).tolist()
    }
     # Extraction du chromagramme
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)  # CQT pour plus de précision sur les notes

    # Obtenir les indices des notes dominantes pour chaque frame
    note_indices = np.argmax(chroma, axis=0)
        
    # Correspondance des indices avec les noms des notes
    notes = ['Do', 'Do#', 'Ré', 'Ré#', 'Mi', 'Fa', 'Fa#', 'Sol', 'Sol#', 'La', 'La#', 'Si']
    feature_vector["extracted_notes"] = [notes[idx] for idx in note_indices]


    return feature_vector




