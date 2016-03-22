"""
Runs the application server.
"""
import argparse
from app import init_app

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--debug', action='store_true', default=False)
parser.add_argument('--host', default='127.0.0.1')
parser.add_argument('--port', default='5000', type=int)
args = parser.parse_args()

app = init_app()
app.run(host=args.host, port=args.port, debug=args.debug)
