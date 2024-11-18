import requests
import yt_dlp

API_KEY = "AIzaSyD1ZbZB4KM9QovoA7KKzY2orll-MfZR2EQ"

def get_youtube_url(query, api_key):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&key={api_key}"
    response = requests.get(url).json()
    if 'items' in response and len(response['items']) > 0:
        video_id = response['items'][0]['id']['videoId']
        return f"https://www.youtube.com/watch?v={video_id}"
    return None

def download_audio_from_youtube(url):
    options = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': f'{"./data/audios"}/%(title)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

# Étapes :
# 1. Chercher l'URL avec le nom
music_name = "Aieaieouille"
api_key = API_KEY
youtube_url = get_youtube_url(music_name, api_key)

# 2. Télécharger l'audio si l'URL est trouvée
if youtube_url:
    print(f"Downloading audio from: {youtube_url}")
    download_audio_from_youtube(youtube_url)
else:
    print("Music not found!")