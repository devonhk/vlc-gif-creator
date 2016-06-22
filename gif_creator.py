import os
import sys
import configparser
import argparse
import requests
from moviepy.editor import VideoFileClip
import xml.etree.ElementTree as ET
import keyboard


counter = 0


def generate_gif(media_path: str, time: int, size: float, gif_len, gif_name: str, output_path='.'):
    """
    Args:
        media_path: full path to media
        time: in seconds to create the gif
        size: to resize the gif
        gif_len: duration of gif in seconds
        gif_name: base name of all gifs
        output_path: path to write out file
    """
    clip = VideoFileClip(media_path, audio=False).subclip(
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
    resp = sess.post(url)
    tree = ET.fromstring(resp.text.encode('utf-8'))
    time = tree.find('.//time')
    return int(time.text)


def main():
    global counter
    opts = get_config()
    sess = requests.session()
    sess.auth = (opts['user'], opts['password'])
    time = get_media_time(sess, opts['status'])
    path = get_media_path(sess, opts['playlist'])
    if file_contains_spaces(path):
        sym_link_path = create_symlink(parse_path_unix(path))
        try:
            generate_gif(sym_link_path, time, opts['resize'], opts['gif_len'], opts['gif_name'])
        finally:
            clean_up(sym_link_path)
    else:
        generate_gif(path, time, opts['resize'], opts['gif_len'], opts['gif_name'])
    counter += 1


def get_config() -> dict:
    """
    Returns: dict containing config options
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


def file_contains_spaces(path):
    if '%20' in path:
        return True
    else:
        return False


def create_symlink(path):
    """
    We pass a symlink to ffmpeg, which it gadly accepts.
    This is a workaround when files have spaces.
    Args:
        path: to media file

    Returns: path to symlink of media file
    """
    sym_link_path = '/tmp/tmp_vid_link{}'.format(counter)
    os.system('ln -s {0} {1}'.format(path, sym_link_path))
    return sym_link_path


def clean_up(path):
    os.system('rm {}'.format(path))


if __name__ == '__main__':
    keyboard.add_hotkey('ctrl', lambda: main())

    # Blocks until you press esc.
    keyboard.wait('esc')

