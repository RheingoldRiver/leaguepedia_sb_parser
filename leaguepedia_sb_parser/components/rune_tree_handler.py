import warnings
from typing import Tuple

import lol_dto
import lol_id_tools
import requests


class RuneTreeHandler:
    """A simple class that caches data from ddragon and gets rune tree per rune ID."""

    def __init__(self, patch=None):
        self.patch = patch
        self.cache = {}
        self.versions = None
        self.reload_versions()

    def reload_versions(self):
        self.versions = requests.get(
            "https://ddragon.leagueoflegends.com/api/versions.json"
        ).json()

    def get_runes_data(self):
        full_patch = self.get_version()

        if full_patch not in self.cache:
            self.cache[full_patch] = requests.get(
                f"https://ddragon.leagueoflegends.com/cdn/{full_patch}/data/en_US/runesReforged.json"
            ).json()

        return self.cache[full_patch]

    def get_version(self):
        if self.patch is None:
            return self.versions[0]

        for version in self.versions:
            if ".".join(version.split(".")[:2]) == self.patch:
                return version

        # If we have a patch that we do not know, we reload versions stupidly.
        warnings.warn("Reloading game versions")
        self.reload_versions()
        return self.get_version()

    def get_primary_tree(self, runes) -> Tuple[int, str]:
        return self.get_tree(runes[0])

    def get_primary_tree_name(self, runes) -> str:
        idx, name = self.get_primary_tree(runes)
        return name

    def get_secondary_tree(self, runes) -> Tuple[int, str]:
        return self.get_tree(runes[4])

    def get_secondary_tree_name(self, runes):
        idx, name = self.get_secondary_tree(runes)
        return name

    def get_tree(self, _rune: lol_dto.classes.game.LolGamePlayerRune) -> Tuple[int, str]:
        data = self.get_runes_data()

        for tree in data:
            for slot in tree["slots"]:
                for rune in slot["runes"]:
                    if rune["id"] == _rune.id:
                        return tree["id"], lol_id_tools.get_name(
                            tree["id"], object_type="rune"
                        )
