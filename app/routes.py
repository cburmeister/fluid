"""
Routes for browsing movies and controlling the Chromecast media controller.
"""
from flask import Blueprint, current_app, render_template, jsonify, g
from lib.chromecast import Chromecast
from lib.media import Media
from werkzeug.urls import url_decode
import lib.partial_file as partial_file
import mimetypes
import os

root = Blueprint('root', __name__)


@root.before_request
def before_request():
    """Initialize a connection to the Chromecast before each request."""
    g.chromecast = Chromecast(current_app.config['CHROMECAST_IP'])


@root.after_request
def after_request(response):
    """Disconnect from the chromecast before each response."""
    if g.chromecast:
        g.chromecast.disconnect()

    return response


@root.route('/')
def index():
    """Returns the page markup."""
    return render_template('index.html')


@root.route('/media')
def media():
    """Return all available media as JSON."""
    valid_ext = ('.mp4', '.mkv', '.avi', '.m2ts', 'm4v')
    media = os.listdir(current_app.config['MEDIA_PATH'])
    media = filter(lambda x: x.endswith(valid_ext), media)
    media = [Media(x) for x in media]
    media = [x.to_dict() for x in media if x.is_valid]
    return jsonify(media=media)


@root.route('/chromecast/status')
def chromecast_status():
    """Return Chromecast status as JSON."""
    if not g.chromecast:
        return jsonify(chromecast=None)

    status = g.chromecast.connection.media_controller.status
    args = {
        'current_time': status.current_time,
        'duration': status.duration,
        'is_idle': status.player_is_idle,
        'is_paused': status.player_is_paused,
        'is_playing': status.player_is_playing,
    }
    try:
        filename = (
            status.title or
            url_decode(status.content_id).keys()[0].split('/')[-1]
        )
        args['now_playing'] = Media(filename).to_dict()
    except:
        pass

    return jsonify(chromecast=args)


@root.route('/cast/<filename>')
def cast(filename):
    """Cast the filename to a chromecast."""
    if not g.chromecast:
        return jsonify(chromecast=None)

    media = Media(filename).to_dict()
    mimetype, _ = mimetypes.guess_type(filename)
    g.chromecast.cast(media['urls']['media'], mimetype)

    return jsonify()


@root.route('/play')
def play():
    """Resume playback of the media on the Chromecast."""
    if not g.chromecast:
        return jsonify(chromecast=None)

    g.chromecast.play()

    return jsonify()


@root.route('/pause')
def pause():
    """Pause playback of the media on the Chromecast."""
    if not g.chromecast:
        return jsonify(chromecast=None)

    g.chromecast.pause()

    return jsonify()


@root.route('/stop')
def stop():
    """Stop playback of the media on the Chromecast."""
    if not g.chromecast:
        return jsonify(chromecast=None)

    g.chromecast.stop()

    return jsonify()


@root.route('/forward')
def forward():
    """Seek forward through the media on the Chromecast."""
    if not g.chromecast:
        return jsonify(chromecast=None)

    g.chromecast.forward()

    return jsonify()


@root.route('/backward')
def backward():
    """Seek backward through the media on the Chromecast."""
    if not g.chromecast:
        return jsonify(chromecast=None)

    g.chromecast.backward()

    return jsonify()


@root.route('/media/<filename>')
def serve_media(filename):
    """Serves a media file via the 206 partial protocol."""
    path = '{}/{}'.format(current_app.config['MEDIA_PATH'], filename)
    return partial_file.send(path)
