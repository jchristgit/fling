import pathlib
import unittest

from fling import workspace


class WorkspaceTests(unittest.TestCase):
    def test_ensure_clean_name_ok_for_valid_names(self):
        self.assertIsNone(workspace.ensure_clean_name("foo"))
        self.assertIsNone(workspace.ensure_clean_name("123"))
        self.assertIsNone(workspace.ensure_clean_name("foobar441"))

    def test_ensure_clean_name_raises_for_invalid_names(self):
        for name in ('%%%§§§§§§', 'hello/world', '../../../hello'):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    workspace.ensure_clean_name(name)

    def test_path_for_valid_names(self):
        self.assertEqual(
            workspace.path_for(
                full_url='https://git.example.com:443/subpath/owner/project',
                full_name='myname/myproject',
                root=pathlib.Path('/fling-tests/')
            ),
            (
                pathlib.Path('/fling-tests') / 'workspace'
                / 'git.example.com' / 'myname' / 'myproject'
            )
        )

    def test_default_workspace_path(self):
        self.assertEqual(
            workspace.path_for(
                full_url='https://git.example.com:443/subpath/owner/project',
                full_name='myname/myproject'
            ),
            (
                pathlib.Path(__file__).parent.parent / 'workspace'
                / 'git.example.com' / 'myname' / 'myproject'
            )
        )

