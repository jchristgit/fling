import logging
import pathlib
import shutil
import string
import subprocess

from . import workspace


log = logging.getLogger(__name__)


def ensure_clean_name(name: str):
    if any(
        c not in (string.ascii_letters + string.digits + '_')
        for c in name
    ):
        raise ValueError("unclean name: %r" % (name,))


def prepare(
        commit: str, workspace: str,
        packages: str, suite: str = 'stable',
) -> str:
    template_machine_path = workspace / 'machines' / 'template'
    if not template_machine_path.exists():
        log.debug("Creating template chroot at `%s`.", template_machine_path)
        subprocess.run(
            [
                'fakechroot',
                'fakeroot',
                'debootstrap',
                '--variant=minbase',
                f'--include={packages}',
                suite,
                template_machine_path
            ],
            check=True
        )
        log.debug("Template chroot ready.")

    build_machine_path = workspace / 'machines' / commit
    if not build_machine_path.exists():
        subprocess.run(
            [
                'cp', '--archive',
                '--reflink=auto',
                template_machine_path,
                build_machine_path
            ],
            check=True
        )
        log.debug("Build chroot ready.")

    return build_machine_path


def cleanup(machine_path: pathlib.Path):
    shutil.rmtree(machine_path)
    log.debug("Cleaned up machine at `%s`.", machine_path)
