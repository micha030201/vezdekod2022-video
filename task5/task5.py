import os
import argparse

import requests


parser = argparse.ArgumentParser()
parser.add_argument('--token')
parser.add_argument('--community', type=int)
args = parser.parse_args()

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
    views = video['views']
    id = video['id']
    title = video['title'].replace('"', '')

    print(f'processing {title}...')

    if len(title) <= 5:
        title = f'\u3000\u3000{title}\u3000\u3000'

    image = max(video['image'], key=lambda i: i['width'])

    filename = f'frame_{9999999999-views}_{id}'
    r = requests.get(image['url'])
    with open(filename, 'wb') as f:
        f.write(r.content)

    os.system(f'''\
        convert {filename} -set option:size %[w]x \
        -fill white -background "#00000080" \
        \( label:"{title}" \
            -virtual-pixel background -distort SRT "0.8 0" \
            -virtual-pixel none -distort SRT "0.8 0" \) \
        -gravity south -composite -resize 1920x1080 -background black -gravity center -extent 1920x1080 {filename}_text.jpg''')

print('making video...')

os.system(f'ffmpeg -framerate 0.2 -pattern_type glob -i \'frame_*_text.jpg\' -c:v libx264 -pix_fmt yuv420p {args.community}.mp4')
os.system('rm frame_*')

print('Done!')
