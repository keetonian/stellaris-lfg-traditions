#!/usr/bin/env python3
"""Static verification for the LFG Traditions mod.

  python3 -I tools/check_mod.py                    # full check (uses installed game + Giga when found)
  python3 -I tools/check_mod.py --require-sources  # fail instead of skipping checks that need game files
  python3 -I tools/check_mod.py --update-snapshot  # refresh tools/data/modifiers_4.5.txt.gz from modifiers.log

Checks that only need the repo (always run, also in CI): file layout, parse errors, localisation format/BOM/duplicates,
tradition tree structure and prerequisites, required localisation keys, sprite definitions, modifier names (against
modifiers.log or the bundled snapshot), key prefixes, descriptor and thumbnail.
Checks that need the installed game / Giga: tree templates, texture files, referenced techs/origins/civics/ethics/
variables, and that the generated vanilla overrides are up to date.
"""
from __future__ import annotations

import argparse
import gzip
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_overrides  # noqa: E402
import pdx  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
STEAM = Path.home() / "Library/Application Support/Steam/steamapps"
DEFAULT_GAME = STEAM / "common/Stellaris"
DEFAULT_GIGA = STEAM / "workshop/content/281990/1121692237"
DEFAULT_MODIFIERS_LOG = Path.home() / "Documents/Paradox Interactive/Stellaris/logs/script_documentation/modifiers.log"
SNAPSHOT = REPO / "tools/data/modifiers_4.5.txt.gz"

# Vanilla tree layouts in interface/topbar_traditions_view.gui (4.5). Used when the game isn't installed.
KNOWN_TREE_TEMPLATES = {
    "tree_11_11_21", "tree_11_111", "tree_11_12_21", "tree_11_12", "tree_111_11", "tree_12_11_11",
    "tree_12_11", "tree_12_12", "tree_21_11", "tree_21_12", "tree_21_21",
}
# Required prerequisites per layout: slot index -> slots it must require (1-based).
TEMPLATE_PREREQS = {"tree_21_11": {4: {1, 2}, 5: {3}}}

ALLOWED_FILES = [
    r"descriptor\.mod",
    r"thumbnail\.png",
    r"common/tradition_categories/[^/]+\.txt",
    r"common/traditions/[^/]+\.txt",
    r"common/governments/civics/[^/]+\.txt",
    r"common/ascension_perks/[^/]+\.txt",
    r"common/technology/zz_lfg_[^/]+\.txt",
    r"common/inline_scripts/technology/giga_mega_repeatable\.txt",  # generated whole-file override of Giga's
    r"common/situations/zz_lfg_[^/]+\.txt",
    r"common/districts/zz_lfg_[^/]+\.txt",
    r"common/buildings/zz_lfg_[^/]+\.txt",
    r"common/zones/zz_lfg_[^/]+\.txt",
    r"common/script_values/[^/]+\.txt",
    r"common/scripted_variables/[^/]+\.txt",
    r"common/scripted_triggers/[^/]+\.txt",
    r"common/scripted_effects/[^/]+\.txt",
    r"common/edicts/[^/]+\.txt",
    r"common/council_agendas/[^/]+\.txt",
    r"common/static_modifiers/[^/]+\.txt",
    r"common/on_actions/[^/]+\.txt",
    r"common/policies/[^/]+\.txt",
    r"common/decisions/[^/]+\.txt",
    r"common/traits/[^/]+\.txt",
    r"events/[^/]+\.txt",
    r"interface/[^/]+\.gfx",
    r"localisation/english/[^/]+_l_english\.yml",
    r"localisation/english/replace/lfg_[^/]+_l_english\.yml",  # generated overrides of game/Giga text
]
OVERRIDE_FILES = {Path(p).relative_to("mod").as_posix() for p in gen_overrides.OVERRIDES}
KEY_PREFIXES = ("tradition_lfg_", "tr_lfg_", "civic_lfg_", "agenda_lfg_", "decision_lfg_", "trait_lfg_", "ap_lfg_", "lfg_",
                "@lfg_")
# Folders whose top-level keys are vanilla names we add to (on_actions merge into vanilla lists).
PREFIX_EXEMPT_FOLDERS = ("common/on_actions/",)
# Single-category values used by vanilla policies (common/policies/00_policies.txt, 4.5).
POLICY_CATEGORIES = {"diplomacy", "economy", "military", "research", "society"}
STATIC_MODIFIER_NON_MODIFIERS = {"icon", "icon_frame", "custom_tooltip", "hide_in_tooltip", "show_only_custom_tooltip"}
LOC_LINE = re.compile(r'^ ([A-Za-z0-9_.\-]+):(\d+)? "(.*)"\s*$')
# Keys whose value is a localisation key.
LOC_VALUE_KEYS = {"desc", "description", "negative_description", "text", "fail_text", "custom_tooltip"}
NOT_MODIFIERS = {"potential", "mult", "desc", "custom_tooltip", "show_only_custom_tooltip"}


