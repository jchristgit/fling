import unittest

from fling import notifications


class NotificationTests(unittest.TestCase):
    """Tests the notifications module."""

    def test_commit_status_api_path(self):
        self.assertEqual(
            notifications.commit_status_api_path(
                repository_url='https://git.example.com/foo/bar/baz',
                repository_name='owner/project',
                commit='abcdef'
            ),
            'https://git.example.com/api/v1/repos/owner/project/statuses/abcdef'
        )
