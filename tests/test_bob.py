import pathlib
import unittest
import unittest.mock

from fling import bob
from fling import enums


class BobTestCase(unittest.TestCase):
    @unittest.mock.patch('subprocess.run')
    def test_run_build_commands_on_success(self, subprocess_run):
        subprocess_run.return_value = unittest.mock.MagicMock()
        subprocess_run.return_value.returncode = 0

        machine_path = pathlib.Path('machine') / 'path'
        clone_path = pathlib.Path('clone') / 'path'
        commands = 'false'
        (state, reason) = bob.run_build_commands(
            machine_path=machine_path,
            clone_path=clone_path,
            commands=commands
        )
        bash_cmdline = (
            f"""
            set -eu
            cd /checkout
            set -x

            {commands}
            """
        )

        self.assertIs(state, enums.BuildState.SUCCESS)
        self.assertEqual(reason, 'build completed successfully')
        subprocess_run.assert_called_once_with(
            [
                'systemd-nspawn',
                '--ephemeral',
                '--quiet',
                '--directory', str(machine_path),
                '/bin/bash', '-c',
                bash_cmdline
            ]
        )

    @unittest.mock.patch('subprocess.run')
    def test_run_build_commands_on_failure(self, subprocess_run):
        machine_path = pathlib.Path('machine') / 'path'
        clone_path = pathlib.Path('clone') / 'path'
        commands = 'false'
        subprocess_run.return_value = unittest.mock.MagicMock()

        # triple quote string indent matches the indentation of
        # the code it's part of
        # a brilliant decision for a language wmaking use of extensive indents
        bash_cmdline = (
            f"""
            set -eu
            cd /checkout
            set -x

            {commands}
            """
        )

        for rc in (1, 5, 255):
            with self.subTest(rc=rc):
                subprocess_run.return_value.returncode = rc

                (state, reason) = bob.run_build_commands(
                    machine_path=machine_path,
                    clone_path=clone_path,
                    commands=commands
                )

                self.assertIs(state, enums.BuildState.FAILED)
                self.assertEqual(reason, f'build failed with rc {rc}')
                subprocess_run.assert_called_once_with(
                    [
                        'systemd-nspawn',
                        '--ephemeral',
                        '--quiet',
                        '--directory', str(machine_path),
                        '/bin/bash', '-c',
                        bash_cmdline
                    ]
                )
                subprocess_run.reset_mock()