class Report:
    def __init__(self, require_sources: bool):
        self.failures: List[str] = []
        self.skipped: List[str] = []
        self.require_sources = require_sources

    def fail(self, msg: str) -> None:
        self.failures.append(msg)

    def skip(self, what: str) -> None:
        if self.require_sources:
            self.fail(f"{what}: game/Giga files not found (--require-sources)")
        else:
            self.skipped.append(what)


class Mod:
    """Parsed view of the mod directory."""

    def __init__(self, root: Path, report: Report):
        self.root = root
        self.report = report
        self.files: Dict[str, List[pdx.Entry]] = {}
        for path in sorted(root.rglob("*")):
            rel = path.relative_to(root).as_posix()
            if path.is_file() and path.suffix in (".txt", ".gfx"):
                try:
                    self.files[rel] = pdx.parse_file(path)
                except (pdx.ParseError, UnicodeDecodeError) as e:
                    report.fail(f"{rel}: parse error: {e}")

    def top(self, folder: str) -> Dict[str, pdx.Entry]:
        out: Dict[str, pdx.Entry] = {}
        for rel, entries in self.files.items():
            if rel.startswith(folder + "/") and rel not in OVERRIDE_FILES:
                for e in entries:
                    if e.key is not None:
                        if e.key in out:
                            self.report.fail(f"{rel}: duplicate definition of {e.key}")
                        out[e.key] = e
        return out


# ------------------------------------------------------------------------------------------------
def check_layout(mod: Mod, r: Report) -> None:
    for path in sorted(mod.root.rglob("*")):
        if path.is_file() and path.name != ".DS_Store":  # Finder junk; install/publish strip it
            rel = path.relative_to(mod.root).as_posix()
            if not any(re.fullmatch(p, rel) for p in ALLOWED_FILES):
                r.fail(f"unexpected file in mod/: {rel}")


def check_descriptor(mod: Mod, r: Report) -> None:
    d = mod.root / "descriptor.mod"
    if not d.exists():
        r.fail("missing descriptor.mod")
        return
    text = d.read_text(encoding="utf-8")
    for field in ("name", "version", "supported_version", "picture"):
        if not re.search(rf'^{field}="[^"]+"', text, re.M):
            r.fail(f"descriptor.mod: missing {field}")
    if re.search(r"^path=", text, re.M):
        r.fail("descriptor.mod: must not contain path=")
    thumb = mod.root / "thumbnail.png"
    if not thumb.exists():
        r.fail("missing thumbnail.png")
    else:
        data = thumb.read_bytes()
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            r.fail("thumbnail.png is not a PNG")
        if len(data) >= 1024 * 1024:
            r.fail(f"thumbnail.png is {len(data)} bytes (Steam limit 1 MB)")


def load_loc(mod: Mod, r: Report) -> Dict[str, str]:
    keys: Dict[str, str] = {}
    for path in sorted((mod.root / "localisation").rglob("*.yml")):
        rel = path.relative_to(mod.root).as_posix()
        raw = path.read_bytes()
        if not raw.startswith(b"\xef\xbb\xbf"):
            r.fail(f"{rel}: missing UTF-8 BOM")
        lines = raw.decode("utf-8-sig").splitlines()
        if not lines or lines[0].strip() != "l_english:":
            r.fail(f"{rel}: first line must be 'l_english:'")
        for n, line in enumerate(lines[1:], start=2):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            m = LOC_LINE.match(line)
            if not m:
                r.fail(f"{rel}:{n}: malformed localisation line: {line.strip()[:60]}")
                continue
            key, value = m.group(1), m.group(3)
            if key in keys:
                r.fail(f"{rel}:{n}: duplicate localisation key {key}")
            if value.count("§") and value.count("§!") * 2 != value.count("§"):
                r.fail(f"{rel}:{n}: unbalanced § colour codes in {key}")
            keys[key] = value
    return keys


def tree_file_name(name: str) -> str:
    """00_<English tree name>_lfg.txt: sorts the tree alphabetically among vanilla's 00_<tree>.txt regular trees in the
    traditions window (load order = file name order), instead of after the 01_* ascension trees."""
    words = re.sub(r"[^a-z0-9]+", " ", name.lower()).split()
    if words[:1] == ["the"]:
        words = words[1:]
    return "00_" + "_".join(words) + "_lfg.txt"


