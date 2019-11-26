# -*- coding: utf8 -*-
import os
import av


def create_thumbnail(video_filename, thumbnail_folder_path, filename_without_ext):

    if not os.path.exists(thumbnail_folder_path):
        os.makedirs(thumbnail_folder_path)

    filepath = f'{thumbnail_folder_path}/{filename_without_ext}.jpg'
    if not os.path.isfile(filepath):
        container = av.open(video_filename)
        frame = next(container.decode(video=0))
        frame.reformat(500, 400, 'rgb24').to_image().save(filepath)
    return f'{filename_without_ext}.jpg'
