import argparse
import unittest

from fling import cli


class CLITests(unittest.TestCase):
    def test_parse_bind_address_for_valid_addresses(self):
        self.assertEqual(
            cli.parse_bind_address('127.0.0.1:1234'),
            ('127.0.0.1', 1234)
        )
        self.assertEqual(
            # IPv6 loopback
            cli.parse_bind_address('::1:1234'),
            ('::1', 1234)
        )

    def test_parse_bind_address_for_invalid_addresses(self):
        with self.assertRaises(ValueError):
            cli.parse_bind_address('foo:555')

    def test_make_parser(self):
        self.assertIsInstance(cli.make_parser(), argparse.ArgumentParser)
