# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request, send_file, Response
import config
from pathlib import Path
import os
from natsort import natsorted, ns
from os import listdir
from os.path import isfile, join, isdir
import get_image_size
from thumbnail import create_thumbnail

from flask import abort
import sys
import re

prefix = "/video"

video_bp = Blueprint("video", __name__, url_prefix=prefix)


@video_bp.after_request
def after_request(response):
    response.headers.add("Accept-Ranges", "bytes")
    return response


@video_bp.route("/<name>")
@video_bp.route("/<path:name>")
# @auth.login_required
def folder(name=""):
    print(name, file=sys.stdout)
    response = {"videos": prepare_video(name)}
    agent = request.headers.get("User-Agent")
    response["type"] = (
        "mobile" if ("iphone" or "android") in agent.lower() else "desktop"
    )
    return render_template("video.html", response=response)


@video_bp.route("/")
def video():
    response = {"videos": prepare_video()}
    agent = request.headers.get("User-Agent")
    response["type"] = (
        "mobile" if ("iphone" or "android") in agent.lower() else "desktop"
    )
    return render_template("video.html", response=response)


def prepare_video(sub_path=""):
    result = {"videos": [], "folders": []}
    video_path = config.VIDEO_PATH
    thumbnail_path = config.THUMBNAIL_PATH

    if sub_path:
        video_path += sub_path
        abs_path = os.path.abspath(video_path)
        if not (os.path.exists(video_path) and abs_path.find(config.VIDEO_PATH) == 0):
            abort(404)
        name = video_path.replace(config.VIDEO_PATH, "").split("/")[:-1]

        # Добавить путь, что если внутренняя папка - добавить у урл её
        name = "/video/" + "/".join(name)
        result["folders"].append(
            {
                "name": name,
                "icon": "/static/images/back.png",
                "width": 60,
                "height": 60,
            }
        )
    template_path = "{}/{}"

    if os.path.isdir(video_path):
        for f in sorted(listdir(video_path)):
            result_path = join(video_path, f)
            if isfile(result_path) and f.split(".")[-1].lower() in config.VIDEO_EXT:
                filename_without_ext = f.split(".")[0]
                template_thumbnail_file = create_thumbnail(
                    result_path, thumbnail_path, filename_without_ext
                )

                result["videos"].append(
                    {
                        "name": f,
                        "path": config.URL_STATIC_VIDEO
                        + template_path.format(sub_path, f)
                        if sub_path
                        else config.URL_STATIC_VIDEO + f,
                        "ext": f.split(".")[-1].lower(),
                        "thumbnail": config.URL_STATIC_THUMBNAIL
                        + template_thumbnail_file,
                    }
                )
            else:
                f = join(video_path, f).replace(config.VIDEO_PATH, "")
                result["folders"].append(
                    {
                        "name": f,
                        "path": config.URL_STATIC_VIDEO + f,
                        "icon": "/static/images/folder.png",
                        "ext": f.split(".")[-1].lower(),
                        "width": 60,
                        "height": 60,
                    }
                )
    return result


def get_chunk(full_path="", byte1=None, byte2=None):
    file_size = os.stat(full_path).st_size
    start = 0
    length = 102400

    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start

    with open(full_path, "rb") as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, file_size


@video_bp.route("/get_thumbnail/<name>")
def get_thumbnail(name):
    try:
        print(config.URL_STATIC_THUMBNAIL + name)
        return send_file(config.THUMBNAIL_PATH + name)
    except FileNotFoundError:
        abort(404)


@video_bp.route("/get_video/<name>")
@video_bp.route("/get_video/<path:varargs>/<name>")
def get_video(name, varargs=""):

    if varargs:
        varargs += "/"

    file_path = config.VIDEO_PATH + varargs + name
    if not os.path.exists(file_path):
        abort(404)

    range_header = request.headers.get("Range", None)
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r"(\d+)-(\d*)", range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])

    chunk, start, length, file_size = get_chunk(file_path, byte1, byte2)
    resp = Response(
        chunk,
        206,
        mimetype="video/mp4",
        content_type="video/mp4",
        direct_passthrough=True,
    )
    resp.headers.add(
        "Content-Range",
        "bytes {0}-{1}/{2}".format(start, start + length - 1, file_size),
    )
    return resp
