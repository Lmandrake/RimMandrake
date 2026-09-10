#!/usr/bin/env python3
"""gen_fauna_assignment_sheet.py — the owner's fauna sheet, rebuilt to his 2026-09-09 rulings.

What the owner ruled at the sitting (all encoded here):
  1. Only the creatures going IN each biome — no eviction rows anywhere.
  2. Smallest → largest inside each biome group, at TRUE relative scale, with the
     SAME colonist figure in every scale panel (the creature panels already carry it).
  3. Four controls per creature: In/Out/Move verdict · intended SIZE BIN
     (small / medium / large / TITAN, prefilled as a real recommendation, saying
     whether that grows or shrinks the creature) · art verdict keep/improve/redo ·
     a note. FOUNDRY rescales defs to the chosen bin afterwards.
  4. Badge creatures from mods on their way out.
  5. A HOMELESS section after the biomes: every live wild creature with no home,
     each with a plain recommendation. Out on a homeless row = CUT FOR REAL.
  6. Plain language everywhere. Questions become cards: the question, the
     tradeoffs, my recommendation. "Open" is renamed "Decide later".

Two outputs; only ONE is dangerous to re-run (review-sheets skill §7):
  fauna_assignment_register.html            safe to regenerate any time
  fauna_assignment_register.decisions.json  THE AGENT'S GUESSES — refuses to
                                            overwrite a sheet-stamped or frozen file
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROSTERS = HERE.parent / "biomes" / "rosters"
REGISTER = HERE / "creature_register_rows.json"
ART_DECISIONS = HERE / "creature_art_register.decisions.json"
SHEET = HERE / "fauna_assignment_register.html"
DECISIONS = HERE / "fauna_assignment_register.decisions.json"

TEMPLATE_CANDIDATES = [
    pathlib.Path.home() / ".claude/skills/review-sheets/assets/sheet_template.html",
]

NATIVE_DIR = r"D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review"

PANEL_PPC = 64.0          # px per cell the scale panels were rendered at
GROUP_MAX_PX = 460        # the biggest panel in a group is shown at most this wide/tall
HUMAN_CELLS = 1.5

# ── size bins (owner ruling 3; boundaries are MINE — CONFIG.invented names them) ──
BIN_EDGES = [("small", 0.0, 1.0), ("medium", 1.0, 2.2),
             ("large", 2.2, 5.0), ("titan", 5.0, 9e9)]
BIN_LABEL = {"small": "small", "medium": "medium (human)", "large": "large",
             "titan": "TITAN"}

# mods on their way out (ruling 4; sources: mod_retirement_audit.md,
# creature_recognizability_rule.md, STARWARS_DONOR_SUNSET_1)
MOD_DIES = {
    "Megafauna", "Beasts of the Rim (Continued)", "Mythic Ages: Megafauna Bestiary",
    "Jurassic Rimworld - Dinosaurs Only (Continued)",
}
MOD_SUNSET = {"Star Wars Animal Collection (Continued)"}
MOD_FEW = {"GRiNDTerra Biomes", "Biomes! Caverns", "Biomes! Polluted Lands",
           "Erin's Final Fantasy Animals", "Primordial Geysers", "ReGrowth 2"}

ART_MAP = {"approve": "keep", "revise": "improve", "redraw": "redo",
           "replace": "redo", "cancel": "redo"}


# ═══════════════════════════════════════════════════════ plain-language helpers
CITE = re.compile(
    r"\s*\((?:[^()]*(?:§|prep|fig\d|R\d|MEASURED|UNMEASURED|\.md|register|proxy)"
    r"[^()]*)\)")
JARGON = [
    (re.compile(r"\(MEASURED[^)]*\)|\(UNMEASURED[^)]*\)"), ""),
    (re.compile(r"\bMEASURED\b:?\s*"), ""),
    (re.compile(r"\bUNMEASURED\b:?\s*"), "unverified "),
    (re.compile(r"\bprep\s*§[\d.]+(?:\s*(?:recommendation|trim|q\d+))?'s"), "the prep notes'"),
    (re.compile(r"\bprep\s*§[\d.]+(?:\s*(?:recommendation|trim|q\d+))?"), "the prep notes"),
    (re.compile(r"\bsheet\s*§[\d.]+\w*"), "the biome sheet"),
    (re.compile(r"§[\d.]+\w*'s"), "the sheet's"),
    (re.compile(r"§[\d.]+\w*"), "the sheet"),
    (re.compile(r"§\s*"), "the sheet's "),
    (re.compile(r"\bproxy\b"), "quick test"),
    (re.compile(r"\bubiquity\b"), "everywhere-at-once"),
    (re.compile(r"\bfig\d+\w*(?:'s)?"), "the survey"),
    (re.compile(r"\bR\d+[a-z]?\b(?:'s)?"), "an earlier ruling"),
    (re.compile(r"\bban\s+(\d+)\b"), r"the sheet's rule \1"),
    (re.compile(r"\bcomm\b\.?"), "commonality"),
    (re.compile(r"\bbs\s+(?=[\d.])"), "body size "),
    (re.compile(r"\bspd\s+(?=[\d.])"), "speed "),
    (re.compile(r"\bdefName?s?\b"), "name"),
    (re.compile(r"\bwildAnimals\b"), "wild-animal list"),
    (re.compile(r"\bregister\b"), "creature data"),
    (re.compile(r"\bubiquity-25\b"), "everywhere-at-once"),
    (re.compile(r"\bhomeless-reserve\b"), "the no-home pool"),
]


def plain(text: str) -> str:
    """Strip sheet citations and jargon out of a law/note line."""
    out = CITE.sub("", str(text or ""))
    for rx, rep in JARGON:
        out = rx.sub(rep, out)
    out = re.sub(r"\s{2,}", " ", out)
    out = re.sub(r"\s+([;,.])", r"\1", out)
    out = re.sub(r"[;,]\s*(?=[;,.])", "", out)
    return out.strip(" ;,-")


def num(value) -> str:
    if value is None:
        return "?"
    text = f"{float(value):.4f}".rstrip("0").rstrip(".")
    return text or "0"


def size_bin(cells: float | None) -> str | None:
    if cells is None:
        return None
    for name, lo, hi in BIN_EDGES:
        if lo <= cells < hi:
            return name
    return "titan"


def size_phrase(cells: float | None, bs) -> str:
    if cells is None:
        return "size not measurable"
    if cells < 0.5:
        return f"tiny on screen ({num(cells)} squares)"
    if cells < 1.0:
        return f"small on screen ({num(cells)} squares — a person is 1.5)"
    if cells < 2.2:
        return f"about person-sized on screen ({num(cells)} squares)"
    if cells < 5.0:
        return f"big on screen ({num(cells)} squares — a person is 1.5)"
    return f"enormous on screen ({num(cells)} squares — a person is 1.5)"


def speed_phrase(spd) -> str:
    if spd is None:
        return "speed unknown"
    s = float(spd)
    if s < 2.0:
        return f"crawls ({num(spd)})"
    if s < 3.5:
        return f"slow ({num(spd)})"
    if s < 4.8:
        return f"walks ({num(spd)})"
    return f"fast ({num(spd)})"


def rarity_phrase(comm) -> str:
    if comm is None:
        return "spawn rate unset"
    c = float(comm)
    if c < 0.05:
        return "vanishingly rare here"
    if c < 0.2:
        return "rare here"
    if c < 0.6:
        return "seen now and then"
    if c < 1.0:
        return "common here"
    return "one of the most common animals here"


def threat_phrases(row: dict) -> list[str]:
    bits = []
    seen = " ".join(s.get("text", "") for s in (row.get("specials") or []))
    if "predator" in seen:
        bits.append("hunts other animals — and people count")
    if "venomous" in seen:
        bits.append("venomous")
    if "herd" in seen or "herds" in seen:
        bits.append("moves in herds")
    if "manhunter" in seen:
        bits.append("turns on people easily when hurt")
    if "dormant" in seen:
        bits.append("lies dormant until disturbed")
    return bits


def draw_cells(row: dict) -> float | None:
    v = row.get("drawSize")
    if isinstance(v, list):
        vv = [x for x in v if isinstance(x, (int, float))]
        return max(vv) if vv else None
    return v if isinstance(v, (int, float)) else None


def mod_badge(mod: str) -> str | None:
    """Only the rare, hard case gets the badge — measured, the softer tiers would
    sit on ~45% of rows and wallpaper the marker. They ride the mod line instead."""
    if mod in MOD_DIES:
        return ("Its mod is being retired — keeping this creature means porting it "
                "into our own files first.")
    return None


def mod_line(mod: str) -> str:
    if mod in MOD_SUNSET:
        return (f"from {mod} — a donor mod being wound down; anything kept gets "
                "ported to our own files")
    if mod in MOD_FEW:
        return f"from {mod} — a mod that now contributes only a few surviving things"
    return f"from {mod or 'an unknown mod'}"


# band words → the scale class the roster itself asked for
BAND_SMALL = re.compile(r"grain|small|vermin|runway|trace|floor-vermin|ship-vermin", re.I)
BAND_MED = re.compile(r"medium|interface|tunnel", re.I)
BAND_LARGE = re.compile(r"\blarge\b|brake", re.I)
BAND_TITAN = re.compile(r"huge|giant|megafauna|landform|colossus|leviathan|titan", re.I)


def band_allowed(band: str) -> set[str] | None:
    b = str(band or "")
    if BAND_SMALL.search(b):
        return {"small"}
    if BAND_MED.search(b):
        return {"medium"}
    if BAND_TITAN.search(b):
        return {"large", "titan"}
    if BAND_LARGE.search(b):
        return {"large"}
    return None


ORDER = ["small", "medium", "large", "titan"]


def advise_bin(measured: str | None, band: str) -> tuple[str | None, str]:
    """-> (advised bin, plain sentence about grow/shrink)."""
    if measured is None:
        return None, "I could not measure its real size, so no size advice."
    allowed = band_allowed(band)
    if not allowed or measured in allowed:
        return measured, "keeps its current size."
    target = min(allowed, key=lambda b: abs(ORDER.index(b) - ORDER.index(measured)))
    verb = "grown" if ORDER.index(target) > ORDER.index(measured) else "shrunk"
    return target, (f"the roster wants it {BIN_LABEL[target]}, so it would be "
                    f"{verb} from its current {BIN_LABEL[measured]} size.")


# ═══════════════════════════════════ per-row attachments (was confidence[] rows)
# The open calls that belong ON a creature row rather than as a separate card.
ATTACH: dict[tuple[str, str], str] = {
    ("dune_sea + deep_desert", "GraniteSlug"):
        "The sheet bans a mineralized, shiny look here. It is stone-named but reads "
        "matte and dusty to me — judge by the picture; Out if it reads shiny to you.",
    ("dune_sea + deep_desert", "AA_BoulderMit"):
        "The sheet bans a mineralized, shiny look here. It reads like a dusty boulder "
        "to me — judge by the picture; Out if it reads shiny to you.",
    ("the_forge", "Beldon"):
        "The biome sheet rules it a placid gas-grazer, but as shipped it hunts. We "
        "will strip the hunting behaviour to match the sheet — say in the note if "
        "you would rather keep it dangerous.",
    ("the_rust_cathedral", "Mynock"):
        "This is the mynock's third named home (with the Scarlands and the Fall "
        "Line). An earlier trim said two homes at most; fliers crossing biomes was "
        "the excuse for a third. Out here enforces the trim.",
    ("the_scarlands", "Mynock"):
        "The prep once suggested other homes for the mynock; the frozen sheet claims "
        "it here, and I landed this as its first true home. Move it if you disagree.",
    ("the_rust_cathedral", "Ling_Cockroach"):
        "A cockroach is a nameable Earth animal — but your own sheet note says it "
        "'might work here after all'. Kept at trace on your word; the art verdict "
        "is the real test.",
    ("the_sump", "AA_Bumbledrone"):
        "Kept for the honey economy after some back-and-forth — Out here if the "
        "hives feel wrong for the Sump.",
    ("the_webwork", "Wyyyschokk"):
        "Its spawn rate is deliberately moderate-but-low so the wood stays eerily "
        "silent: one lethal spider over a near-empty cast. Note a number if you "
        "want it more or less present.",
    ("wasteland", "SW_Electrictick"):
        "Open idea from the prep: slow it to walking pace and promote it to a "
        "signature of the brine pools. Note yes/no if you have a view.",
    ("terminator_sea + the_grey_deep", "AA_Aerofleet"):
        "The deep bans glow below the surface. This drifts at the shore, above it — "
        "if its art reads glowing to you, say so and it moves or goes.",
}

# nightside art-ban sentence for the goo shelf
NIGHTSIDE_ART = ("The nightside bans eyes, glow, and any ordinary animal silhouette. "
                 "Your art verdict IS that test — redo or Out if it reads as a "
                 "creature at a glance.")
NIGHTSIDE_SHELF = {"AA_TetraSlug", "AA_BoulderMit", "AA_SummitCrab", "AA_GreenGoo",
                   "AA_RedGoo", "AA_CrystalMit", "AA_Slurrypede", "AA_Terramorph",
                   "AA_PebbleMit"}
WEEPING_COMB = {"ColossusToad", "Ollopom", "Boma"}
WEEPING_ART = ("The Weeping Stones' comb-silhouette rule is an art test no stat can "
               "pass — your art verdict here is that test.")


# ═══════════════════════════════════════════════════════ question cards (fauna)
CARDS = [
    {
        "id": "q:desert:dewback-blurrg-mounts",
        "sheet_key": "desert",
        "label": "Dewback and Blurrg — bring them back as desert mounts?",
        "q": "Should Dewback and Blurrg go back into the desert as slow herd mounts?",
        "trade": "They were dropped because the data flags them as predators — but "
                 "that flag is unreliable on these two, and they read as omnivore "
                 "mounts. Keeping them adds two Star Wars staples to the desert; "
                 "dropping them keeps the no-pursuit rule airtight.",
        "rec": "Bring them in as slow mounts — I judged from what they are, not the "
               "unreliable flag. In = add them to the desert; Out = leave them out.",
        "prefill": "in",
    },
    {
        "id": "q:the_fever_wood:giant-ants-art",
        "sheet_key": "the_fever_wood",
        "label": "The Fever Wood's Ants — is the Giant Ants art usable?",
        "q": "The Fever Wood's raider Ants would be built on the Giant Ants mod's "
             "creature — is that art good enough to carry them?",
        "trade": "Its stats fit (person-sized, walking pace, hunts). If the art "
                 "reads as a cheap cartoon ant, the Fever Wood's signature threat "
                 "looks silly; commissioning new art costs a queue item.",
        "rec": "Judge it by eye when it next appears; they raid from off-map, so "
               "nothing on this sheet moves either way. In = use the mod's art for "
               "now; Out = commission our own; Decide later is fine.",
        "prefill": "later",
        "open_note": "left undecided on purpose — this is an eye call only you can make.",
    },
    {
        "id": "q:the_rot:strange-cavern-keeps",
        "sheet_key": "the_rot",
        "label": "The Rot — do the strange cavern animals stay?",
        "q": "The Rot kept its glow bat, cave spider, bovine beetle, pillbug and "
             "slugs — does that stand against the stricter reading that everything "
             "there must be hybrid-or-out?",
        "trade": "Your own sheet listed them as 'keep the strange'. Read strictly, "
                 "the ban would drop them all to the no-home pool and the Rot opens "
                 "nearly empty.",
        "rec": "Keep them — they are fungal-cavern creatures, which is what the Rot "
               "IS. In = they stay; Out = they all drop to the no-home pool.",
        "prefill": "in",
    },
    {
        "id": "q:wreck_fields:premise",
        "sheet_key": "wreck_fields",
        "label": "The Wreck Fields — rule the premise: live, powered wrecks?",
        "q": "Do the Wreck Fields get live powered wrecks (and with them a fauna of "
             "cavity-nesters, heat-homing hunters and one hull-breaking giant)?",
        "trade": "Ruling yes commissions a whole new-art wanted-list (nothing "
                 "existing fits). Ruling no leaves the Wreck Fields as quiet salvage "
                 "terrain with the little it has.",
        "rec": "I lean yes — it is the biome's whole identity — but every creature "
               "for it must be drawn from scratch, so it is a budget call. In = "
               "rule yes and queue the wanted-list; Out = quiet salvage terrain.",
        "prefill": "later",
        "open_note": "left undecided on purpose — it commissions a whole art wave.",
    },
    {
        "id": "q:nightside:empty-is-correct",
        "sheet_key": "nightside_ice",
        "label": "The Nightside — confirm: nearly empty is the design?",
        "q": "The nightside keeps only a shelf of goo and slug forms at trace "
             "rates — 9 in 10 former residents are gone. Is nearly-empty right?",
        "trade": "Empty is what the sheet asks for ('if a player can tell it is a "
                 "creature before it acts, it is wrong') — but it means whole "
                 "regions where nothing visibly lives. Keeping more texture "
                 "costs the alien emptiness.",
        "rec": "Yes — emptiness is the biome. The art verdicts on the shelf rows "
               "below are the real remaining test. In = confirm; Out = ask me to "
               "refill some texture.",
        "prefill": "in",
    },
]

CARD_GROUP = "Questions for you — the calls I could not settle"
HOMELESS_OUT = ("Out here = CUT FOR REAL: the creature is removed from the game by "
                "the next Cherry Picker pass.")


# ═══════════════════════════════════════════ homeless recommendation rules (5)
HOMELESS_GROUPS = {
    "cave": ("No home yet → my call: the underground & cave layer (draft roster)",
             "These become the first draft roster for the cave and underground "
             "strata (the Lantern Deeps admits ordinary dark-cave fauna; the rest "
             "await their own sittings). " + HOMELESS_OUT),
    "sea": ("No home yet → my call: the deep seas & underwater layer (draft roster)",
            "These become the first draft roster for the underwater layer — the "
            "deep-sea concept wants shoal grazers, ambushers, pack hunters and "
            "leviathans, and nothing else on the planet fits that brief. "
            + HOMELESS_OUT),
    "dungeon": ("No home yet → my call: dungeon & vault guardians (draft palette)",
                "These never spawn wild — they become guardian stock for the "
                "Assailant complex and the Forsaken vaults. " + HOMELESS_OUT),
    "events": ("No home yet → my call: keep for events & quests only",
               "No wild home anywhere, but worth keeping alive for raids, quests "
               "and one-off encounters. " + HOMELESS_OUT),
    "livestock": ("No home yet → my call: livestock & trader stock only",
                  "Never wild — but tameable, productive, or a pack animal, so "
                  "traders and starting herds can carry them. " + HOMELESS_OUT),
    "cut": ("No home yet → my call: cut for real",
            "I recommend actually removing these — recognisably Earth, from a "
            "retiring mod, or adding nothing this planet wants. Leaving the row "
            "as-is agrees to the cut; In keeps it alive in the events reserve "
            "instead. " + HOMELESS_OUT),
}
HOMELESS_ORDER = ["cave", "sea", "dungeon", "events", "livestock", "cut"]

# curated overrides: defName -> (groupKey, one-line reason)
HOMELESS_OVERRIDES = {
    "Rancor": ("dungeon", "THE lair monster — a Rancor belongs behind a vault door, "
                          "not on open ground."),
    "Gundark": ("dungeon", "Classic close-quarters bruiser — vault guardian stock."),
    "Roggwart": ("dungeon", "Big keyed-up predator — guardian stock."),
    "KellDragon": ("dungeon", "Arena beast by lore — guardian stock."),
    "Drexl": ("events", "Too big and loud for any roster — a raid/quest monster."),
    "Vapaad": ("events", "Fast pursuit giant no biome allows — event monster."),
    "Aiwha": ("sea", "A flying whale — the Twilight Sea's skylights are the only "
                     "place it makes sense."),
    "Thranta": ("events", "Sky beast — keep for sky/trade flavour events."),
    "Orray": ("livestock", "Docile mount by lore — trader and herd stock."),
    "Falumpaset": ("livestock", "Pack beast by lore — trader stock."),
    "Fambaa": ("livestock", "Gungan draft beast — trader stock, and a body donor "
                            "for the shrubland giant."),
    "Tauntaun": ("livestock", "THE cold-weather mount — starting/trade stock for "
                              "cold maps."),
    "Bordok": ("livestock", "Pack pony — trader stock."),
    "Eponee": ("livestock", "Riding stock."),
    "Tusken_Massiff": ("events", "Raider companion beast — spawns with raids, not wild."),
    "Akk": ("events", "Raider war-beast — event stock."),
    "PaintedSpat": ("events", "Decorative rarity — quest reward stock."),
    "Tooke": ("events", "Vermin icon — quest/texture events."),
    "SandWorm_Thing": ("events", "I could not measure it at all (its stats never "
                                 "resolved) — park it in events until someone looks."),
    "RUT_LongHunger": ("events", "Ours, and stats never resolved — park in events; "
                                 "it is campaign material, not roster filler."),
}

SW_SEA = re.compile(r"^RSW_|Sando", re.I)
CAVE_NAME = re.compile(r"cave|blind|dark|glow|myco|fungal|spore|crystal|depth|sonar|murk|dusk|night", re.I)
SEA_NAME = re.compile(r"fish|whale|shark|squid|kraken|eel|shrimp|crab|reef|aqua|sea|tide|coral|jelly|octop|cephal|leviath", re.I)
EARTHISH = re.compile(
    r"^(Rat|Hare|Boar|WildBoar|Raccoon|Fox|Wolf|Bear|Deer|Elk|Cow|Pig|Goat|Sheep|"
    r"Chicken|Duck|Goose|Turkey|Cat|Dog|Horse|Donkey|Mule|Alpaca|Bison|Caribou|"
    r"Chinchilla|Cougar|Gazelle|GuineaPig|Husky|Ibex|Iguana|Lynx|Monkey|Ostrich|"
    r"Panther|Rhinoceros|Squirrel|Tortoise|Capybara|Elephant|Megasloth|Cassowary|"
    r"Emu|LabradorRetriever|YorkshireTerrier|Warg|Snowhare|Toucan|Pengu)", re.I)


def homeless_call(row: dict) -> tuple[str, str]:
    """-> (group key, plain reason)."""
    d = row["defName"]
    if d in HOMELESS_OVERRIDES:
        return HOMELESS_OVERRIDES[d]
    mod = row.get("mod") or ""
    label = row.get("label") or d
    name = f"{d} {label}"
    trainable = (row.get("trainability") or "None") != "None"
    produces = bool(row.get("produces"))
    pred = any("predator" in s.get("text", "") for s in row.get("specials") or [])
    bs = row.get("bodySize") or 0

    if mod == "RimMandrake - SW Sea Beasts" or SW_SEA.search(d):
        return "sea", ("Our own sea-beast stock — the seas can only hold a couple "
                       "each, so the rest seed the underwater layer.")
    if SEA_NAME.search(name):
        return "sea", "Reads aquatic — a candidate for the underwater layer."
    if mod == "Biomes! Caverns" or CAVE_NAME.search(name):
        return "cave", ("Cave-adapted stock — a candidate for the underground "
                        "draft roster (many will still fail the eye test there).")
    if mod in ("Vanilla Factions Expanded - Insectoids 2",
               "Insectoids 2 - Isopoda geneline", "Better Infestations (Continued)",
               "They! (Giant Ants)", "Horrors (Continued)"):
        return "dungeon", ("Hive/horror stock — guardian and infestation material, "
                           "never wild spawns.")
    if mod == "Vanilla Genetics Expanded":
        return "events", ("A made creature, not a wild one — genetics-lab and "
                          "quest material; its mechanics are protected, so not a "
                          "cut candidate.")
    if mod in ("Vanilla Quests Expanded - Ancients",
               "Vanilla Quests Expanded - Cryptoforge", "Mo'Events (Continued)"):
        return "events", "Belongs to its quest mod's own events — leave it there."
    if mod in MOD_DIES:
        return "cut", ("Its whole mod is being retired — keeping it would mean "
                       "porting it for no biome that wants it.")
    if EARTHISH.search(d):
        return "cut", ("Recognisably an Earth animal (or a thin retexture of one) "
                       "— exactly what the planet-wide purge removes.")
    if trainable and (produces or not pred) and bs >= 0.8:
        return "livestock", ("Tameable and useful — worth keeping as trader and "
                             "herd stock even with no wild home.")
    if mod == "Star Wars Animal Collection (Continued)":
        return "events", ("Star Wars stock with no legal biome — keep alive for "
                          "raids, caravans and quests while the donor mod winds "
                          "down.")
    if mod in ("Alpha Animals", "Alpha Genes", "Alpha Memes"):
        return "events", ("Strange enough to keep — no biome asked for it, so it "
                          "waits in the events reserve.")
    if pred and bs >= 2:
        return "dungeon", "A big keyed-up predator — guardian stock."
    if mod in ("Core", "Odyssey", "Biotech"):
        return "cut", ("Vanilla stock nothing on this planet asked for — the purge "
                       "takes it.")
    if mod in ("Dark Ages : Beasts and Monsters", "Little Critters",
               "Giant Toads (Continued)", "Erin's Final Fantasy Animals"):
        return "cut", "Fantasy/Earth flavour that fits no sheet — cut."
    return "events", "Nothing wants it wild; parked in the events reserve."


# ═══════════════════════════════════════════════════════════════ data assembly
def load_template() -> str:
    for path in TEMPLATE_CANDIDATES:
        if path.is_file():
            return path.read_text(encoding="utf-8")
    sys.exit("cannot find the review-sheets template (the chrome is not ours to author)")


def read_rosters() -> tuple[list[dict], dict]:
    sheets = []
    for path in sorted(ROSTERS.glob("*.json")):
        if path.name.startswith("_"):
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        sheets.append(doc)
    glob = json.loads((ROSTERS / "_global.json").read_text(encoding="utf-8"))
    return sheets, glob


def pretty_sheet(key: str) -> str:
    words = key.replace("_", " ").split()
    small = {"the", "of", "and"}
    out = " ".join(w if w in small and i else w.capitalize()
                   for i, w in enumerate(words))
    return out.replace(" + ", "  +  ")


def png_size(path: pathlib.Path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:  # noqa: BLE001
        return None


def art_prefill_map() -> dict[str, tuple[str, str]]:
    """defName -> (art verdict, provenance sentence)."""
    out = {}
    try:
        doc = json.loads(ART_DECISIONS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return out
    stamped = bool(doc.get("savedBy"))
    for rid, rec in (doc.get("decisions") or {}).items():
        if not rid.startswith("c:"):
            continue
        verdict = ART_MAP.get(rec.get("decision") or "")
        if verdict:
            src = ("your art-register verdict" if stamped
                   else "the art register's grading (carried your older verdicts)")
            out[rid[2:]] = (verdict, src)
    return out


def build_creature_item(defname: str, reg_row: dict, group: str, item_id: str,
                        art_pre: dict, *, comm=None, why: str = "",
                        extra: list[str] | None = None,
                        band: str = "", zeroed_here: bool = False,
                        prefill: str = "in", contested: bool = False,
                        open_note: str = "") -> dict:
    cells = draw_cells(reg_row)
    mbin = size_bin(cells)
    abin, means = advise_bin(mbin, band)
    art = reg_row.get("art") or {}
    scale = art.get("scale")
    nat = png_size(HERE / scale) if scale else None
    if not reg_row.get("statsResolved", True):
        cells, mbin, abin = None, None, None
        means = "I could not measure this creature at all — its stats never resolved."

    bits = [size_phrase(cells, reg_row.get("bodySize")),
            speed_phrase(reg_row.get("moveSpeed"))]
    bits += threat_phrases(reg_row)
    if comm is not None:
        bits.append(rarity_phrase(comm))
    sentences = []
    if why:
        sentences.append("Why it's here: " + plain(why))
    for s in extra or []:
        sentences.append(s)
    if zeroed_here:
        sentences.append("Heads-up: an old content cut still blocks this creature "
                         "from spawning here — the cut gets lifted when this row "
                         "lands as In.")
    badge = mod_badge(reg_row.get("mod") or "")
    item = {
        "id": item_id,
        "label": (reg_row.get("label") or defname),
        "group": group,
        "thumb": art.get("detail"),
        "effect": " · ".join(bits),
        "sentences": sentences,
        "modLine": mod_line(reg_row.get("mod") or ""),
        "badge": badge,
        "prefill": prefill,
        "contested": contested,
        "cells": cells,
        "sizeBinPrefill": abin or "",
        "sizeMeans": means,
        "hasSize": abin is not None,
        "hasArt": True,
    }
    if open_note:
        item["openNote"] = open_note
    ap = art_pre.get(defname)
    if ap:
        item["artPrefill"], item["artSrc"] = ap
    else:
        ppc = art.get("pxPerCell")
        if scale is None:
            item["artPrefill"], item["artSrc"] = "redo", (
                "no picture could be rendered for it at all")
        elif ppc is not None and ppc < 0.7:
            item["artPrefill"], item["artSrc"] = "improve", (
                "the sprite is blurry at the size the game draws it")
        else:
            item["artPrefill"], item["artSrc"] = "keep", "no visible defect"
    if nat and scale:
        item["panel"] = {"file": scale, "w": nat[0], "h": nat[1],
                         "shown": art.get("shownPct") or 100}
    else:
        item["sentences"].append("I could not render this one to scale — the small "
                                 "picture is NOT at true size.")
    return item


def scale_groups(items: list[dict]) -> None:
    """One uniform px-per-square inside each group; the same colonist is in every
    panel, so uniform panel scale = true relative scale."""
    groups: dict[str, list[dict]] = {}
    for it in items:
        if it.get("panel"):
            groups.setdefault(it["group"], []).append(it)
    for rows in groups.values():
        max_cells = max(max(it["panel"]["w"], it["panel"]["h"])
                        / (PANEL_PPC * it["panel"]["shown"] / 100.0)
                        for it in rows)
        target = min(PANEL_PPC, GROUP_MAX_PX / max_cells)
        for it in rows:
            p = it["panel"]
            k = target / (PANEL_PPC * p["shown"] / 100.0)
            it["panelW"] = max(24, int(round(p["w"] * k)))
            it["panelH"] = max(16, int(round(p["h"] * k)))
            it["panelPpc"] = round(target, 1)
            it["panelSrc"] = p["file"]
            del it["panel"]


def build_items(sheets: list[dict], glob: dict, reg: dict) -> tuple[list[dict], dict]:
    art_pre = art_prefill_map()
    cards: list[dict] = []
    biome_rows: list[dict] = []
    homeless_rows: list[dict] = []

    sheet_tiles = {}
    for doc in sheets:
        sheet_tiles[doc["sheet"]] = doc.get("tiles")

    for card in CARDS:
        cards.append({
            "id": card["id"],
            "label": card["label"],
            "group": CARD_GROUP,
            "thumb": None,
            "effect": card["q"],
            "card": {"q": card["q"], "trade": card["trade"], "rec": card["rec"]},
            "prefill": card["prefill"],
            "contested": True,
            "hasSize": False, "hasArt": False,
            **({"openNote": card["open_note"]} if card.get("open_note") else {}),
        })

    for doc in sheets:
        key = doc["sheet"]
        tiles = doc.get("tiles")
        gname = pretty_sheet(key) + (f" — {tiles:,} tiles" if isinstance(tiles, int) else "")
        own_defs = set(doc.get("defNames") or [])
        tunes: dict[str, list[str]] = {}
        for adj in doc.get("stat_adjustments") or []:
            tunes.setdefault(adj["def"], []).append(
                f"{adj.get('field')} {num(adj.get('from'))} → {num(adj.get('to'))}")

        for entry in doc.get("fauna") or []:
            defname = entry["def"]
            row = reg.get(defname)
            if row is None:
                continue
            extra = []
            if tunes.get(defname):
                extra.append("Already tuned to fit this biome: "
                             + "; ".join(tunes[defname]) + ".")
            note = entry.get("note")
            if note and str(note).lower() not in ("icon",):
                extra.append(plain(str(note)))
            att = ATTACH.get((key, defname))
            if att:
                extra.append(att)
            if key == "nightside_ice" and defname in NIGHTSIDE_SHELF:
                extra.append(NIGHTSIDE_ART)
            if key == "weeping_stones" and defname in WEEPING_COMB:
                extra.append(WEEPING_ART)
            ubex = entry.get("ubiquity_exception")
            if ubex:
                extra.append("This one is an exception I took against the "
                             "everywhere-at-once trim: " + plain(str(ubex)))
            zeroed = any(b.get("biomeDef") in own_defs
                         for b in (row.get("zeroedBiomes") or []))
            contested = bool(ubex or att
                             or re.search(r"CONFLICT|flag", str(entry), re.I))
            biome_rows.append(build_creature_item(
                defname, row, gname, f"fauna:{key}:{defname}", art_pre,
                comm=entry.get("commonality"), why=entry.get("law") or "",
                extra=extra, band=entry.get("band") or "", zeroed_here=zeroed,
                prefill="in", contested=contested))

    # ── the homeless pool ─────────────────────────────────────────────────────
    rostered = {it["id"].split(":")[-1] for it in biome_rows}
    for defname in glob.get("reserve_for_events") or []:
        row = reg.get(defname)
        if row is None or defname in rostered:
            continue
        if row.get("kindOf") not in ("animal", "insectoid"):
            continue
        if row.get("cut") or row.get("modDropped"):
            continue
        gkey, reason = homeless_call(row)
        prefill = "out" if gkey == "cut" else "in"
        homeless_rows.append(build_creature_item(
            defname, row, HOMELESS_GROUPS[gkey][0],
            f"homeless:{defname}", art_pre,
            extra=["My call: " + reason], prefill=prefill))

    # sort: cards first, then biome groups A→Z with smallest→largest inside,
    # then the homeless groups in fixed order
    biome_rows.sort(key=lambda it: (it["group"],
                                    it["cells"] if it["cells"] is not None else 99,
                                    it["label"].lower()))
    horder = {HOMELESS_GROUPS[k][0]: i for i, k in enumerate(HOMELESS_ORDER)}
    homeless_rows.sort(key=lambda it: (horder[it["group"]],
                                       it["cells"] if it["cells"] is not None else 99,
                                       it["label"].lower()))
    items = cards + biome_rows + homeless_rows
    scale_groups(items)

    counts = {
        "rows": len(items),
        "cards": len(cards),
        "biomeRows": len(biome_rows),
        "homeless": len(homeless_rows),
        "biomes": len({it["group"] for it in biome_rows}),
        "contested": sum(1 for it in items if it.get("contested")),
        "cutRec": sum(1 for it in homeless_rows if it["prefill"] == "out"),
        "badged": sum(1 for it in items if it.get("badge")),
        "unsized": sum(1 for it in items
                       if it.get("hasArt") and not it.get("hasSize")),
    }
    return items, counts


# ═══════════════════════════════════════════════════════════ page text + chrome
CRITERION = (
    "Rows are what the biome sheets ADMIT — a lawfulness test, not a worth test. "
    "Sizes and speeds are measured from the game's own data; every spawn rate, "
    "every size-bin suggestion and every homeless recommendation is my call, and "
    "your overrules are the point."
)

INVENTED = [
    "Size bins are mine: small < 1.0 squares on screen · medium 1.0–2.2 (a person "
    "is 1.5) · large 2.2–5.0 · TITAN over 5.0. FOUNDRY rescales each kept creature "
    "to the bin you pick, so the bin buttons are design intent, not labels.",
    "The retirement flag: the ⚑ badge fires only when a creature's mod is "
    "actually named for retirement in the audit (rare, so it stays visible). "
    "Softer states — the Star Wars donor being wound down, or a mod keeping only "
    "a few surviving things (a quarter or less of its content) — are written on "
    "each row's mod line instead, because they cover nearly half the sheet.",
    "True-scale rule: every panel in a biome group shares one px-per-game-square, "
    "chosen so the group's biggest creature fits about 460px. Scale is honest "
    "WITHIN a group; different groups use different zoom levels.",
    "Homeless recommendations follow my own rules: sea-named stock to the "
    "underwater layer, cave stock underground, hive and horror stock to dungeon "
    "guardian duty, tameable-and-useful to livestock/trade, recognisably-Earth "
    "and retiring-mod stock to the cut list. The strange-strata groups double as "
    "DRAFT rosters — no roster file exists for those places yet.",
    "Every spawn rate on every row is agent-chosen — nothing measures how common "
    "a creature should be.",
    "Where a roster's own band name (grain, medium, huge…) disagrees with the "
    "creature's measured size, the size-bin suggestion follows the roster's wish "
    "and the row says whether that grows or shrinks the creature.",
    "The creature data's 'flies' flag is broken and juvenile sizes are absent, so "
    "every flier and life-stage judgement here is by eye, not by data.",
]


def brief_html(counts: dict) -> str:
    return (
        "<p><b>What this is:</b> every wild creature going INTO each of Ash'karr's "
        f"biomes — <b>{counts['biomeRows']}</b> creatures across "
        f"<b>{counts['biomes']}</b> biomes — plus <b>{counts['homeless']}</b> "
        "creatures that currently have no home anywhere, each with my "
        "recommendation. Who was evicted from where is deliberately not shown: "
        "this sheet is about who is IN.</p>"
        "<p><b>The four controls on a creature row:</b> "
        "<b>In</b> — it stays where the row says · "
        "<b>Move</b> — somewhere else: <i>name the biome in the note</i> · "
        "<b>Out</b> — it leaves (in a biome group that drops it to the no-home "
        "pool; <b>in the no-home section Out = CUT FOR REAL</b> — removed from "
        "the game by the next content pass) · "
        "<b>Decide later</b> — parked, on purpose. "
        "Then <b>size</b>: small / medium / large / TITAN is what the creature "
        "SHOULD be — pick a different bin and it gets rescaled to match "
        "(small &lt; 1 square on screen · medium 1–2.2, a person is 1.5 · large "
        "2.2–5 · TITAN 5+). "
        "And <b>art</b>: keep / improve / redo drives the redraw queue.</p>"
        "<p><b>The pictures are at true relative scale.</b> Inside each biome "
        "group, every creature and the white colonist figure share one zoom "
        "level, smallest creature first — some will be huge and some tiny, and "
        "that is the point. Click any small picture for a close-up (the close-up "
        "is NOT to scale).</p>"
        f"<p><b>Start with the questions at the top</b> ({counts['cards']} cards) "
        f"and the {counts['contested']} rows marked as the toughest calls. "
        f"{counts['badged']} rows carry a flag because their mod is on its way "
        "out. The note beats every button — one sentence about WHY you overruled "
        "me teaches more than the click.</p>"
    )


RENDER_BLOCK = r"""
<style>
  .label .id{display:none}
  .scalepanel{margin:6px 0 2px;overflow-x:auto;max-width:100%}
  .scalepanel img{display:block;border-radius:4px;border:1px solid var(--line)}
  .scalecap{font-size:10px;color:var(--dim);margin:1px 0 3px}
  .plainlines{font-size:12px;color:#aeb7c4;margin-top:3px}
  .plainlines div{margin-top:2px}
  .modline{font-size:10.5px;color:#5f6b7a;margin-top:2px}
  .badgeline{font-size:11px;color:var(--warn);margin-top:3px}
  .qcard{border:1px solid #2f4358;background:#0d151d;border-radius:6px;
         padding:7px 10px;margin-top:4px;font-size:12.5px}
  .qcard b{color:var(--link)}
  .qcard .rec{color:var(--accent)}
  .xtr{display:flex;gap:4px;align-items:center;margin-top:6px;flex-wrap:wrap}
  .xlab{font-size:10.5px;color:var(--dim);min-width:28px}
  .xtr button{cursor:pointer;background:#161a20;border:1px solid var(--line);
              border-radius:5px;padding:2px 9px;font-size:11px;color:var(--dim)}
  .xtr button:hover{border-color:#3d4653;color:var(--ink)}
  .xtr button.sel{color:#0b0d10;font-weight:700;border-color:transparent}
  .xmeans{font-size:10.5px;color:var(--dim)}
  .xovr{font-size:10px;color:var(--accent)}
</style>
<script id="RENDER">
  window.SIZE_BINS = [["small","small","#6aa6e8"],["medium","medium","#5ac37f"],
                      ["large","large","#e8b64c"],["titan","TITAN","#e06c6c"]];
  window.ART_OPTS  = [["keep","keep","#5ac37f"],["improve","improve","#e8b64c"],
                      ["redo","redo","#e06c6c"]];
  window.itemBody = it => {
    const d = (typeof DEC === 'object' && DEC[it.id]) || {};
    let h = '';
    if (it.card) {
      h += '<div class="qcard"><div><b>The question:</b> ' + esc(it.card.q) + '</div>'
        + '<div style="margin-top:4px"><b>The tradeoffs:</b> ' + esc(it.card.trade) + '</div>'
        + '<div class="rec" style="margin-top:4px"><b>My recommendation:</b> ' + esc(it.card.rec) + '</div></div>';
      return h;
    }
    if (it.panelSrc) {
      h += '<div class="scalepanel"><img src="' + esc(it.panelSrc) + '" width="' + it.panelW
        + '" height="' + it.panelH + '" loading="lazy" decoding="async" alt=""></div>'
        + '<div class="scalecap">to scale for this group</div>';
    }
    h += '<div class="effect">' + esc(it.effect || '') + '</div>';
    if ((it.sentences || []).length)
      h += '<div class="plainlines">' + it.sentences.map(s => '<div>' + esc(s) + '</div>').join('') + '</div>';
    if (it.badge) h += '<div class="badgeline">⚑ ' + esc(it.badge) + '</div>';
    if (it.modLine) h += '<div class="modline">' + esc(it.modLine) + '</div>';
    if (it.hasSize) {
      const cur = d.sizeBin !== undefined && d.sizeBin !== '' ? d.sizeBin : (it.sizeBinPrefill || '');
      h += '<div class="xtr"><span class="xlab">size</span>'
        + SIZE_BINS.map(([k,lab,col]) => '<button data-bin="' + k + '"'
            + (k === cur ? ' class="sel" style="background:' + col + '"' : '')
            + '>' + lab + '</button>').join('')
        + '<span class="xmeans">' + esc(it.sizeMeans || '') + '</span>'
        + (d.sizeBin && it.sizeBinPrefill && d.sizeBin !== it.sizeBinPrefill
            ? '<span class="xovr">⟲ you changed this (I suggested ' + esc(it.sizeBinPrefill) + ')</span>' : '')
        + '</div>';
    } else if (!it.card && it.hasArt) {
      h += '<div class="xtr"><span class="xmeans">' + esc(it.sizeMeans || '') + '</span></div>';
    }
    if (it.hasArt) {
      const cura = d.art !== undefined && d.art !== '' ? d.art : (it.artPrefill || '');
      h += '<div class="xtr"><span class="xlab">art</span>'
        + ART_OPTS.map(([k,lab,col]) => '<button data-art="' + k + '"'
            + (k === cura ? ' class="sel" style="background:' + col + '"' : '')
            + '>' + lab + '</button>').join('')
        + '<span class="xmeans">' + (d.art && it.artPrefill && d.art !== it.artPrefill
            ? '⟲ was ' + esc(it.artPrefill) + ' — ' : '')
        + esc(it.artSrc || '') + '</span></div>';
    }
    return h;
  };
</script>
"""

WIRE_BLOCK = r"""
<script>
"use strict";
/* extra wiring: size-bin + art buttons persist into the same per-row record the
   sidecar already merges; a click re-renders the whole row so every control and
   chip stays true. */
(function () {
  const fm = document.getElementById('fmark');
  if (fm) {
    const c = fm.querySelector('option[value="contested"]');
    if (c) c.textContent = 'toughest calls only';
    const inf = fm.querySelector('option[value="inferred"]');
    if (inf) inf.remove();
  }
  const rerender = id => {
    const node = document.querySelector('.row[data-id="' + cssEsc(id) + '"]');
    const it = byId.get(id);
    if (!node || !it) return;
    node.outerHTML = card(it);
    const fresh = document.querySelector('.row[data-id="' + cssEsc(id) + '"] .note');
    if (fresh && fresh.value) { fresh.style.height = 'auto';
      fresh.style.height = Math.min(fresh.scrollHeight, 160) + 'px'; }
  };
  /* patchRow only repaints the verdict buttons; our rows carry more. */
  const origPatch = patchRow;
  patchRow = function (id) { origPatch(id); rerender(id); };

  document.getElementById('list').addEventListener('click', e => {
    const btn = e.target.closest('[data-bin],[data-art]');
    if (!btn) return;
    if (frozen) { showErr('This sheet is frozen — decisions are read-only.'); return; }
    const rowNode = btn.closest('.row');
    if (!rowNode) return;
    const id = rowNode.dataset.id, it = byId.get(id);
    if (!it) return;
    const rec = DEC[id] || (DEC[id] = { decision: '', note: '', prefill: (it.prefill ?? null) });
    const before = JSON.parse(JSON.stringify(rec));
    if (btn.dataset.bin !== undefined) {
      rec.sizeBin = (rec.sizeBin === btn.dataset.bin) ? '' : btn.dataset.bin;
      if (rec.sizeBinPrefill === undefined) rec.sizeBinPrefill = it.sizeBinPrefill || '';
    } else {
      rec.art = (rec.art === btn.dataset.art) ? '' : btn.dataset.art;
      if (rec.artPrefill === undefined) rec.artPrefill = it.artPrefill || '';
    }
    undoStack.push({ entries: [{ id, before }] });
    redoStack.length = 0;
    queue(id);
    rerender(id);
  });
})();
</script>
"""


def fill(template: str, config: dict, items: list[dict]) -> str:
    out = re.sub(
        r'(<script id="CONFIG" type="application/json">\n).*?(\n</script>)',
        lambda m: m.group(1) + json.dumps(config, indent=1, ensure_ascii=False) + m.group(2),
        template, count=1, flags=re.S,
    )
    out = re.sub(
        r'(<script id="ITEMS" type="application/json">\n).*?(\n</script>)',
        lambda m: m.group(1) + json.dumps(items, ensure_ascii=False) + m.group(2),
        out, count=1, flags=re.S,
    )
    anchor = '<script>\n"use strict";'
    if anchor not in out:
        sys.exit("template changed shape: no main <script> anchor")
    out = out.replace(anchor, RENDER_BLOCK.strip() + "\n\n" + anchor, 1)
    return out.replace("</body>", WIRE_BLOCK.strip() + "\n</body>", 1)


def guard_decisions(path: pathlib.Path, force: bool) -> None:
    if not path.is_file() or force:
        return
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if doc.get("savedBy") or doc.get("writeCount") or doc.get("frozen"):
        sys.exit(
            f"REFUSING to overwrite {path.name}: it carries savedBy/writeCount/"
            "frozen — keys only the sheet's own plumbing writes. These are the "
            "OWNER's decisions.\nRe-run with "
            "--i-know-this-overwrites-the-owners-decisions to discard them."
        )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sheet-only", action="store_true")
    ap.add_argument("--i-know-this-overwrites-the-owners-decisions",
                    action="store_true", dest="force")
    ap.add_argument("--template")
    args = ap.parse_args()
    if args.template:
        TEMPLATE_CANDIDATES.insert(0, pathlib.Path(args.template))

    sheets, glob = read_rosters()
    reg = {r["defName"]: r
           for r in json.loads(REGISTER.read_text(encoding="utf-8"))["rows"]}
    items, counts = build_items(sheets, glob, reg)

    for it in items:
        if it.get("thumb") and not (HERE / it["thumb"]).is_file():
            it["thumb"] = None

    config = {
        "sheetId": "fauna_assignment_register",
        "title": "Fauna of Ash'karr — who lives where",
        "subtitle": f"{counts['biomeRows']} creatures in {counts['biomes']} biomes · "
                    f"{counts['homeless']} with no home · {counts['cards']} questions",
        "briefHtml": brief_html(counts),
        "criterion": CRITERION,
        "invented": INVENTED,
        "posture": {
            "mode": "blacklist",
            "explain": "Everything stands as recommended unless you overrule it. "
                       "Biome rows are already-landed data; a homeless row's "
                       "recommendation is carried out as printed — and Out on a "
                       "homeless row removes the creature from the game for real.",
        },
        "options": [
            {"key": "in",    "label": "In",           "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "move",  "label": "Move",         "hotkey": "2", "color": "#6aa6e8", "counts": "in"},
            {"key": "out",   "label": "Out",          "hotkey": "3", "color": "#e06c6c", "counts": "out"},
            {"key": "later", "label": "Decide later", "hotkey": "4", "color": "#98a2b3"},
        ],
        "groupLabel": "section",
        "media": True,
        "decisionsFile": DECISIONS.name,
        "decisionsPath": NATIVE_DIR + "\\" + DECISIONS.name,
        "sheetPath": NATIVE_DIR + "\\" + SHEET.name,
    }

    SHEET.write_text(fill(load_template(), config, items), encoding="utf-8")
    print(f"wrote {SHEET.name}: {counts}")

    if args.sheet_only:
        return 0
    guard_decisions(DECISIONS, args.force)
    doc = {
        "sheet": "fauna_assignment_register",
        "posture": "blacklist",
        "postureMeaning": "Stands as recommended unless overruled. Out on a "
                          "homeless row = cut from the game for real.",
        "criterion": CRITERION,
        "generatedBy": "gen_fauna_assignment_sheet.py (2026-09-09 rulings rebuild)",
        "generatedFrom": "design/Jawa/worldbuilding/biomes/rosters/*.json",
        "invented": INVENTED,
        "decisions": {
            it["id"]: {
                "decision": it["prefill"],
                "prefill": it["prefill"],
                "note": it.get("openNote") or "",
                **({"sizeBin": it["sizeBinPrefill"],
                    "sizeBinPrefill": it["sizeBinPrefill"]} if it.get("hasSize") else {}),
                **({"art": it["artPrefill"],
                    "artPrefill": it["artPrefill"]} if it.get("hasArt") else {}),
            }
            for it in items
        },
    }
    DECISIONS.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n",
                         encoding="utf-8")
    print(f"wrote {DECISIONS.name} ({len(doc['decisions'])} pre-filled rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
