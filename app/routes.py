"""
Routes for browsing movies and controlling the Chromecast media controller.
"""
from flask import (
    Blueprint, current_app, flash, redirect, render_template, url_for,
    safe_join
)
from lib.media import Media
from werkzeug.urls import url_decode
import lib.partial_file as partial_file
import mimetypes
import os
from lib.chromecast import Chromecast
import time

root = Blueprint('root', __name__)


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
    with Chromecast(current_app.config['CHROMECAST_IP']) as chromecast:
        if not chromecast:
            flash('Chromecast not found.', 'error')

        now_playing = None
        is_paused = False

        if chromecast:
            mc = chromecast.connection.media_controller

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
    with Chromecast(current_app.config['CHROMECAST_IP']) as chromecast:
        if not chromecast:
            return redirect(url_for('root.index'))

        media = Media(filename).to_dict()
        mimetype, _ = mimetypes.guess_type(filename)
        chromecast.cast(media['urls']['media'], mimetype)
        time.sleep(6)

    return redirect(url_for('root.index'))


@root.route('/play')
def play():
    """Resume playback of the media on the Chromecast."""
    with Chromecast(current_app.config['CHROMECAST_IP']) as chromecast:
        if not chromecast:
            return redirect(url_for('root.index'))

        chromecast.play()

    return redirect(url_for('root.index'))


@root.route('/pause')
def pause():
    """Pause playback of the media on the Chromecast."""
    with Chromecast(current_app.config['CHROMECAST_IP']) as chromecast:
        if not chromecast:
            return redirect(url_for('root.index'))

        chromecast.pause()

    return redirect(url_for('root.index'))


@root.route('/stop')
def stop():
    """Stop playback of the media on the Chromecast."""
    with Chromecast(current_app.config['CHROMECAST_IP']) as chromecast:
        if not chromecast:
            return redirect(url_for('root.index'))

        chromecast.stop()

    return redirect(url_for('root.index'))


@root.route('/forward')
def forward():
    """Seek forward through the media on the Chromecast."""
    with Chromecast(current_app.config['CHROMECAST_IP']) as chromecast:
        if not chromecast:
            return redirect(url_for('root.index'))

        chromecast.forward()
        time.sleep(6)

    return redirect(url_for('root.index'))


@root.route('/backward')
def backward():
    """Seek backward through the media on the Chromecast."""
    with Chromecast(current_app.config['CHROMECAST_IP']) as chromecast:
        if not chromecast:
            return redirect(url_for('root.index'))

        chromecast.backward()
        time.sleep(6)

    return redirect(url_for('root.index'))


@root.route('/media/<filename>')
def media(filename):
    """Serves a media file via the 206 partial protocol."""
    path = safe_join(current_app.config['MEDIA_PATH'], filename)
    return partial_file.send(path)
