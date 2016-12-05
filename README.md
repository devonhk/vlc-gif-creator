## VLC gif generator
--------------------

### Demo

[Watch the tool in action](https://vid.me/PsJk)
--------------------
I wrote this tool because I wanted to create gifs quickly and efficiently.
This tool allows you to effortlessly create gifs from VLC. Big shoutout to [moviepy](https://github.com/Zulko/moviepy).
I wouldn't have thought of writing this tool if it was not for that library. Unfortunately it isn't
maintained anymore.

#### How it works
You start by playing a video in VLC. Whenever you see a scene that you like, you hit the action key
which triggers the tool to connect to VLC's http server to grab metadata about the video your currently watching.
The tool then creates a gif of n seconds long starting from where you were in the video.

#### Setup

First off you need to install VLC media player

    http://www.videolan.org/vlc/

Then configure the VLC http server
<br>

###### First click on Tools > Preferences

###### Then click on select all

![select all](./docs/usage/select_all.png)

###### Click on web interface

![web_interface](./docs/usage/web_interface.png)

###### Set a password for the web interface (username not necessary)

![set_password](./docs/usage/set_password.png)

##### Once VLC is setup you can begin installing the python package
`cd` into the root of the project directory.

`virtualenv -p python3 --no-site-packages env`

`. env/bin/activate`

`pip install -r requirements.txt`

-------------------------------------------

### Configuration

This tool uses a config file for connecting to VLC's http server and for 
creating the GIFs.
To create your own config:

`cp config.ini.default config.ini`

#### Roadmap

I'd like add a real gui (pyqt) and offer snap packages to install the tool.

###### Note

Not affiliated with VLC in any way.

#### License

![license](./LICENSE.md)




