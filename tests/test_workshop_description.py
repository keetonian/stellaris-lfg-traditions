"""The Steam page (workshop_description.txt) must not reveal the Evolutionary Predators easter eggs."""
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SECRETS = ("Evolutionary Predators", "Species Experimentation", "Inherited Genius", "lfg_species_experimentation",
           "trait_lfg_inherited_genius", "subspecies")


class WorkshopDescriptionTests(unittest.TestCase):
    def test_fits_steam_limit(self):
        # Over 8000 characters, Steam fails the whole upload with "Invalid Parameter".
        text = (REPO / "workshop_description.txt").read_text(encoding="utf-8")
        self.assertLessEqual(len(text), 8000, f"workshop_description.txt is {len(text)} characters (Steam limit 8000)")

    def test_no_easter_eggs(self):
        text = (REPO / "workshop_description.txt").read_text(encoding="utf-8")
        for secret in SECRETS:
            self.assertNotIn(secret, text, f"workshop_description.txt reveals an easter egg: {secret!r}")


if __name__ == "__main__":
    unittest.main()