def check_tree_files(mod: Mod, loc: Dict[str, str], r: Report) -> None:
    for rel, entries in mod.files.items():
        if not rel.startswith("common/tradition_categories/"):
            continue
        keys = [e.key for e in entries if e.key is not None]
        if len(keys) != 1:
            r.fail(f"{rel}: put exactly one tree per file (found {len(keys)}), so each sorts into place")
            continue
        if keys[0] in loc:
            expected = tree_file_name(loc[keys[0]])
            if Path(rel).name != expected:
                r.fail(f"{rel}: rename to {expected} so {keys[0]} sorts by its name in the traditions window")


def check_traditions(mod: Mod, loc: Dict[str, str], templates: Set[str], r: Report) -> None:
    cats = mod.top("common/tradition_categories")
    trads = mod.top("common/traditions")
    owner: Dict[str, str] = {}
    if not cats:
        r.fail("no tradition categories defined")
    for ck, cat in cats.items():
        if not cat.is_block:
            r.fail(f"{ck}: not a block")
            continue
        body = cat.value
        tmpl = pdx.first(body, "tree_template")
        if tmpl is None or tmpl.value not in templates:
            r.fail(f"{ck}: unknown tree_template {getattr(tmpl, 'value', None)!r}")
        tlist = pdx.first(body, "traditions")
        listed = pdx.bare_values(tlist.value) if tlist is not None and tlist.is_block else []
        if len(listed) != 5:
            r.fail(f"{ck}: expected 5 traditions, found {len(listed)}")
        members = list(listed)
        for bonus in ("adoption_bonus", "finish_bonus"):
            e = pdx.first(body, bonus)
            if e is None:
                r.fail(f"{ck}: missing {bonus}")
            else:
                members.append(e.value)
        for t in members:
            if t not in trads:
                r.fail(f"{ck}: tradition {t} is not defined")
            if t in owner:
                r.fail(f"{t}: listed in both {owner[t]} and {ck}")
            owner[t] = ck
        # loc + sprites for the category
        for key in (ck, f"{ck}_desc"):
            if key not in loc:
                r.fail(f"missing localisation: {key}")
        for d in pdx.get(body, "desc"):
            text = d.value if not d.is_block else (pdx.first(d.value, "text") or pdx.Entry(None, None, "", 0)).value
            if text and text not in loc:
                r.fail(f"{ck}: desc key {text} has no localisation")
        for key in members:
            if key not in loc:
                r.fail(f"missing localisation: {key}")
        for key in listed:
            for suffix in ("_desc", "_delayed"):
                if key + suffix not in loc:
                    r.fail(f"missing localisation: {key}{suffix}")
        # prerequisites stay inside the tree and match the layout
        slots = {t: i + 1 for i, t in enumerate(listed)}
        for t in listed:
            if t not in trads or not trads[t].is_block:
                continue
            possible = pdx.first(trads[t].value, "possible")
            reqs = [e.value for e in pdx.walk(possible.value) if e.key == "has_tradition"] \
                if possible is not None and possible.is_block else []
            for req in reqs:
                if req not in slots:
                    r.fail(f"{t}: requires {req}, which is not in {ck}")
            expected = TEMPLATE_PREREQS.get(getattr(tmpl, "value", ""), {}).get(slots[t], set())
            got = {slots[q] for q in reqs if q in slots}
            if tmpl is not None and tmpl.value in TEMPLATE_PREREQS and got != expected:
                r.fail(f"{t}: slot {slots[t]} of {tmpl.value} should require slots {sorted(expected)}, requires {sorted(got)}")
    for t in trads:
        if t not in owner:
            r.fail(f"{t}: defined but not part of any tradition category")


def check_civics(mod: Mod, loc: Dict[str, str], r: Report) -> None:
    for ck, civ in mod.top("common/governments/civics").items():
        for key in (ck, f"{ck}_desc"):
            if key not in loc:
                r.fail(f"missing localisation: {key}")
        if civ.is_block and pdx.first(civ.value, "modifier") is None:
            r.fail(f"{ck}: has no modifier block")


def check_loc_references(mod: Mod, loc: Dict[str, str], r: Report) -> None:
    for rel, entries in mod.files.items():
        for e in pdx.walk(entries):
            if e.key in LOC_VALUE_KEYS and not e.is_block and "lfg" in e.value and e.value not in loc:
                r.fail(f"{rel}:{e.line}: {e.key} = {e.value} has no localisation")


def check_edicts(mod: Mod, loc: Dict[str, str], r: Report) -> None:
    # Edicts are localised as edict_<key>; decisions, traits and ascension perks as <key> (vanilla conventions).
    names = ([f"edict_{k}" for k in mod.top("common/edicts")] + list(mod.top("common/decisions"))
             + list(mod.top("common/traits")) + list(mod.top("common/ascension_perks")))
    for key in names:
        for k in (key, f"{key}_desc"):
            if k not in loc:
                r.fail(f"missing localisation: {k}")


