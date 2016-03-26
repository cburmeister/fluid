"""
A class representing a media file.
"""
from flask import url_for
import json
import omdb
import os
import requests
import logging


class Media(object):
    """A class representing a media file."""

    def __init__(self, filename):
        self.filename = filename
        self.pieces = filename.split('.')
        self.pieces.pop(-1)
        self.quality = self.pieces.pop(-1)
        self.year = self.pieces.pop(-1)
        self.query = ' '.join(self.pieces)

        self.data_path = 'app/static/tmp/{}.json'.format(self.filename)
        self.poster_path = 'app/static/tmp/{}.jpg'.format(self.filename)

        self.data = self.get_data()
        self.get_poster()

    @property
    def is_valid(self):
        return bool(self.data)

    def get_data(self):
        """Download information about the media via OMDB."""
        if not os.path.exists(self.data_path):
            logging.debug('Loading data on {}'.format(self.filename))

            response = omdb.request(t=self.query, y=self.year).json()
            if response['Response'] == 'True':
                with open(self.data_path, 'w') as f:
                    json.dump(response, f)
                return response
            else:
                logging.error(
                    'Unable to load data for {}'.format(self.filename))
                return {}

        with open(self.data_path) as f:
            return json.loads(f.read())

    def get_poster(self):
        """Download poster via IMDB."""
        if not os.path.exists(self.poster_path):
            if not self.data or self.data['Poster'] == 'N/A':
                logging.error(
                    'Unable to find poster for {}'.format(self.filename))
                return

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
                'cast': url_for('root.cast', filename=self.filename),
                'media': url_for(
                    'root.serve_media', filename=self.filename, _external=True
                ),
                'poster': url_for(
                    'static', filename='tmp/{}.jpg'.format(self.filename)
                ),
            }
        }
