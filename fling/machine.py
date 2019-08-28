import logging
import pathlib
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
        suite: str = 'stable',
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
                '--include=fakeroot',
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
