import json
import urllib.parse
import urllib.request

from . import bob


def commit_status_api_path(
    repository_url: str, repository_name: str, commit: str
) -> str:
    parsed = urllib.parse.urlparse(repository_url)
    return f'{parsed.scheme}://{parsed.netloc}/api/v1/repos/{repository_name}/statuses/{commit}'


def set_status(
    build: bob.BuildResult,
    repository_url: str,
    repository_name: str,
    commit: str,
    gitea_token: str
):
    url = commit_status_api_path(
        repository_url=repository_url,
        repository_name=repository_name,
        commit=commit
    )

    request = urllib.request.Request(
        url,
        data=json.dumps({
            'context': build.context,
            'description': build.description,
            'state': build.state.value,
            'target_url': '#'
        }).encode(),
        headers={
            'Authorization': f'token {gitea_token}',
            'Content-Type': 'application/json'
        }
    )
    urllib.request.urlopen(request)