def mod_event_ids(mod: Mod) -> Set[str]:
    ids: Set[str] = set()
    for rel, entries in mod.files.items():
        if rel.startswith("events/") and rel not in OVERRIDE_FILES:
            for e in entries:
                if e.key and e.key.endswith("_event") and e.is_block:
                    i = pdx.first(e.value, "id")
                    if i is not None:
                        ids.add(i.value)
    return ids


def check_events(mod: Mod, loc: Dict[str, str], r: Report) -> None:
    seen: Set[str] = set()
    for rel, entries in mod.files.items():
        if not rel.startswith("events/") or rel in OVERRIDE_FILES:  # generated vanilla event overrides
            continue
        namespaces = [e.value for e in pdx.get(entries, "namespace")]
        if not namespaces:
            r.fail(f"{rel}: missing namespace")
        for ns in namespaces:
            if not ns.startswith("lfg_"):
                r.fail(f"{rel}: namespace {ns} lacks an lfg prefix")
        for e in entries:
            if e.key == "namespace":
                continue
            if not (e.key and e.key.endswith("_event") and e.is_block):
                r.fail(f"{rel}:{e.line}: unexpected top-level entry {e.key}")
                continue
            i = pdx.first(e.value, "id")
            if i is None or not any(i.value.startswith(ns + ".") for ns in namespaces):
                r.fail(f"{rel}:{e.line}: event id {getattr(i, 'value', None)} not in this file's namespace")
                continue
            if i.value in seen:
                r.fail(f"{rel}:{e.line}: duplicate event id {i.value}")
            seen.add(i.value)
            keys = [x.value for x in pdx.get(e.value, "title") + pdx.get(e.value, "desc") if not x.is_block]
            for opt in pdx.get(e.value, "option"):
                keys += [x.value for x in pdx.get(opt.value, "name") if not x.is_block]
            for k in keys:
                if k not in loc:
                    r.fail(f"{rel}: {i.value} uses {k}, which has no localisation")
    # Fired events: any nested `*_event = { id = lfg_... }` (top-level blocks in events/ are the definitions).
    ids = mod_event_ids(mod)
    for rel, entries in mod.files.items():
        definitions = {id(e) for e in entries} if rel.startswith("events/") else set()
        for e in pdx.walk(entries):
            if id(e) in definitions or not (e.key and e.key.endswith("_event") and e.is_block):
                continue
            i = pdx.first(e.value, "id")
            if i is not None and i.value.startswith("lfg_") and i.value not in ids:
                r.fail(f"{rel}:{e.line}: fires {i.value}, which is not defined")


def check_agendas_and_static_modifiers(mod: Mod, loc: Dict[str, str], known: Set[str], r: Report) -> None:
    agendas = mod.top("common/council_agendas")
    statics = mod.top("common/static_modifiers")
    for key, a in agendas.items():
        for k in (f"council_agenda_{key}_name", f"council_agenda_{key}_desc"):
            if k not in loc:
                r.fail(f"missing localisation: {k}")
        fm = pdx.first(a.value, "finish_modifier") if a.is_block else None
        if fm is None:
            r.fail(f"{key}: missing finish_modifier")
        elif fm.value.startswith(KEY_PREFIXES) and fm.value not in statics:
            r.fail(f"{key}: finish_modifier {fm.value} is not defined in common/static_modifiers")
    for key, sm in statics.items():
        for k in (key, f"{key}_desc"):
            if k not in loc:
                r.fail(f"missing localisation: {k}")
        for m in sm.value if sm.is_block else []:
            if m.key in STATIC_MODIFIER_NON_MODIFIERS:
                continue
            if m.key not in known:
                r.fail(f"static modifier {key}: unknown modifier {m.key}")
            if m.is_block or not re.fullmatch(r"-?\d+(\.\d+)?|@[A-Za-z0-9_]+", m.value):
                r.fail(f"static modifier {key}: {m.key} has non-numeric value {m.value!r}")
    for rel, entries in mod.files.items():
        for e in pdx.walk(entries):
            if e.key == "unlocks_agenda" and not e.is_block and e.value.startswith(KEY_PREFIXES) \
                    and e.value not in agendas:
                r.fail(f"{rel}:{e.line}: unlocks_agenda {e.value} is not defined in common/council_agendas")
            if e.key == "add_modifier" and e.is_block:
                m = pdx.first(e.value, "modifier")
                if m is not None and m.value.startswith(KEY_PREFIXES) and m.value not in statics:
                    r.fail(f"{rel}:{e.line}: add_modifier {m.value} is not defined in common/static_modifiers")


