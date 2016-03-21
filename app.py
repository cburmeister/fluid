"""
Browse your local movies with IMDB data and stream them to a Chromecast.
"""
from flask import Flask, flash, redirect, render_template, url_for
from media import Media
from werkzeug.urls import url_decode
import argparse
import mimetypes
import os
import partial_file
import pychromecast
import time
import logging
import logging.config
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)
app.config.update({
    'CHROMECAST_IP': os.environ['CHROMECAST_IP'],
    'MEDIA_PATH': os.environ['MEDIA_PATH'],
    'SECRET_KEY': os.environ['SECRET_KEY'],
})


def get_chromecast():
    """Returns a connection to the Chromecast."""
    try:
        return pychromecast.Chromecast(app.config['CHROMECAST_IP'])
    except pychromecast.ChromecastConnectionError:
        pass


def get_media():
    """Returns all available media."""
    valid_ext = ('.mp4', '.mkv', '.avi', '.m2ts', 'm4v')
    files = os.listdir(app.config['MEDIA_PATH'])
    files = filter(lambda x: x.endswith(valid_ext), files)

    media = [Media(x) for x in files]
    return [x.to_dict() for x in media if x.is_valid()]


@app.route('/')
def index():
    """Returns all media within the directory."""
    chromecast = get_chromecast()
    if not chromecast:
        flash('Chromecast not found.', 'error')

    now_playing = None
    is_paused = False

    if chromecast:
        mc = chromecast.media_controller

        time.sleep(1)

        if mc.status.player_is_playing or mc.status.player_is_paused:
            is_paused = mc.status.player_is_paused
            filename = (
                mc.status.title or
                url_decode(mc.status.content_id).keys()[0].split('/')[-1]
            )
            now_playing = Media(filename).to_dict()
        else:
            flash('Chromecast is idle.', 'info')

    return render_template(
        'index.html',
        is_paused=is_paused,
        media=get_media(),
        now_playing=now_playing,
    )


@app.route('/cast/<filename>')
def cast(filename):
    """Cast the filename to a chromecast."""
    chromecast = get_chromecast()
    if not chromecast:
        return redirect(url_for('index'))

    media = Media(filename).to_dict()
    mimetype, _ = mimetypes.guess_type(filename)
    chromecast.media_controller.play_media(media['urls']['media'], mimetype)

    time.sleep(6)

    return redirect(url_for('index'))


@app.route('/play')
def play():
    """Resume playback of the media on the Chromecast."""
    chromecast = get_chromecast()
    if not chromecast:
        return redirect(url_for('index'))

    time.sleep(1)

    chromecast.media_controller.play()

    return redirect(url_for('index'))


@app.route('/pause')
def pause():
    """Pause playback of the media on the Chromecast."""
    chromecast = get_chromecast()
    if not chromecast:
        return redirect(url_for('index'))

    time.sleep(1)

    chromecast.media_controller.pause()

    return redirect(url_for('index'))


@app.route('/stop')
def stop():
    """Stop playback of the media on the Chromecast."""
    chromecast = get_chromecast()
    if not chromecast:
        return redirect(url_for('index'))

    time.sleep(1)

    chromecast.media_controller.stop()
    chromecast.quit_app()

    return redirect(url_for('index'))


@app.route('/forward')
def forward():
    """Seek forward through the media on the Chromecast."""
    chromecast = get_chromecast()
    if not chromecast:
        return redirect(url_for('index'))

    time.sleep(1)

    duration = chromecast.media_controller.status.duration
    current_time = chromecast.media_controller.status.current_time
    batch_size = duration / 20
    chromecast.media_controller.seek(current_time + batch_size)

    time.sleep(6)

    return redirect(url_for('index'))


@app.route('/backward')
def backward():
    """Seek backward through the media on the Chromecast."""
    chromecast = get_chromecast()
    if not chromecast:
        return redirect(url_for('index'))

    time.sleep(1)

    duration = chromecast.media_controller.status.duration
    current_time = chromecast.media_controller.status.current_time
    batch_size = duration / 20
    chromecast.media_controller.seek(current_time - batch_size)

    time.sleep(6)

    return redirect(url_for('index'))


@app.route('/media/<filename>')
def media(filename):
    """Serves a media file via the 206 partial protocol."""
    path = '{}/{}'.format(app.config['MEDIA_PATH'], filename)
    return partial_file.send(path)

def init_logging():
    config = {
        'version': 1,
        'formatters': {
            'simple': {
                'format': '%(asctime)s:%(levelname)s:%(module)s.py:%(lineno)d - %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'simple',
                'stream': 'ext://sys.stderr'
            },
            'file': {
                'class': 'logging.FileHandler',
                'level': 'INFO',
                'formatter': 'simple',
                'filename': 'fluid.log'
            }
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG'
        }
    }

    logging.config.dictConfig(config)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default='5000', type=int)
    args = parser.parse_args()
    
    init_logging()
    app.run(host=args.host, port=args.port, debug=args.debug)
