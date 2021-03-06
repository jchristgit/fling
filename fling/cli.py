import argparse
import ipaddress
import pathlib
import typing

from . import __version__
from . import settings


def parse_bind_address(addr: str) -> typing.Tuple[str, int]:
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
    parser.add_argument(
        '-l', '--log-level',
        help="level to log at",
        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR'),
        default='INFO'
    )

    subparsers = parser.add_subparsers(
        dest='subcommand',
        required=True,
        help="function to perform"
    )

    build_parser = subparsers.add_parser('build', help="run a build locally")
    build_parser.add_argument(
        '-w',
        '--workspace',
        help="base directory where to store files",
        default=pathlib.Path('/var/lib/fling'),
        type=pathlib.Path,
    )

    server_parser = subparsers.add_parser('server', help="run the web server")

    security_group = server_parser.add_argument_group('security options')
    security_group.add_argument(
        '--trust',
        help=(
            "which configuration file to use on builds: 'maintainers' to load "
            "it from the default branch, 'everyone' to load it from the "
            "commit the build is performed for"
        ),
        choices=tuple(settings.Trust),
        type=settings.Trust,
        default=settings.Trust.MAINTAINERS
    )

    server_group = server_parser.add_argument_group('server options')
    server_group.add_argument(
        '-b', '--bind',
        type=parse_bind_address,
        help="colon-seperated address and port to bind the server on",
        default='127.0.0.1:5555'
    )
    server_group.add_argument(
        '-t', '--gitea-token',
        help="gitea API token"
    )

    return parser
