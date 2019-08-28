import logging
import pathlib
import string
import subprocess


log = logging.getLogger(__name__)


def ensure_clean_name(name: str):
    if any(
        c not in (string.ascii_letters + string.digits + '_')
        for c in name
    ):
        raise ValueError("unclean name: %r" % (name,))


def machine_exists(name: str):
    result = subprocess.run(
        ['sudo', 'machinectl', 'show-image', name],
        capture_output=True
    )
    return result.returncode == 0


def prepare(
    name: str, commit: str, suite: str = 'stable',
    root: pathlib.Path = pathlib.Path('/var/lib/machines')
) -> str:
    clean_name = name.replace('/', '_')
    ensure_clean_name(clean_name)

    template_machine_name = 'fling_' + clean_name

    if not machine_exists(template_machine_name):
        template_machine_path = root / template_machine_name
        log.debug("Creating template machine at `%s`.", template_machine_path)
        subprocess.run(
            [
                'sudo',
                'debootstrap',
                '--include=systemd-container',
                suite,
                template_machine_path
            ],
            check=True
        )
        subprocess.run(
            ['sudo', 'machinectl', '--quiet', 'read-only', template_machine_name, 'true'],
            capture_output=True
        )
        log.debug("Template machine ready.")

    build_machine_name = template_machine_name + '_' + commit
    subprocess.run(
        [
            'sudo', 'machinectl', '--quiet', 'clone',
            template_machine_name, build_machine_name
        ],
        check=True
    )
    log.debug("Build machine ready.")
    return build_machine_name
