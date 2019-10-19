from os import listdir
from os.path import isfile, join
from flask import Flask, render_template, send_file, abort
import yaml
import get_image_size


try:
    with open('config.yaml', 'r') as yml_file:
        cfg = yaml.load(yml_file, Loader=yaml.SafeLoader)['path']
except (FileNotFoundError, IOError) as e:
    raise e

picture_path = cfg['image']
video_path = cfg['video']

video = []
picture = []
video_ext = ['webm', 'mp4']
images_ext = ['jpg', 'jpeg', 'gif', 'png']
app = Flask(__name__)

for f in sorted(listdir(picture_path)):
    if isfile(join(picture_path, f)) and f.split('.')[-1].lower() in images_ext:
        img = get_image_size.get_image_metadata(join(picture_path, f))
        picture.append(
            {'name': f, 'width': img.width, 'height': img.height})


for f in sorted(listdir(video_path)):
    if isfile(join(video_path, f)) and f.split('.')[-1].lower() in video_ext:
        video.append({'name': f, 'ext': f.split('.')[-1].lower()})


@app.route('/')
def index():
    return render_template('index.html', file_list={'picture': picture, 'video': video})


@app.route('/get_image/<name>')
def get_image(name):
    try:
        return send_file(picture_path + name)
    except FileNotFoundError:
        abort(404)


@app.route('/get_video/<name>')
def get_video(name):
    try:
        return send_file(video_path + name)
    except FileNotFoundError:
        abort(404)
