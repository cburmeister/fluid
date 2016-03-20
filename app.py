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

app = Flask(__name__)
app.config.update({
    'CHROMECAST_IP': os.environ['CHROMECAST_IP'],
    'MEDIA_PATH': os.environ['MEDIA_PATH'],
    'SECRET_KEY': os.environ['SECRET_KEY'],
})


def get_chromecast():
    """Returns a connection to the Chromecast."""
    return pychromecast.Chromecast(app.config['CHROMECAST_IP'])


def get_media():
    """Returns all available media."""
    media = os.listdir(app.config['MEDIA_PATH'])
    media = filter(lambda x: x.endswith(('.mp4', '.mkv')), media)
    return [Media(x).to_dict() for x in media]


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default='5000', type=int)
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)
