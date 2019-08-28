# the builder

import logging
import pathlib
import shutil
import subprocess


log = logging.getLogger(__name__)


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


def execute_build(
    clone_path: pathlib.Path, machine_path: pathlib.Path, payload: dict
):
    machine_checkout_path = machine_path / 'checkout'
    if not machine_checkout_path.exists():
        shutil.copytree(clone_path, machine_checkout_path)
    log.debug("Starting build.")
    run_build_commands(machine_path=machine_path, clone_path=clone_path)
    log.debug("Build complete.")
