import requests

username = input('Enter the github username: ')
query_url = f'https://api.github.com/users/{username}/repos'

req = requests.get(query_url)
json = req.json()

if len(json) > 0:
    print(f"\n{username}'s repos:\n")
    for i in range(0, len(json)):
        print(i + 1, json[i]['name'])
else:
    print('\nno data found')
