# the builder

import configparser
import dataclasses
import logging
import pathlib
import shutil
import subprocess
import typing
import urllib.error
import urllib.request
import urllib.parse

from . import enums
from . import settings


log = logging.getLogger(__name__)


@dataclasses.dataclass
class Build:
    state: enums.BuildState
    context: str
    description: str


def run_build_commands(machine_path: pathlib.Path, clone_path: pathlib.Path):
    subprocess.run(
        [
            'fakeroot', 'fakechroot',
            'chroot', machine_path,
            'bash', '-c',
            f"""
            set -eu
            cd /checkout
            set -x

            apt-get install -y python3
            python3 -m unittest
            whoami
            echo $HOME
            """
        ],
        check=True,
    )


def load_build_config(
    repository_url: str,
    repository_name: str,
    commit: str,
    gitea_token: str,
    trust: settings.Trust
) -> (enums.BuildState, typing.Union[str, configparser.ConfigParser]):
    parsed = urllib.parse.urlparse(repository_url)
    endpoint = f'{parsed.scheme}://{parsed.netloc}/api/v1/repos/{repository_name}/contents/.fling.ini'

    if trust == settings.Trust.EVERYONE:
        endpoint += f'?ref={commit}'

    request = urllib.request.Request(
        endpoint,
        headers={'Authorization': f'Token {gitea_token}'}
    )

    try:
        response = urllib.request.urlopen(request)
        data = json.load(response)
        parser = configparser.ConfigParser()
        parser.read_string(
            data['content'],
            source=f'.fling.ini@{repository_name}'
        )
        return (enums.BuildState.SUCCESS, parser)

    except urllib.error.HTTPError as err:
        return (
            enums.BuildState.ERROR, 
            f'got unexpected status {err.getcode()} trying to load build config'
        )


def execute_build(
    clone_path: pathlib.Path,
    machine_path: pathlib.Path,
    trust: settings.Trust,
    gitea_token: str,
    payload: dict,
    commit: str
) -> Build:
    machine_checkout_path = machine_path / 'checkout'
    if not machine_checkout_path.exists():
        shutil.copytree(clone_path, machine_checkout_path)

    log.debug("Starting build.")
    (status, config) = load_build_config(
        repository_url=payload['repository']['html_url'],
        repository_name=payload['repository']['full_name'],
        commit=commit,
        gitea_token=gitea_token,
        trust=trust
    )

    if status is not enums.BuildState.SUCCESS:
        return (status, config)

    (status, reason) = run_build_commands(
        machine_path=machine_path,
        clone_path=clone_path,
        config=config,
    )

    log.debug("Build complete.")
    return (status, reason)
