import hashlib
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


def shasum_from_packages(packages: str) -> str:
    return hashlib.sha512(packages.encode()).hexdigest()


def template_up_to_date(machine_path: str, include_packages: str):
    shasum_path = machine_path / '.fling-shasums'
    return (
        shasum_path.exists()
        and shasum_path.read_text() == shasum_from_packages(include_packages)
    )


def prepare(
        commit: str, workspace: str,
        include_packages: str, suite: str = 'stable',
) -> str:
    template_machine_path = workspace / 'machines' / 'template'
    if not template_up_to_date(template_machine_path, include_packages):
        log.debug("Creating template chroot at `%s`.", template_machine_path)
        shutil.rmtree(template_machine_path, ignore_errors=True)
        subprocess.run(
            [
                'fakechroot',
                'fakeroot',
                'debootstrap',
                '--variant=minbase',
                f'--include={include_packages}',
                suite,
                template_machine_path
            ],
            check=True
        )

        with open(template_machine_path / '.fling-shasums', 'w+') as f:
            f.write(shasum_from_packages(include_packages))

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
