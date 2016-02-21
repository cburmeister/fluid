"""
A class representing a media file.
"""
from flask import url_for
import json
import omdb
import os
import requests


class Media(object):
    """A class representing a media file."""

    def __init__(self, filename):
        self.filename = filename
        self.pieces = filename.split('.')
        self.pieces.pop(-1)
        self.quality = self.pieces.pop(-1)
        self.year = self.pieces.pop(-1)
        self.query = ' '.join(self.pieces)

        self.data_path = 'static/tmp/{}.json'.format(self.filename)
        self.poster_path = 'static/tmp/{}.jpg'.format(self.filename)

        self.data = self.get_data()
        self.get_poster()

    def get_data(self):
        """Download information about the media via OMDB."""
        if not os.path.exists(self.data_path):
            response = omdb.request(t=self.query, y=self.year)
            if response.status_code == 200:
                data = response.json()
                with open(self.data_path, 'w') as f:
                    json.dump(data, f)
                return data

        with open(self.data_path) as f:
            return json.loads(f.read())

    def get_poster(self):
        """Download poster via IMDB."""
        if not os.path.exists(self.poster_path):
            response = requests.get(self.data['Poster'], stream=True)
            if response.status_code == 200:
                with open(self.poster_path, 'wb') as f:
                    for chunk in response:
                        f.write(chunk)

    def to_dict(self):
        """Return a dictionary representation of the media."""
        return {
            'filename': self.filename,
            'title': self.data['Title'],
            'urls': {
                'poster': self.poster_path,
                'cast': url_for('cast', filename=self.filename),
            }
        }
