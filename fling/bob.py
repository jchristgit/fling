# the builder

import base64
import configparser
import dataclasses
import json
import logging
import pathlib
import shutil
import subprocess
import typing
import urllib.error
import urllib.parse
import urllib.request

from . import enums
from . import settings


log = logging.getLogger(__name__)


@dataclasses.dataclass
class BuildResult:
    state: enums.BuildState
    context: str
    description: str


def run_build_commands(
    machine_path: pathlib.Path,
    clone_path: pathlib.Path,
    commands: str
):
    process = subprocess.run(
        [
            'systemd-nspawn',
            '--ephemeral',
            '--quiet',
            '--directory', str(machine_path),
            '/bin/bash', '-c',
            f"""
            set -eu
            cd /checkout
            set -x

            {commands}
            """
        ]
    )
    if process.returncode == 0:
        return (enums.BuildState.SUCCESS, 'build completed successfully')
    return (enums.BuildState.FAILED, f'build failed with rc {process.returncode}')


def load_build_config(
    repository_url: str,
    repository_name: str,
    commit: str,
    gitea_token: str,
    trust: settings.Trust
) -> typing.Tuple[enums.BuildState, typing.Union[str, configparser.ConfigParser]]:
    parsed = urllib.parse.urlparse(repository_url)
    endpoint = (
        f'{parsed.scheme}://{parsed.netloc}'
        f'/api/v1/repos/{repository_name}/contents/.fling.ini'
    )

    if trust == settings.Trust.EVERYONE:
        endpoint += f'?ref={commit}'

    request = urllib.request.Request(
        endpoint,
        headers={'Authorization': f'token {gitea_token}'}
    )

    try:
        response = urllib.request.urlopen(request)
        data = json.load(response)
        parser = configparser.ConfigParser()
        parser.read_string(
            base64.b64decode(data['content'].encode()).decode(),
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
    commit: str,
    commands: str,
) -> typing.Tuple[enums.BuildState, str]:
    machine_checkout_path = machine_path / 'checkout'
    if not machine_checkout_path.exists() or commit == '<unknown>':

        if commit == '<unknown>' and machine_checkout_path.exists():
            shutil.rmtree(machine_checkout_path)

        log.debug("Copying source tree into machine checkout path.")
        subprocess.run(
            [
                'cp',
                '--archive',
                '--reflink=auto',
                clone_path,
                machine_checkout_path
            ],
            check=True
        )

    log.debug("Starting build.")
    (status, reason) = run_build_commands(
        machine_path=machine_path,
        clone_path=clone_path,
        commands=commands,
    )

    log.debug("Build complete.")
    return (status, reason)