def check_policies(mod: Mod, loc: Dict[str, str], r: Report) -> None:
    flags: Set[str] = set()
    for key, pol in mod.top("common/policies").items():
        cat = pdx.first(pol.value, "category") if pol.is_block else None
        if cat is None or cat.is_block or cat.value not in POLICY_CATEGORIES:
            r.fail(f"{key}: policy category must be one of {sorted(POLICY_CATEGORIES)}")
        for k in (f"policy_{key}", f"policy_{key}_desc"):
            if k not in loc:
                r.fail(f"missing localisation: {k}")
        options = pdx.get(pol.value, "option") if pol.is_block else []
        if len(options) < 2:
            r.fail(f"{key}: a policy needs at least 2 options")
        for opt in options:
            name = pdx.first(opt.value, "name")
            if name is None:
                r.fail(f"{key}:{opt.line}: option without a name")
                continue
            for k in (name.value, f"{name.value}_name", f"{name.value}_desc"):
                if k not in loc:
                    r.fail(f"missing localisation: {k}")
            for block in pdx.get(opt.value, "policy_flags"):
                flags.update(pdx.bare_values(block.value))
    for rel, entries in mod.files.items():
        for e in pdx.walk(entries):
            if e.key == "has_policy_flag" and not e.is_block and e.value.startswith("lfg_") and e.value not in flags:
                r.fail(f"{rel}:{e.line}: has_policy_flag = {e.value} is not set by any policy option in this mod")


def check_on_actions(mod: Mod, r: Report) -> None:
    ids = mod_event_ids(mod)
    for rel, entries in mod.files.items():
        if not rel.startswith("common/on_actions/"):
            continue
        for action in entries:
            for block in pdx.get(action.value, "events") if action.is_block else []:
                for ev in pdx.bare_values(block.value) if block.is_block else []:
                    if ev.startswith("lfg_") and ev not in ids:
                        r.fail(f"{rel}: {action.key} fires {ev}, which is not defined")


def check_scripted_references(mod: Mod, r: Report) -> None:
    """lfg_* scripted triggers/effects used as `x = yes` and value:lfg_* script values must be defined in the mod."""
    scripted = set(mod.top("common/scripted_triggers")) | set(mod.top("common/scripted_effects"))
    values = set(mod.top("common/script_values"))
    edicts = set(mod.top("common/edicts"))
    for rel, entries in mod.files.items():
        for e in pdx.walk(entries):
            if e.is_block:
                continue
            if e.key == "has_edict" and e.value.startswith("lfg_"):
                names = [e.value.replace("$area$", a) for a in gen_overrides.MEGA_CAP_AREAS] if "$area$" in e.value \
                    else [e.value]
                for name in names:
                    if name not in edicts:
                        r.fail(f"{rel}:{e.line}: has_edict = {name} is not an edict defined in this mod")
            if e.key and e.key.startswith("lfg_") and e.value in ("yes", "no") and e.key not in scripted:
                r.fail(f"{rel}:{e.line}: {e.key} is not a scripted trigger/effect defined in this mod")
            if isinstance(e.value, str) and e.value.startswith("value:lfg_") and e.value[6:] not in values:
                r.fail(f"{rel}:{e.line}: {e.value} is not defined in common/script_values")


def mod_sprites(mod: Mod, r: Report) -> Dict[str, str]:
    sprites: Dict[str, str] = {}
    for rel, entries in mod.files.items():
        if not rel.endswith(".gfx"):
            continue
        for block in pdx.get(entries, "spriteTypes"):
            for s in block.value if block.is_block else []:
                if not s.is_block:
                    continue
                name, tex = pdx.first(s.value, "name"), pdx.first(s.value, "textureFile")
                if name is None or tex is None:
                    r.fail(f"{rel}:{s.line}: sprite missing name or textureFile")
                    continue
                if name.value in sprites:
                    r.fail(f"{rel}:{s.line}: duplicate sprite {name.value}")
                sprites[name.value] = tex.value
    return sprites


def check_sprites(mod: Mod, game: Optional[Path], r: Report) -> None:
    sprites = mod_sprites(mod, r)
    for ck, cat in mod.top("common/tradition_categories").items():
        for kind in ("hex_bg", "category_bg", "category_tile", "category_icon"):
            if f"GFX_tradition_{kind}_{ck}" not in sprites:
                r.fail(f"{ck}: missing sprite GFX_tradition_{kind}_{ck}")
        tlist = pdx.first(cat.value, "traditions") if cat.is_block else None
        for t in pdx.bare_values(tlist.value) if tlist is not None and tlist.is_block else []:
            if f"GFX_{t}" not in sprites:
                r.fail(f"{t}: missing sprite GFX_{t}")
    for ap in mod.top("common/ascension_perks"):
        if f"GFX_{ap}" not in sprites:
            r.fail(f"{ap}: missing sprite GFX_{ap}")
    textures = set(sprites.values())
    for civ in list(mod.top("common/governments/civics").values()) + list(mod.top("common/traits").values()):
        icon = pdx.first(civ.value, "icon") if civ.is_block else None
        if icon is not None:
            textures.add(icon.value)
    if game is None:
        r.skip("texture files exist")
        return
    for tex in sorted(textures):
        if not ((mod.root / tex).exists() or (game / tex).exists()):
            r.fail(f"texture not found in mod or game: {tex}")


