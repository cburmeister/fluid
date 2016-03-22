"""
A wrapper around Flask's send_file implementing the 206 partial protocol.
"""
from flask import Response, request, send_file
import mimetypes
import os
import re


def send(path):
    """Returns a file via the 206 partial protocol."""
    range_header = request.headers.get('Range', None)
    if not range_header:
        return send_file(path)  # Client must want the entire file

    size = os.path.getsize(path)
    start, end = 0, None

    m = re.search('(\d+)-(\d*)', range_header)
    g = m.groups()

    if g[0]:
        start = int(g[0])
    if g[1]:
        end = int(g[1])

    length = min(size - start, 5120000)
    if end is not None:
        length = end - start

    data = None
    with open(path, 'rb') as f:
        f.seek(start)
        data = f.read(length)

    mimetype, _ = mimetypes.guess_type(path)

    rv = Response(data, 206, mimetype=mimetype, direct_passthrough=True)
    rv.headers.add('Accept-Ranges', 'bytes')
    rv.headers.add(
        'Content-Range', 'bytes {0}-{1}/{2}'.format(
            start, start + length - 1, size
        )
    )
    return rv
