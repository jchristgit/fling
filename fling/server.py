from http.server import BaseHTTPRequestHandler


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

    routing_table = {
        'hook/gitea': handle_post_hook_gitea
    }
