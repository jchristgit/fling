import json
import logging
from http.server import BaseHTTPRequestHandler

from . import bob
from . import enums
from . import machine
from . import notifications
from . import settings
from . import workspace


log = logging.getLogger(__name__)


class RequestHandler(BaseHTTPRequestHandler):
    gitea_token: str
    trust: settings.Trust

    def do_POST(self):
        clean_path = self.path.strip('/')
        handler = self.routing_table.get(clean_path)
        if handler is not None:
            return handler(self)

        self.send_response(404)
        self.end_headers()

    def handle_post_hook_gitea(self):
        self.send_response(204)
        self.end_headers()

        payload = json.load(self.rfile)
        for commit in payload['commits']:
            def set_status(state, description):
                notifications.set_status(
                    build=bob.BuildResult(
                        state=state,
                        context='fling',
                        description=description
                    ),
                    repository_url=payload['repository']['html_url'],
                    repository_name=payload['repository']['full_name'],
                    commit=commit['id'],
                    gitea_token=self.gitea_token
                )

            # prepare git checkout
            set_status(enums.BuildState.PENDING, 'preparing workspace')
            clone_path = workspace.prepare(
                ssh_clone_url=payload['repository']['ssh_url'],
                full_name=payload['repository']['full_name'],
                commit=commit['id']
            )
            # load config
            set_status(enums.BuildState.PENDING, 'loading configuration')
            (result, config) = bob.load_build_config(
                repository_url=payload['repository']['html_url'],
                repository_name=payload['repository']['full_name'],
                commit=commit['id'],
                gitea_token=self.gitea_token,
                trust=self.trust
            )
            if result is not enums.BuildState.SUCCESS:
                # config is reason
                set_status(result, config)
                log.debug("Done with result %s: %s.", result, reason)
                return

            # prepare chroot
            set_status(enums.BuildState.PENDING, 'preparing chroot')
            machine_path = machine.prepare(
                commit=commit['id'],
                workspace=clone_path.parent,
                include_packages=config.get('fling', 'packages', fallback='')
            )

            # actually execute
            set_status(enums.BuildState.PENDING, 'running build')
            (result, reason) = bob.execute_build(
                clone_path=clone_path,
                machine_path=machine_path,
                trust=self.trust,
                gitea_token=self.gitea_token,
                payload=payload,
                commit=commit
            )

            set_status(enums.BuildState.PENDING, 'cleaning up')
            machine.cleanup(machine_path)

            set_status(result, reason)
            log.debug("Done with result %s: %s.", result, reason)


    routing_table = {
        'hook/gitea': handle_post_hook_gitea
    }
