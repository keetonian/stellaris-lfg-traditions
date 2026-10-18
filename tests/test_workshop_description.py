"""The Steam page (workshop_description.txt) must not reveal the Evolutionary Predators easter eggs."""
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SECRETS = ("Evolutionary Predators", "Species Experimentation", "Inherited Genius", "lfg_species_experimentation",
           "trait_lfg_inherited_genius", "subspecies")


class WorkshopDescriptionTests(unittest.TestCase):
    def test_no_easter_eggs(self):
        text = (REPO / "workshop_description.txt").read_text(encoding="utf-8")
        for secret in SECRETS:
            self.assertNotIn(secret, text, f"workshop_description.txt reveals an easter egg: {secret!r}")


if __name__ == "__main__":
    unittest.main()
