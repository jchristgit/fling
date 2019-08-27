import argparse
import ipaddress

from . import __version__


def parse_bind_address(addr: str) -> (str, int):
    host, port = addr.rsplit(':', maxsplit=1)
    ipaddress.ip_address(host)  # raise ValueError when `host` is invalid
    return (host, int(port))


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog='fling'
    )
    parser.add_argument(
        '-V', '--version',
        action='version',
        version='%%(prog)s %s' % __version__
    )

    server_group = parser.add_argument_group('server options')
    server_group.add_argument(
        '-b', '--bind',
        type=parse_bind_address,
        help="colon-seperated address and port to bind the server on",
        default='127.0.0.1:5555'
    )
    server_group.add_argument(
        '-l', '--log-level',
        help="level to log at",
        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR'),
        default='INFO'
    )
    return parser