def load_modifiers(log: Optional[Path]) -> Set[str]:
    if log is not None and log.exists():
        text = log.read_text(encoding="utf-8", errors="replace")
        return set(re.findall(r"^- ([A-Za-z0-9_@]+), Category", text, re.M))
    with gzip.open(SNAPSHOT, "rt", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip() and not line.startswith("#")}


def modifier_keys(mod: Mod):
    for folder in ("common/traditions", "common/governments/civics", "common/council_agendas"):
        for key, e in mod.top(folder).items():
            if not e.is_block:
                continue
            for block in pdx.get(e.value, "modifier") + pdx.get(e.value, "triggered_modifier"):
                for m in block.value if block.is_block else []:
                    if m.key and m.key not in NOT_MODIFIERS:
                        yield key, m


def check_modifiers(mod: Mod, known: Set[str], r: Report) -> None:
    for owner, m in modifier_keys(mod):
        if m.key not in known:
            r.fail(f"{owner}: unknown modifier {m.key}")
        if m.is_block or not re.fullmatch(r"-?\d+(\.\d+)?|@[A-Za-z0-9_]+", m.value):
            r.fail(f"{owner}: modifier {m.key} has non-numeric value {m.value!r}")


def visible_modifier_keys(mod: Mod):
    """(owner, key) for every modifier shown in a tooltip: traditions/civics/agendas plus static modifiers,
    skipping blocks that hide their lines behind show_only_custom_tooltip = yes."""
    statics = [(k, e) for k, e in mod.top("common/static_modifiers").items()]
    for owner, m in modifier_keys(mod):
        yield owner, m.key
    for key, sm in statics:
        if sm.is_block:
            for m in sm.value:
                if m.key and m.key not in STATIC_MODIFIER_NON_MODIFIERS:
                    yield key, m.key


def hidden_modifier_keys(mod: Mod) -> Set[str]:
    """Modifiers in static modifiers with show_only_custom_tooltip = yes (their lines never appear in tooltips)."""
    hidden: Set[str] = set()
    for sm in mod.top("common/static_modifiers").values():
        if sm.is_block and any(x.key == "show_only_custom_tooltip" and x.value == "yes" for x in sm.value):
            hidden.update(x.key for x in sm.value if x.key)
    return hidden


def check_show_only_custom_tooltip(mod: Mod, r: Report) -> None:
    """show_only_custom_tooltip is ignored in tradition/civic/agenda modifier blocks (all lines still show in game);
    it only works in static modifiers and techs. Use a static modifier applied via on_enabled instead."""
    for folder in ("common/traditions", "common/governments/civics", "common/council_agendas"):
        for key, e in mod.top(folder).items():
            for x in pdx.walk(e.value) if e.is_block else []:
                if x.key == "show_only_custom_tooltip":
                    r.fail(f"{key}: show_only_custom_tooltip has no effect here; move the modifiers to a static modifier")


# Modifier families the game generates per job / district. Vanilla names some (mod_pop_entertainer_bonus_workforce_mult,
# mod_planet_district_city_build_speed_mult) and not others; unnamed ones show as raw "mod_..." text in tooltips.
GENERATED_MODIFIER = re.compile(
    r"pop_[a-z0-9_]+_(bonus_)?workforce_mult|job_[a-z0-9_]+_(add|per_pop|per_crime|max_workforce_(add|mult)|automated_workforce_mult)"
    r"|planet_(district|building)_[a-z0-9_]+_build_speed_mult|district_[a-z0-9_]+_max_(add|mult)")


def load_game_loc_keys(dirs: List[Path]) -> Set[str]:
    keys: Set[str] = set()
    for d in dirs:
        for path in (d / "localisation").rglob("*english*.yml") if (d / "localisation").exists() else []:
            for m in re.finditer(r"^[ \t]+([A-Za-z0-9_.\-]+):", path.read_text(encoding="utf-8-sig", errors="replace"), re.M):
                keys.add(m.group(1).lower())
    return keys


