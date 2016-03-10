"""
List media from a directory and stream it to a Chromecast.
"""
from flask import Flask, flash, redirect, render_template, url_for
from media import Media
import mimetypes
import optparse
import os
import partial_file
import pychromecast
import time

app = Flask(__name__)
app.config.update({
    'CHROMECAST_NAME': os.environ['CHROMECAST_NAME'],
    'MEDIA_FORMATS': ('.mp4', '.mkv'),
    'MEDIA_PATH': os.environ['MEDIA_PATH'],
    'SECRET_KEY': os.environ['SECRET_KEY'],
})

chromecast = None  # Global containing a connection to the Chromecast device


@app.route('/')
def index():
    """Returns all media within the directory."""
    media = os.listdir(app.config['MEDIA_PATH'])
    media = filter(lambda x: x.endswith(app.config['MEDIA_FORMATS']), media)
    media = [Media(x) for x in media]
    media = [x.to_dict() for x in media]

    global chromecast
    if not chromecast:
        chromecast = pychromecast.get_chromecast(
            friendly_name=app.config['CHROMECAST_NAME']
        )
        if not chromecast:
            flash('Chromecast not found.', 'error')

    now_playing = None
    is_paused = False

    if chromecast:
        if chromecast.is_idle:
            flash('Chromecast is idle.', 'info')

        chromecast.wait()
        media_controller = chromecast.media_controller

        if media_controller.is_paused or media_controller.is_playing:
            is_paused = media_controller.is_paused

            filename = media_controller.status.content_id.split('/')[-1]
            now_playing = Media(filename).to_dict()

    return render_template(
        'index.html',
        is_paused=is_paused,
        media=media,
        now_playing=now_playing,
    )


@app.route('/cast/<filename>')
def cast(filename):
    """Casts the filename to a chromecast."""
    global chromecast
    if not chromecast:
        chromecast = pychromecast.get_chromecast(
            friendly_name=app.config['CHROMECAST_NAME']
        )
        if not chromecast:
            flash('Chromecast not found.', 'error')
            return redirect(url_for('index'))

    media = Media(filename)
    mimetype, _ = mimetypes.guess_type(filename)
    chromecast.media_controller.play_media(media['urls']['media'], mimetype)

    time.sleep(6)

    return redirect(url_for('index'))


@app.route('/play')
def play():
    """Resumes playback of the media on the Chromecast."""
    global chromecast
    if not chromecast:
        chromecast = pychromecast.get_chromecast(
            friendly_name=app.config['CHROMECAST_NAME']
        )
        if not chromecast:
            flash('Chromecast not found.', 'error')
            return redirect(url_for('index'))

    chromecast.media_controller.play()

    time.sleep(1)

    return redirect(url_for('index'))


@app.route('/pause')
def pause():
    """Pauses playback of the media on the Chromecast."""
    global chromecast
    if not chromecast:
        chromecast = pychromecast.get_chromecast(
            friendly_name=app.config['CHROMECAST_NAME']
        )
        if not chromecast:
            flash('Chromecast not found.', 'error')
            return redirect(url_for('index'))

    chromecast.media_controller.pause()

    time.sleep(1)

    return redirect(url_for('index'))


@app.route('/stop')
def stop():
    """Stops playback of the media on the Chromecast."""
    global chromecast
    if not chromecast:
        chromecast = pychromecast.get_chromecast(
            friendly_name=app.config['CHROMECAST_NAME']
        )
        if not chromecast:
            flash('Chromecast not found.', 'error')
            return redirect(url_for('index'))

    chromecast.media_controller.stop()

    time.sleep(1)

    return redirect(url_for('index'))


@app.route('/media/<filename>')
def media(filename):
    """Serves a media file via the 206 partial protocol."""
    path = '{}/{}'.format(app.config['MEDIA_PATH'], filename)
    return partial_file.send(path)


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('--host', default='127.0.0.1')
    parser.add_option('--port', default='5000', type=int)
    options, _ = parser.parse_args()
    app.run(
        host=options.host,
        port=options.port,
        debug=True,
        threaded=True
    )
