import re
import argparse

import requests


parser = argparse.ArgumentParser()
parser.add_argument('--token')
parser.add_argument('--video')
parser.add_argument('--options', nargs='+')
args = parser.parse_args()

owner_id, video_id = args.video.split('_')
owner_id = int(owner_id)

counts = {option: set() for option in args.options}
total_comments = 0

last_id = 0

while True:
    while True:
        r = requests.post(
            'https://api.vk.com/method/video.getComments', data={
                'v': '5.131',
                'owner_id': owner_id,
                'video_id': video_id,
                'access_token': args.token,
                'count': 100,
                'start_comment_id': last_id
            }
        )
        j = r.json()

        if 'error' in j:
            if owner_id > 0:
                owner_id = -owner_id
                continue
            else:
                print(f'error code {j["error"]["error_code"]}, {j["error"]["error_msg"]}')
                exit(1)

        break

    if len(j['response']['items']) <= 1:
        break

    for comment in j['response']['items']:
        total_comments += 1
        last_id = comment['id']

        author = comment['from_id']
        text = comment['text']

        for option in args.options:
            if re.search(option, text):
                # Prioritize the most recent answer from a given author
                for s in counts.values():
                    s.discard(author)
                counts[option].add(author)

print(f'Проанализированно {total_comments} комментариев.\n')

for i, (option, votes) in enumerate(sorted(counts.items(), key=lambda t: len(t[1]), reverse=True)):
    print(f'{i+1} место, {len(votes)} голосов: {option}')
