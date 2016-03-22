"""
Routes for browsing movies and controlling the Chromecast media controller.
"""
from flask import (
    Blueprint, current_app, flash, redirect, render_template, url_for
)
from lib.media import Media
from werkzeug.urls import url_decode
import lib.partial_file as partial_file
import logging
import mimetypes
import os
import pychromecast
import time

root = Blueprint('root', __name__)


def get_chromecast():
    """Returns a connection to the Chromecast."""
    try:
        return pychromecast.Chromecast(current_app.config['CHROMECAST_IP'])
    except pychromecast.ChromecastConnectionError:
        logging.error('Chromecast not found.')


def get_media():
    """Returns all available media."""
    valid_ext = ('.mp4', '.mkv', '.avi', '.m2ts', 'm4v')
    files = os.listdir(current_app.config['MEDIA_PATH'])
    files = filter(lambda x: x.endswith(valid_ext), files)
    files = [Media(x) for x in files]
    return [x.to_dict() for x in files if x.is_valid]


@root.route('/')
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


@root.route('/cast/<filename>')
def cast(filename):
    """Cast the filename to a chromecast."""
    chromecast = get_chromecast()
    if not chromecast:
        return redirect(url_for('root.index'))

    media = Media(filename).to_dict()
    mimetype, _ = mimetypes.guess_type(filename)
    chromecast.media_controller.play_media(media['urls']['media'], mimetype)

    time.sleep(6)

    return redirect(url_for('root.index'))


@root.route('/play')
def play():
    """Resume playback of the media on the Chromecast."""
    chromecast = get_chromecast()
    if not chromecast:
        return redirect(url_for('root.index'))

    time.sleep(1)

    chromecast.media_controller.play()

    return redirect(url_for('root.index'))


@root.route('/pause')
def pause():
    """Pause playback of the media on the Chromecast."""
    chromecast = get_chromecast()
    if not chromecast:
        return redirect(url_for('root.index'))

    time.sleep(1)

    chromecast.media_controller.pause()

    return redirect(url_for('root.index'))


@root.route('/stop')
def stop():
    """Stop playback of the media on the Chromecast."""
    chromecast = get_chromecast()
    if not chromecast:
        return redirect(url_for('root.index'))

    time.sleep(1)

    chromecast.media_controller.stop()
    chromecast.quit_app()

    return redirect(url_for('root.index'))


@root.route('/forward')
def forward():
    """Seek forward through the media on the Chromecast."""
    chromecast = get_chromecast()
    if not chromecast:
        return redirect(url_for('root.index'))

    time.sleep(1)

    duration = chromecast.media_controller.status.duration
    current_time = chromecast.media_controller.status.current_time
    batch_size = duration / 20
    chromecast.media_controller.seek(current_time + batch_size)

    time.sleep(6)

    return redirect(url_for('root.index'))


@root.route('/backward')
def backward():
    """Seek backward through the media on the Chromecast."""
    chromecast = get_chromecast()
    if not chromecast:
        return redirect(url_for('root.index'))

    time.sleep(1)

    duration = chromecast.media_controller.status.duration
    current_time = chromecast.media_controller.status.current_time
    batch_size = duration / 20
    chromecast.media_controller.seek(current_time - batch_size)

    time.sleep(6)

    return redirect(url_for('root.index'))


@root.route('/media/<filename>')
def media(filename):
    """Serves a media file via the 206 partial protocol."""
    path = '{}/{}'.format(current_app.config['MEDIA_PATH'], filename)
    return partial_file.send(path)
