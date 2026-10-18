"""scripts/publish.sh tests (DRY_RUN only; nothing is uploaded).

publish.sh runs check_mod.py --require-sources, so these need the installed game + Gigastructural (skipped in CI).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import check_mod  # noqa: E402

GAME_INSTALLED = check_mod.DEFAULT_GAME.exists() and check_mod.DEFAULT_GIGA.exists()


@unittest.skipUnless(GAME_INSTALLED, "Stellaris + Gigastructural not installed")
@unittest.skipUnless(shutil.which("rsync"), "rsync not available")
class PublishDryRunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.mod = self.tmp / "mod"
        shutil.copytree(REPO / "mod", self.mod)
        # Start from a never-published descriptor; tests that need an id add one.
        descriptor = self.mod / "descriptor.mod"
        descriptor.write_text("".join(line for line in descriptor.read_text().splitlines(keepends=True)
                                      if not line.startswith("remote_file_id=")))
        self.desc = self.tmp / "desc.txt"
        self.desc.write_text('Use "this" not "that".\nPath C:\\mods\\ and a lone " quote.\n', encoding="utf-8")

    def publish(self, *args, **env):
        full_env = dict(os.environ, DRY_RUN="1", ALLOW_DIRTY="1", PUBLISH_SKIP_TESTS="1",
                        MOD_DIR=str(self.mod), DESCRIPTION_FILE=str(self.desc))
        full_env.pop("STEAM_USER", None)
        full_env.update(env)
        return subprocess.run(["bash", str(REPO / "scripts/publish.sh"), *args], env=full_env,
                              capture_output=True, text=True)

    def vdf(self, out):
        return out[out.index('"workshopitem"'):]

    def test_dry_run_writes_valid_vdf(self):
        res = self.publish('note "quoted"')
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        vdf = self.vdf(res.stdout)
        # steamcmd's VDF parser has no escapes: the only `"` allowed are the ones delimiting keys/values.
        keys = len(re.findall(r'^\t"[a-z]+"\t+"', vdf, re.M))
        self.assertGreaterEqual(keys, 7)
        self.assertEqual(vdf.count('"'), 2 + 4 * keys, vdf)
        self.assertIn("Use “this” not “that”.", vdf)
        self.assertIn('"note “quoted”"', vdf)
        self.assertIn("C:\\mods\\", vdf)

    def test_new_item_is_private_with_title_and_description(self):
        vdf = self.vdf(self.publish().stdout)
        self.assertIn('"publishedfileid"\t"0"', vdf)
        self.assertIn('"visibility"\t"2"', vdf)
        self.assertIn('"title"\t\t"LFG Traditions"', vdf)
        self.assertIn('"description"', vdf)

    def test_update_syncs_description_but_keeps_title_and_visibility(self):
        with open(self.mod / "descriptor.mod", "a") as f:
            f.write('remote_file_id="123456"\n')
        vdf = self.vdf(self.publish().stdout)
        self.assertIn('"publishedfileid"\t"123456"', vdf)
        self.assertIn('"description"', vdf)
        for key in ('"title"', '"visibility"'):
            self.assertNotIn(key, vdf)

    def test_sync_description_can_be_disabled(self):
        with open(self.mod / "descriptor.mod", "a") as f:
            f.write('remote_file_id="123456"\n')
        self.assertNotIn('"description"', self.vdf(self.publish(SYNC_DESCRIPTION="0").stdout))

    def test_stages_exactly_the_mod_files(self):
        (self.mod / ".DS_Store").write_text("junk")
        out = self.publish().stdout
        staged = re.findall(r"^   \./(.+)$", out, re.M)
        expected = sorted(p.relative_to(self.mod).as_posix() for p in self.mod.rglob("*")
                          if p.is_file() and p.name != ".DS_Store")
        self.assertEqual(sorted(staged), expected)

    def test_refuses_when_check_fails(self):
        path = self.mod / "common/traditions/lfg_traditions.txt"
        path.write_text(path.read_text().replace("pop_happiness = 0.05", "pop_happyness = 0.05"))
        res = self.publish()
        self.assertNotEqual(res.returncode, 0)
        self.assertNotIn('"workshopitem"', res.stdout)
        self.assertIn("unknown modifier pop_happyness", res.stdout)

    def test_requires_steam_user_for_real_upload(self):
        res = self.publish(DRY_RUN="0")
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("STEAM_USER", res.stderr)


if __name__ == "__main__":
    unittest.main()
