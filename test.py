import requests
# API IMPORTANT ELEMENTS
API_URL = "https://api.themoviedb.org/3/movie/42194"
API_KEY = "1ca6e2755aa2b25c46ac7da65e92b5e8"
request_token = "8e5d085b6955f2f0926200fb8bcabeaf26c3849d"

parameters = {
            "api_key": API_KEY,
        }
response = requests.get(url=API_URL, params=parameters)
response.raise_for_status()
data = response.json()
title = data['original_title']
img_url = "https://image.tmdb.org/t/p/w500/" + data['poster_path']
print(img_url)
