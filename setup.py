from setuptools import find_packages, setup
import os


REQUIRED = ['requests>=2.18.4', 'moviepy==0.2.3.2']

setup(
    name='vlc_gif_creator',
    version='0.1',
    py_modules=['gif_creator'],
    license='MIT',
    description='CLI tool used to create gifs from videos playing in VLC',
    url='https://github.com/pydo/vlc-gif-creator',
    long_description=open('README.md').read(),
    install_requires=REQUIRED,
    author='pydo',
    author_email='pydo@fastmail.com',
    scripts=['gifcreator'],
    keywords='vlc gif video',
    data_files=[(os.getenv('HOME'), ['config.ini.default'])]
)
