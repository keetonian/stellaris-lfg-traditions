"""scripts/install.sh tests: local installs are labelled [LOCAL DEV] and unlinked from Steam; RELEASE=1 is exact."""
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DESCRIPTOR = REPO / "mod/descriptor.mod"


@unittest.skipUnless(shutil.which("rsync"), "rsync not available")
class InstallTests(unittest.TestCase):
    def setUp(self):
        self.mods = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.mods)
        self.repo_descriptor = DESCRIPTOR.read_text()
        self.name = re.search(r'^name="(.*)"', self.repo_descriptor, re.M).group(1)

    def install(self, **env):
        subprocess.run(["bash", str(REPO / "scripts/install.sh")], check=True, capture_output=True,
                       env=dict(os.environ, STELLARIS_MOD_DIR=str(self.mods), **env))
        return (self.mods / "lfg_traditions.mod").read_text(), (self.mods / "lfg_traditions/descriptor.mod").read_text()

    def test_dev_install_is_labelled_and_unlinked(self):
        launcher, installed = self.install()
        for text in (launcher, installed):
            self.assertIn(f'name="[LOCAL DEV] {self.name}"', text)
            self.assertNotIn("remote_file_id=", text)
        self.assertIn(f'path="{self.mods / "lfg_traditions"}"', launcher)
        self.assertEqual((self.mods / "lfg_traditions/common/traditions/lfg_traditions.txt").read_bytes(),
                         (REPO / "mod/common/traditions/lfg_traditions.txt").read_bytes())

    def test_release_install_is_exact(self):
        launcher, installed = self.install(RELEASE="1")
        self.assertEqual(installed, self.repo_descriptor)
        self.assertTrue(launcher.startswith(self.repo_descriptor))

    def test_repo_descriptor_untouched(self):
        self.install()
        self.install(RELEASE="1")
        self.assertEqual(DESCRIPTOR.read_text(), self.repo_descriptor)


if __name__ == "__main__":
    unittest.main()
