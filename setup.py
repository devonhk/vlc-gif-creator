from distutils.core import setup
from setuptools import find_packages
import os


REQUIRED = ['requests', 'moviepy']

setup(
    name='vlc_gif_creator',
    version='0.1',
    py_modules=['gif_creator'],
    license='MIT',
    long_description=open('README.md').read(),
    install_requires=REQUIRED,
    author='pydo',
    author_email='pydo@fastmail.com',
    scripts=['gifcreator'],
    data_files=[(os.getenv('HOME'), ['config.ini.default'])]
)
