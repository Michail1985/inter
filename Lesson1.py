import requests
import json

url = 'https://api.github.com'
username = 'Michail1985'

r = requests.get(f'{url}/users/{username}/repos')

with open('data.json', 'w') as f:
    json.dump(r.json(), f)

for i in r.json():
    print(i['name'])