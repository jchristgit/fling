import argparse
import ipaddress


def parse_bind_address(addr: str) -> (str, int):
    host, port = addr.rsplit(':', maxsplit=1)
    ipaddress.ip_address(host)  # raise ValueError when `host` is invalid
    return (host, int(port))


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
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