def check_modifier_loc(mod: Mod, loc: Dict[str, str], game: Optional[Path], giga: Optional[Path], r: Report) -> None:
    """Every modifier shown in a tooltip needs a mod_<modifier> loc key somewhere, or the game prints the raw key."""
    if game is None or giga is None:
        r.skip("modifiers have in-game localisation")
        return
    game_keys = load_game_loc_keys([game, giga])
    mod_keys = {k.lower() for k in loc}
    hidden = hidden_modifier_keys(mod)
    seen: Set[str] = set()
    for owner, key in visible_modifier_keys(mod):
        if key in hidden or key in seen:
            continue
        seen.add(key)
        if not GENERATED_MODIFIER.fullmatch(key):
            continue  # engine/category modifiers get names automatically or under unpredictable MOD_* keys
        loc_key = f"mod_{key}".lower()
        if loc_key not in game_keys and loc_key not in mod_keys:
            r.fail(f"{owner}: modifier {key} has no localisation (add mod_{key} to the mod's loc)")
    for k in loc:
        if k.lower().startswith("mod_") and k.lower() in game_keys:
            r.fail(f"localisation key {k} overrides an existing game/Giga key")


def check_prefixes(mod: Mod, loc: Dict[str, str], r: Report) -> None:
    for rel, entries in mod.files.items():
        if not rel.startswith("common/") or rel in OVERRIDE_FILES or rel.startswith(PREFIX_EXEMPT_FOLDERS):
            continue
        for e in entries:
            if e.key is not None and not e.key.startswith(KEY_PREFIXES):
                r.fail(f"{rel}:{e.line}: top-level key {e.key} lacks an lfg prefix")
    replaced = set(gen_overrides.LOC_OVERRIDES_KEYS)
    for key in loc:
        if "lfg" not in key and not key.startswith("mod_") and key not in replaced:  # mod_<modifier>: loc for modifiers vanilla left unnamed
            r.fail(f"localisation key {key} lacks an lfg prefix (could overwrite vanilla/other mods)")


# --- needs game / Giga --------------------------------------------------------------------------
def check_loc_parameters(loc: Dict[str, str], game: Optional[Path], giga: Optional[Path], r: Report) -> None:
    """$key$ references in the mod's loc (e.g. tech names in the Shelve edicts) must name an existing loc key."""
    if game is None or giga is None:
        r.skip("$key$ references in localisation exist")
        return
    known = load_game_loc_keys([game, giga]) | {k.lower() for k in loc}
    for key, value in loc.items():
        for ref in re.findall(r"\$([A-Za-z0-9_.]+)\$", value):
            if ref.lower() not in known:
                r.fail(f"localisation {key}: ${ref}$ is not a localisation key in the game, Giga or this mod")


def defined_keys(dirs: List[Path], folder: str) -> Set[str]:
    out: Set[str] = set()
    for d in dirs:
        for path in (d / folder).rglob("*.txt") if (d / folder).exists() else []:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            out.update(re.findall(r"^([A-Za-z0-9_\.]+)\s*=\s*\{", text, re.M))
    return out


def defined_variables(dirs: List[Path]) -> Set[str]:
    out: Set[str] = set()
    for d in dirs:
        for path in (d / "common/scripted_variables").rglob("*.txt") if (d / "common/scripted_variables").exists() else []:
            out.update(re.findall(r"^(@[A-Za-z0-9_]+)\s*=", path.read_text(encoding="utf-8-sig", errors="replace"), re.M))
    return out


def check_references(mod: Mod, game: Optional[Path], giga: Optional[Path], r: Report) -> None:
    if game is None or giga is None:
        r.skip("referenced techs/origins/civics/ethics/variables exist")
        return
    dirs = [game, giga, mod.root]
    techs = defined_keys(dirs, "common/technology")
    civics = defined_keys(dirs, "common/governments/civics")  # civics and origins
    ethics = defined_keys(dirs, "common/ethics")
    trads = defined_keys(dirs, "common/traditions")
    buildings = defined_keys(dirs, "common/buildings")
    perks = defined_keys(dirs, "common/ascension_perks")
    variables = defined_variables([game, giga, mod.root])
    lookups = {"has_technology": techs, "has_origin": civics, "has_valid_civic": civics, "has_civic": civics,
               "has_ethic": ethics, "has_tradition": trads, "has_building": buildings, "has_ascension_perk": perks}
    for rel, entries in mod.files.items():
        if not rel.startswith("common/") or rel in OVERRIDE_FILES:
            continue
        for e in pdx.walk(entries):
            # $PARAM$ values are scripted-effect/trigger parameters, filled in at the call site
            if not e.is_block and e.key in lookups and "$" not in e.value and e.value not in lookups[e.key]:
                r.fail(f"{rel}:{e.line}: {e.key} = {e.value} is not defined in the game, Giga or this mod")
            if not e.is_block and isinstance(e.value, str) and e.value.startswith("@") and e.value not in variables:
                r.fail(f"{rel}:{e.line}: scripted variable {e.value} is not defined")
            if e.key in ("origin", "civics", "ethics") and e.is_block:
                pool = ethics if e.key == "ethics" else civics
                for v in pdx.walk(e.value):
                    if v.key == "value" and v.value not in pool:
                        r.fail(f"{rel}:{v.line}: {e.key} value {v.value} is not defined")


