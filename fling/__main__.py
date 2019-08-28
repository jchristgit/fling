import logging
import os
import socket
import socketserver

from .cli import make_parser
from .server import RequestHandler


logging.basicConfig(
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
)
log = logging.getLogger('fling')


if __name__ == '__main__':
    args = make_parser().parse_args()
    log_level = getattr(logging, args.log_level)
    log.setLevel(log_level)
    os.umask(0o077)

    # would much prefer to pass this in as arguments
    # but request handler needs to be a class due to
    # how socketserver works
    RequestHandler.gitea_token = args.gitea_token
    RequestHandler.trust = args.trust

    with socketserver.TCPServer(args.bind, RequestHandler) as server:
        server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        log.info("Starting HTTP on %s:%d.", *args.bind)
        server.serve_forever()
