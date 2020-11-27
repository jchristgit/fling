# One-off build management.

import configparser
import logging
import pathlib

from . import bob
from . import enums
from . import machine
from . import settings


log = logging.getLogger(__name__)


def local_execute(path: pathlib.Path, workspace: pathlib.Path) -> int:
    config = configparser.ConfigParser()
    fling_config = path / '.fling.ini'
    config.read_string(fling_config.read_text())

    log.info("Preparing machine in workspace %s.", workspace)
    machine_path = machine.prepare(
        commit='<unknown>',
        workspace=workspace,
        include_packages=config.get('fling', 'packages', fallback='')
    )

    log.info("Starting build.")
    (result, reason) = bob.execute_build(
        clone_path=path,
        machine_path=machine_path,
        trust=settings.Trust.MAINTAINERS,
        gitea_token='<unknown>',
        payload={},
        commit='<unknown>',
        commands=config.get('fling', 'commands')
    )

    if result is enums.BuildState.SUCCESS:
        log.info("Build finished successfully.")
        return 0
    else:
        log.error("Build failed: %r.", reason)
        return 1
