import time
import argparse

import requests


parser = argparse.ArgumentParser()
parser.add_argument('--token')
parser.add_argument('--community', type=int)
args = parser.parse_args()

reported = set()

print('Мониторим новые трансляции...')

while True:
    r = requests.post(
        'https://api.vk.com/method/video.get', data={
            'v': '5.131',
            'owner_id': -args.community,
            'access_token': args.token
        }
    )
    j = r.json()

    if 'error' in j:
        print(f'error code {j["error"]["error_code"]}, {j["error"]["error_msg"]}')
        exit(1)

    for video in j['response']['items']:
        id = video['id']
        title = video['title']

        url = video.get('player', 'нет ссылки')  # idk why that happens

        if 'live' in video and id not in reported:
            reported.add(id)
            print(f'Новая трансляция: {title} -- {url}')

    time.sleep(1)
