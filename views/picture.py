# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request, send_file
import config
from pathlib import Path
import os
from natsort import natsorted, ns
from os import listdir
from os.path import isfile, join, isdir
import get_image_size

from flask import abort
import sys

prefix = "/picture"

picture_bp = Blueprint("picture", __name__, url_prefix=prefix)


@picture_bp.route("/")
def picture():
    response = {"pictures": prepare_pic()}
    agent = request.headers.get("User-Agent")
    response["type"] = (
        "mobile" if ("iphone" or "android") in agent.lower() else "desktop"
    )
    return render_template("picture.html", response=response)


@picture_bp.route("/<name>")
@picture_bp.route("/<path:name>")
# @auth.login_required
def folder(name=""):
    print(name, file=sys.stdout)
    response = {"pictures": prepare_pic(name)}
    agent = request.headers.get("User-Agent")
    response["type"] = (
        "mobile" if ("iphone" or "android") in agent.lower() else "desktop"
    )
    return render_template("picture.html", response=response)


@picture_bp.route("/get_picture/<name>")
@picture_bp.route("/get_picture/<path:varargs>/<name>")
def get_picture(name, varargs=""):
    try:
        if varargs:
            varargs += "/"
        return send_file(config.IMAGE_PATH + varargs + name)
    except FileNotFoundError:
        abort(404)


def prepare_pic(sub_path=""):
    result = {"pictures": [], "folders": [], "is_back": []}
    picture_path = config.IMAGE_PATH
    template_path = "{}{}"
    if sub_path:
        picture_path += sub_path
        abs_path = os.path.abspath(picture_path)
        if not (os.path.exists(picture_path) and abs_path.find(config.IMAGE_PATH) == 0):
            abort(404)
        name = picture_path.replace(config.IMAGE_PATH, '').split('/')[:-1]
        name = "/picture/" + '/'.join(name)
        result["folders"].append(
            {
                "name": name,
                "icon": "/static/images/back.png",
                "width": 60,
                "height": 60,
            }
        )
        template_path = "{}/{}"

    if os.path.isdir(picture_path):
        for f in natsorted(listdir(picture_path), alg=ns.IGNORECASE):
            result_path = join(picture_path, f)
            if isfile(result_path) and f.split(".")[-1].lower() in config.IMAGES_EXT:
                try:
                    img = get_image_size.get_image_metadata(result_path)
                except get_image_size.UnknownImageFormat as e:
                    continue
                result["pictures"].append(
                    {
                        "name": config.URL_STATIC_IMAGE + template_path.format(sub_path, f),
                        "width": img.width,
                        "height": img.height,
                    }
                )
            elif isdir(result_path):
                f = join(picture_path, f).replace(config.IMAGE_PATH, "")
                print(f)
                result["folders"].append(
                    {
                        "name": f,
                        "folder_name": f.split("/")[-1],
                        "icon": "/static/images/folder.png",
                        "width": 60,
                        "height": 60,
                    }
                )
    else:
        abort(404)
    return result