def check_overrides(mod: Mod, game: Optional[Path], giga: Optional[Path], r: Report) -> None:
    if game is None or giga is None:
        r.skip("vanilla/Giga overrides and Shelve edicts are up to date")
        return
    try:
        generated = gen_overrides.generate(game, giga)
    except (gen_overrides.GenError, OSError) as e:
        r.fail(f"tools/gen_overrides.py fails against the installed game/Giga: {e}")
        return
    for out_rel, content in generated.items():
        path = mod.root.parent / out_rel
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            r.fail(f"{out_rel} is stale: run python3 -I tools/gen_overrides.py and review the diff")


def tree_templates(game: Optional[Path], r: Report) -> Set[str]:
    gui = game / "interface/topbar_traditions_view.gui" if game else None
    if gui is None or not gui.exists():
        r.skip("tree templates from the installed game (using the built-in 4.5 list)")
        return KNOWN_TREE_TEMPLATES
    return set(re.findall(r'name = "(tree_[0-9_]+)"', gui.read_text(encoding="utf-8-sig", errors="replace")))


def run(mod_dir: Path, game: Optional[Path], giga: Optional[Path], modifiers_log: Optional[Path],
        require_sources: bool = False) -> Report:
    r = Report(require_sources)
    game = game if game is not None and game.exists() else None
    giga = giga if giga is not None and giga.exists() else None
    mod = Mod(mod_dir, r)
    check_layout(mod, r)
    check_descriptor(mod, r)
    loc = load_loc(mod, r)
    check_traditions(mod, loc, tree_templates(game, r), r)
    check_tree_files(mod, loc, r)
    check_civics(mod, loc, r)
    check_loc_references(mod, loc, r)
    check_edicts(mod, loc, r)
    check_events(mod, loc, r)
    check_scripted_references(mod, r)
    check_sprites(mod, game, r)
    known_modifiers = load_modifiers(modifiers_log)
    check_modifiers(mod, known_modifiers, r)
    check_agendas_and_static_modifiers(mod, loc, known_modifiers, r)
    check_on_actions(mod, r)
    check_policies(mod, loc, r)
    check_prefixes(mod, loc, r)
    check_references(mod, game, giga, r)
    check_modifier_loc(mod, loc, game, giga, r)
    check_show_only_custom_tooltip(mod, r)
    check_loc_parameters(loc, game, giga, r)
    check_overrides(mod, game, giga, r)
    return r


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Verify the LFG Traditions mod.")
    ap.add_argument("--mod", type=Path, default=REPO / "mod")
    ap.add_argument("--game", type=Path, default=Path(os.environ.get("STELLARIS_GAME", DEFAULT_GAME)))
    ap.add_argument("--giga", type=Path, default=Path(os.environ.get("GIGA_DIR", DEFAULT_GIGA)))
    ap.add_argument("--modifiers-log", type=Path, default=DEFAULT_MODIFIERS_LOG)
    ap.add_argument("--snapshot-only", action="store_true", help="ignore modifiers.log, use the bundled snapshot")
    ap.add_argument("--require-sources", action="store_true")
    ap.add_argument("--update-snapshot", action="store_true")
    args = ap.parse_args(argv)

    if args.update_snapshot:
        names = load_modifiers(args.modifiers_log) if args.modifiers_log.exists() else set()
        if not names:
            print(f"check_mod: {args.modifiers_log} not found", file=sys.stderr)
            return 1
        body = "# Modifier names from Stellaris script_documentation/modifiers.log (with Gigastructural loaded).\n" \
               "# Regenerate: python3 -I tools/check_mod.py --update-snapshot\n" + "\n".join(sorted(names)) + "\n"
        with gzip.GzipFile(SNAPSHOT, "wb", compresslevel=9, mtime=0) as f:
            f.write(body.encode("utf-8"))
        print(f"wrote {SNAPSHOT.relative_to(REPO)} ({len(names)} modifiers)")
        return 0

    log = None if args.snapshot_only else args.modifiers_log
    r = run(args.mod, args.game, args.giga, log, args.require_sources)
    for s in r.skipped:
        print(f"  skip  {s}")
    for f in r.failures:
        print(f"  FAIL  {f}")
    if r.failures:
        print(f"check_mod: {len(r.failures)} problem(s)")
        return 1
    print("check_mod: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
