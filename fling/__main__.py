import logging
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

    with socketserver.TCPServer(args.bind, RequestHandler) as server:
        # doesn't work
        # server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        log.info("Starting HTTP on %s:%d.", *args.bind)
        server.serve_forever()
