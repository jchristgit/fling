import json
from http.server import BaseHTTPRequestHandler

from . import bob
from . import machine
from . import workspace


class RequestHandler(BaseHTTPRequestHandler):
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
            # prepare git checkout
            clone_path = workspace.prepare(
                ssh_clone_url=payload['repository']['ssh_url'],
                full_name=payload['repository']['full_name'],
                commit=commit['id']
            )
            # prepare chroot
            machine_path = machine.prepare(
                commit=commit['id'],
                workspace=clone_path.parent
            )
            bob.execute_build(
                clone_path=clone_path,
                machine_path=machine_path,
                payload=payload
            )
            machine.cleanup(machine_path)


    routing_table = {
        'hook/gitea': handle_post_hook_gitea
    }
