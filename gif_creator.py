import os
import sys
from pathlib import Path
import configparser
import argparse
import requests
from requests.exceptions import ConnectionError
from moviepy.editor import VideoFileClip
import xml.etree.ElementTree as ET


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
    clip = VideoFileClip(media_path, audio=True).subclip(
        t_start=time,
        t_end=time+gif_len
    ).resize(size)
    clip.write_gif(output_path + '/' + gif_name + str(counter) + '.gif')


def get_media_path(sess: object, url: str) -> str:
    """
    Args:
        sess: requests session object. required for http auth
        url: url pointing to vlc's playlist.xml

    Returns: full path to media
    """
    resp = sess.post(url)
    tree = ET.fromstring(resp.text.encode('utf-8'))
    media_path = tree.find('.//leaf')
    media_path = media_path.attrib.get('uri')
    return media_path[7:]


def get_media_time(sess: object, url: str) -> int:
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
    tree = ET.fromstring(resp.text.encode('utf-8'))
    time = tree.find('.//time')
    return int(time.text)


def main(opts, counter, sess):
    sess.auth = (opts['user'], opts['password'])
    time = get_media_time(sess, opts['status'])
    path = get_media_path(sess, opts['playlist'])
    if file_contains_spaces(path):
        sym_link_path = create_symlink(parse_path_unix(path))
        try:
            generate_gif(sym_link_path, time, opts['resize'], opts['gif_len'], opts['gif_name'], counter, opts['output_path'])
        finally:
            os.remove(sym_link_path)
    else:
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


def parse_path_unix(path):
    characters = {
        '%5B': r'\[',
        '%5D': r'\]',
        '%20': r'\ '
    }
    for char, new_char in characters.items():
        path = path.replace(char, new_char)
    return path


def file_contains_spaces(path: str) -> bool:
    return '%20' in path


def create_symlink(path: str):
    """
    We pass a symlink to ffmpeg, which it gladly accepts.
    This is a workaround when files have spaces.
    Args:
        path: to media file

    Returns: path to symlink of media file
    """
    sym_link_path = '/tmp/tmp_vid_link{}'.format(counter)
    os.symlink(path, sym_link_path)
    return sym_link_path


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
