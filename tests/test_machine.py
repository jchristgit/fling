import hashlib
import logging
import pathlib
import shutil
import tempfile
import unittest
import unittest.mock

from fling import machine


class MachineTests(unittest.TestCase):
    def test_shasum_from_packages(self):
        self.assertEqual(
            machine.shasum_from_packages('python3'),
            hashlib.sha512(b'python3').hexdigest()
        )

    @unittest.mock.patch('shutil.rmtree')
    def test_cleanup_dry(self, patch):
        path = '/some/test/path'
        machine.cleanup(path)
        patch.assert_called_once_with(path)

    @unittest.mock.patch('fling.machine.template_up_to_date')
    def test_prepare_dry(self, patch):
        patch.return_value = True
        workspace = pathlib.Path('/workspace')
        self.assertEqual(
            machine.prepare(
                commit='some-commit',
                workspace=workspace,
                include_packages='foobar'
            ),
            workspace / 'machines' / 'template'
        )
        patch.assert_called_once_with(
            workspace / 'machines' / 'template',
            'foobar'
        )


class MachinePrepareSteps(unittest.TestCase):
    def setUp(self):
        self.dir = pathlib.Path(tempfile.mkdtemp(prefix='fling-tests'))
        self.machine_path = self.dir / 'machines' / 'template'
        self.file = self.machine_path / '.fling-shasums'
        self.machine_path.mkdir(parents=True)

    def test_template_is_up_to_date_for_correct_shasums(self):
        packages = 'python3'
        self.file.write_text(hashlib.sha512(packages.encode()).hexdigest())

        self.assertEqual(
            machine.prepare(
                commit='some-commit',
                workspace=self.dir,
                include_packages=packages
            ),
            self.machine_path
        )

    @unittest.mock.patch('shutil.rmtree')
    @unittest.mock.patch('subprocess.run')
    def test_rebuilds_template_when_shasums_outdated(self, subprocess_run, rmtree):
        with self.assertLogs('fling.machine', level=logging.DEBUG) as cm:
            self.assertEqual(
                machine.prepare(
                    commit='some-commit',
                    workspace=self.dir,
                    include_packages='python3'
                ),
                self.machine_path
            )

        rmtree.assert_called_once_with(
            self.machine_path,
            ignore_errors=True
        )
        subprocess_run.assert_called_once_with(
            ['debootstrap', '--include=python3', 'stable', str(self.machine_path)],
            check=True
        )

        [record_a, record_b] = cm.records
        self.assertEqual(
            record_a.message,
            f"Creating template chroot at `{self.machine_path}`."
        )
        self.assertEqual(record_b.message, "Template chroot ready.")

    def tearDown(self):
        if self.file.exists():
            self.file.unlink()
        shutil.rmtree(self.dir)

class MachineUpToDateTests(unittest.TestCase):
    def setUp(self):
        self.dir = pathlib.Path(tempfile.mkdtemp(prefix='fling-tests'))
        self.file = self.dir / '.fling-shasums'

    def test_raises_for_non_existing_template(self):
        path = pathlib.Path('foo') / 'bar' / 'baz'
        self.assertFalse(machine.template_up_to_date(path, 'abc'))

    def test_returns_false_for_wrong_shasums(self):
        self.file.write_text('sum')
        self.assertFalse(machine.template_up_to_date(self.file, 'def'))

    def test_returns_true_for_correct_shasums(self):
        self.file.write_text(hashlib.sha512(b'python3').hexdigest())
        self.assertFalse(machine.template_up_to_date(self.file, 'python3'))

    def tearDown(self):
        if self.file.exists():
            self.file.unlink()
        self.dir.rmdir()


class MachineCleanupTests(unittest.TestCase):
    def setUp(self):
        self.dir = pathlib.Path(tempfile.mkdtemp(prefix='fling-tests'))
        self.file = pathlib.Path(self.dir) / 'test-file'
        self.file.write_bytes(b'ed, man! man, ed')
        self.assertTrue(self.file.exists())

    def test_cleanup_removes_contents(self):
        with self.assertLogs('fling.machine', level=logging.DEBUG) as cm:
            machine.cleanup(self.dir)

        [record] = cm.records
        self.assertEqual(
            record.message,
            f"Cleaned up machine at `{self.dir}`."
        )
        self.assertFalse(self.file.exists())
        self.assertFalse(self.dir.exists())

    def tearDown(self):
        if self.file.exists():
            self.file.unlink()

        if self.dir.exists():
            self.dir.rmdir()
