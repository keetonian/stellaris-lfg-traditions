"""The Steam page (workshop_description.txt) must not reveal the easter eggs (Evolutionary Predators content, Lone Tide,
Shadow Transactions)."""
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SECRETS = ("Evolutionary Predators", "Species Experimentation", "Inherited Genius", "lfg_species_experimentation",
           "trait_lfg_inherited_genius", "subspecies",
           # The Lone Tide special system is a surprise too.
           "Lone Tide", "Thalassa", "special system", "hidden system", "lfg_lone_tide",
           # Swallowed Whole's Criminal Heritage perk is a secret as well.
           "Shadow Transactions", "ap_lfg_shadow_transactions")


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
