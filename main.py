import os
from os import listdir
from os.path import isfile, join
import re
from flask import Flask, render_template, send_file, abort, Response, request
import yaml
import get_image_size


try:
    with open('config.yaml', 'r') as yml_file:
        cfg = yaml.load(yml_file, Loader=yaml.SafeLoader)
except (FileNotFoundError, IOError) as e:
    raise e

picture_path = cfg['path']['image']
video_path = cfg['path']['video']
url_static = '//{}/get_{}/{}'

video = []
picture = []
video_ext = ['webm', 'mp4']
images_ext = ['jpg', 'jpeg', 'gif', 'png']
app = Flask(__name__)

if os.path.isdir(picture_path):
    for f in sorted(listdir(picture_path)):
        if isfile(join(picture_path, f)) and f.split('.')[-1].lower() in images_ext:
            img = get_image_size.get_image_metadata(join(picture_path, f))
            picture.append({
                    'name': url_static.format(cfg['host'], 'image', f),
                    'width': img.width,
                    'height': img.height
                })

if os.path.isdir(video_path):
    for f in sorted(listdir(video_path)):
        if isfile(join(video_path, f)) and f.split('.')[-1].lower() in video_ext:
            video.append({
                'name': f,
                'path': url_static.format(cfg['host'], 'video', f),
                'ext': f.split('.')[-1].lower()
            })


@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response


@app.route('/')
def index():
    response = {'picture': picture, 'video': video}
    agent = request.headers.get('User-Agent')
    response['type'] = 'mobile' if ('iphone' or 'android') in agent.lower() else 'desktop'
    return render_template('index.html', response=response)


@app.route('/get_image/<name>')
def get_image(name):
    try:
        return send_file(picture_path + name)
    except FileNotFoundError:
        abort(404)


@app.route('/get_video/<name>')
def get_video(name):
    file_path = video_path + name
    if not os.path.exists(file_path):
        abort(404)

    range_header = request.headers.get('Range', None)
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])

    chunk, start, length, file_size = get_chunk(file_path, byte1, byte2)
    resp = Response(chunk, 206, mimetype='video/mp4',
                      content_type='video/mp4', direct_passthrough=True)
    resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return resp


def get_chunk(full_path='', byte1=None, byte2=None):
    file_size = os.stat(full_path).st_size
    start = 0
    length = 102400

    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start

    with open(full_path, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, file_size


if __name__ == '__main__':
    app.run(host='0.0.0.0')
