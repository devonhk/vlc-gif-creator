#!/usr/bin/env python

import configparser
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

import requests
from moviepy.editor import VideoFileClip
from requests.exceptions import ConnectionError


def generate_gif(media_path: str, time: int, size: float, gif_len: int, gif_name: str, counter: int, output_path='.'):
    """
    Args:
        media_path: full path to media
        time: in seconds to create the gif
        size: to resize the gif
        gif_len: duration of gif in seconds
        gif_name: base name of all gifs
        counter: number appended to filename
        output_path: path to write out file
    """
    clip = VideoFileClip(media_path, audio=False).subclip(
        t_start=time,
        t_end=time + gif_len
    ).resize(size)
    clip.write_gif(output_path + '/' + gif_name + str(counter) + '.gif', program='ffmpeg')


def get_media_path(sess: requests.Session, url: str, filename: str) -> str:
    """
    Args:
        sess: requests session object. required for http auth
        url: url pointing to vlc's playlist.xml
        filename: name of media content

    Returns: full path to media
    """
    resp = sess.post(url)
    tree = ET.fromstring(resp.text)
    media_path = tree.find('.//leaf[@name="{filename}"]'.format(filename=filename)).get('uri')
    media_path = unquote(media_path)
    return media_path


def get_media_time(sess: requests.Session, url: str) -> tuple:
    """
    Args:
        sess: requests session object. required for http auth
        url: url pointing to vlc's status.xml

    Returns: time in seconds
    """
    try:
        resp = sess.post(url)
    except ConnectionError as e:
        print(e, "\nConnection failed. Did you remember to enable VLC's lua http server?")
        sys.exit(-1)
    tree = ET.fromstring(resp.text)
    time = tree.find('.//time')
    filename = tree.find('.//info[@name="filename"]')
    return int(time.text), filename.text


def main(opts, counter, sess):
    sess.auth = (opts['user'], opts['password'])
    time, filename = get_media_time(sess, opts['status'])
    path = get_media_path(sess, opts['playlist'], filename)
    generate_gif(path, time, opts['resize'], opts['gif_len'], opts['gif_name'], counter, opts['output_path'])


def get_config() -> dict:
    """
    Returns: dict containing config.ini options
    """
    config = configparser.ConfigParser()
    config.read('config.ini')
    user = config['VLC CREDENTIALS']['user']
    password = config['VLC CREDENTIALS']['password']
    resize = float(config['CROPPING']['resize'])
    playlist = config['VLC SERVER']['playlist']
    status = config['VLC SERVER']['status']
    gif_len = int(config['GIF']['length'])
    gif_name = config['GIF']['name']
    output_path = config['GIF']['output_path']
    return dict(
        user=user, password=password, resize=resize,
        playlist=playlist, status=status, gif_len=gif_len,
        gif_name=gif_name, output_path=output_path
    )


def create_output_dir(path: str):
    """Create gif output dir if it doesn't exists"""
    if not Path(path).exists():
        os.mkdir(path)


def run():
    counter = 0
    sess = requests.session()
    config = get_config()
    create_output_dir(config['output_path'])
    while True:
        make_gif = input('Create a gif? y/Y:yes, q/Q:quit\n').lower()
        if make_gif == 'y':
            print('making gif...')
            main(config, counter, sess)
            counter += 1
        if make_gif == 'q':
            print('Bye.')
            sys.exit()


if __name__ == '__main__':
    run()
