"""
A wrapper around pychromecast for interacting with a Chromecast device.
"""
import pychromecast
import time


class Chromecast(object):
    """An object for interacting with a Chromecast device."""

    def __init__(self, host):
        """Initialize the Chromecast."""
        self.host = host
        self.connection = self.connect()

    def connect(self):
        """Returns a connection to the Chromecast."""
        try:
            connection = pychromecast.Chromecast(self.host)
        except:
            return

        if not connection:
            return

        connection.wait()
        time.sleep(1)

        return connection

    def disconnect(self):
        """Disconnects from the Chromecast."""
        if not self.connection:
            return

        self.connection.disconnect(blocking=False)

    def cast(self, url, mimetype):
        """Cast the url to the chromecast."""
        self.connection.media_controller.play_media(url, mimetype)

    def play(self):
        """Resume playback of the media on the Chromecast."""
        self.connection.media_controller.play()

    def pause(self):
        """Pause playback of the media on the Chromecast."""
        self.connection.media_controller.pause()

    def stop(self):
        """Stop playback of the media on the Chromecast."""
        self.connection.media_controller.stop()
        self.connection.quit_app()

    def forward(self):
        """Seek forward through the media on the Chromecast."""
        status = self.connection.media_controller.status
        self.connection.media_controller.seek(
            status.current_time + (status.duration / 20)
        )

    def backward(self):
        """Seek backward through the media on the Chromecast."""
        status = self.connection.media_controller.status
        self.connection.media_controller.seek(
            status.current_time - (status.duration / 20)
        )
