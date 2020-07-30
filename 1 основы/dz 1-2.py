import requests
import json

url = "https://google-translate1.p.rapidapi.com/language/translate/v2"
print('Translate to Russian')
text = input('Input text: ')
lang = 'ru'

payload = f'q={text}&target={lang}'
headers = {
    'x-rapidapi-host': "google-translate1.p.rapidapi.com",
    'x-rapidapi-key': "4201deac85msh7faa311b2aee6b8p16fdacjsn6a344eb3eef4",
    'accept-encoding': "application/gzip",
    'content-type': "application/x-www-form-urlencoded"
    }

response = requests.request("POST", url, data=payload, headers=headers)
res = json.loads(response.text)

print(res['data']['translations'])