import logging
import pathlib
import string
import subprocess
import urllib.parse


log = logging.getLogger(__name__)


def ensure_clean_name(name: str):
    if any(c not in (string.ascii_letters + string.digits) for c in name):
        raise ValueError("unclean name: %r" % (name,))


def path_for(
    full_url: str, full_name: str,
    root: pathlib.Path = pathlib.Path(__file__).parent.parent
) -> pathlib.Path:
    parsed = urllib.parse.urlparse(full_url)
    clone_name, *_ = parsed.netloc.split(':')  # drop ports
    *_user, hostname = clone_name.split('@')
    owner, project = full_name.split('/')
    ensure_clean_name(owner)
    ensure_clean_name(project)
    return root / 'workspace' / hostname / owner / project


def prepare_checkout(clone_path: str, ssh_clone_url: str, commit: str):
    if not clone_path.exists():
        subprocess.run(
            ['git', 'clone', '--quiet', ssh_clone_url, clone_path],
            check=True
        )
    else:
        subprocess.run(
            ['git', 'fetch', '--quiet', '--all'],
            check=True, cwd=clone_path
        )

    subprocess.run(['git', 'checkout', '--quiet', commit])


def prepare(
    ssh_clone_url: str, full_name: str, commit: str,
    root: pathlib.Path = pathlib.Path(__file__).parent.parent,
):
    path = path_for(full_url=ssh_clone_url, full_name=full_name, root=root)
    log.debug("Preparing workspace at `%s`.", path)
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    prepare_checkout(
        clone_path=path / 'repo',
        ssh_clone_url=ssh_clone_url,
        commit=commit
    )
    log.debug("Workspace ready.")
