import json
import multiprocessing
import pathlib
import random
import socketserver
import sys
import tempfile
import unittest
import urllib.error
import urllib.request

from fling import server


def start_server_process(server):
    if pathlib.Path('testserver.log').exists():
        path = 'testserver.log'
    else:
        (path, _) = tempfile.mkstemp(prefix='fling')

    with open(path, 'a+') as outfile:
        # when the cake speaks,
        # the crumb is silent
        sys.stdout = outfile
        sys.stderr = outfile
        server.serve_forever()


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.bindaddr = ('127.0.0.1', random.randrange(1_000, 50_000))
        self.url = 'http://%s:%d' % self.bindaddr
        self.server = socketserver.TCPServer(
            self.bindaddr, server.RequestHandler
        )
        self.process = multiprocessing.Process(
            name='fling test suite: http server',
            target=start_server_process,
            args=(self.server,)
        )
        self.process.start()

    def test_returns_404_on_post_unknown_routes(self):
        request = urllib.request.Request(self.url, method='POST')
        with self.assertRaises(urllib.error.HTTPError) as cm:
            response = urllib.request.urlopen(request)

        self.assertEqual(cm.exception.status, 404)

    def test_returns_204_on_gitea_hook_route(self):
        request = urllib.request.Request(
            self.url + '/hook/gitea',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'commits': []}).encode(),
            method='POST'
        )
        response = urllib.request.urlopen(request)
        self.assertEqual(response.getcode(), 204)
        self.assertEqual(response.read(), b"")

    def tearDown(self):
        self.process.terminate()
        self.server.server_close()
