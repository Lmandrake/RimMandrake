# CANONICAL_SAVE_SCENARIO_MISMATCH_1 — second-look verification, 2026-09-19

Filed by a sibling FOUNDRY window from `WORLDGEN_CLICK_RECONCILE_1` check 3. This note is an
independent second look, requested because a claim of "the canonical save is broken" about
the project's single shipped artifact needs one before it reaches the owner. **The raw facts
in the original filing (scenario name, stock items, founder names, extra colonists) are not
re-disputed here — they were read directly from the file and are correct.** What follows is
the provenance investigation: WHY those facts are true, and whether that means corruption,
drift, or something else.

## Conclusion: none of the three clean hypotheses — a fourth, better-evidenced one

Three hypotheses were up for testing:
- **A (mundane drift):** the save has been played for real since 2026-09-12, so mismatches
  are normal accumulation, not a defect.
- **B (never wired):** `Scenario_Utinni.xml` was designed on paper but never actually built.
- **C (accidental overwrite):** a once-correct save was clobbered by a later `save_game`
  call during testing.

**B is false as stated** — `src/RimUtinni/UtinniPatches/Defs/ScenarioDefs/Scenario_Utinni.xml`
(defName `RUT_Jawa_UtinniStart`) exists, is fully built (six-founder xenotype config page,
the clan Ikee, `Standing` arrival, opening dialog), is deployed to the live Mods folder
(`.../Mods/UtinniPatches/Defs/ScenarioDefs/Scenario_Utinni.xml`), and its owning mod
`mandrake.rut.patches` is active in the live `ModsConfig.xml` (confirmed via `ET.parse`,
not a scan). Last content change 2026-09-11, i.e. finished and live before the save's
2026-09-12 creation date. So "the ScenarioDef doesn't exist / isn't wired" is not the gap.

**C is false** — there is no earlier "pristine" version of this save anywhere that shows the
correct scenario/founders/stock. Checked every predecessor in the lineage:
- `Saves/_cleanup_archive_2026-09-14/CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-biome-world-switch-2026-09-12`
  (same day as creation, hours after) — already vanilla `Crashlanded`, already 0 hits for
  "Sekki"/"Vosh", already carries Hernan/Ashly/Brandy.
- `Saves/_cleanup_archive_2026-09-14/CANONICAL_ASHKARR_2026-09-09.rws` (three days before
  "creation") — same vanilla scenario, same 0 Sekki/Vosh, same names.
- `Saves_archive_2026-09-09/EXPERIMENTAL_shipcrewed_2026-09-09.rws` — the save
  `PLAYER_START_SITE_1.md` describes as "ship + cleared deck + **Founders**, paused,
  pre-fuel" — is *also* vanilla `Crashlanded` with 0 Sekki/Vosh and the same Hernan/Ashly/
  Brandy population. "Founders spawned/named aboard" meant founders were added to the
  existing crashlanded colony's population, not that the colony was replaced by them.
- A `grep -c Sekki` sweep of every top-level file in the live `Saves/` folder returns zero
  matches everywhere. **No save that has ever existed on this machine contains Sekki Vosh,
  the six-founder cast as a closed set, or the Jawa starting stock.**

**A is half right, half wrong.** The save has genuinely been used and re-saved constantly —
`GRAVSHIP_MAP_SIZE_1`, `WORLD_NAME_FIXES_1` and five `.bak-pre-*` files from the last two
days alone confirm ongoing bridge sessions really do drive this exact file, and
`WORLDGEN_CLICK_RECONCILE_1`'s own note (ideo shifting from a placeholder "Astropolitan"
culture to "the Ascendant Genome" mid-save-history) is independent evidence of real change
over time. **But** the specific defects named in the filing — vanilla scenario, missing
Sekki, vanilla stock, Hernan/Ashly/Brandy — are not drift from playing forward. They are
present, byte-for-byte the same shape, in the earliest available snapshot from the day of
creation and in every predecessor back to at least 2026-09-09. Ongoing play only added to
an already-mismatched base (e.g. the Brandy toxic-buildup death, the "jotun adventurer"
join letter) — it did not create the mismatch.

## What actually happened (read from `PLAYER_START_SITE_1.md` + the save lineage)

`SCENARIO_SPEC.md`'s R25 "who does what" table calls for the owner to **start a fresh game
from `Scenario_Utinni.xml`**, with BUILD placing the gravship and authoring the six founders
via the bridge/Character Editor onto that fresh start. That is not what produced
`CANONICAL_ASHKARR_START_2026-09-12.rws`. Per `PLAYER_START_SITE_1.md`'s own "THE START
EXISTS" section: the owner **flew The Utinni gravship live, in person, from the colony
tile, in three hops (1596 → 9926 → 17007), landed at 17007 by hand**, and that flight's
end-state — whatever colony was aboard the ship at that moment — was saved and registered
as the canonical start. The ship being flown was crewed from a long-running vanilla
`Crashlanded` dev/test colony (the same one visible in the 2026-09-09 saves), not a colony
freshly generated from `Scenario_Utinni.xml`. The item file even says explicitly, dated the
same day as the flight, that **"the scenario's start pinned to the tile"** is a thing still
owed — this gap was already known, not a new regression.

So: the world/tile/gravship layer is correct (owner flew it there in person, tile 17007,
`wasSpawnedViaGravShipLanding=True`, world name Ash'karr — all independently confirmed
correct in the original filing). The scenario/founders/stock layer was simply never
produced — no save carrying it was ever created, let alone lost.

## Severity call

This is **not** "the canonical save is broken/corrupted" — nothing regressed and there is
nothing to restore. It is: **the six-founder, Jawa-stock, `Scenario_Utinni`-authored
campaign start that `SCENARIO_SPEC.md` describes as v1's shipped content has never existed
as a save file on this machine.** That is a real gap and, if anything, larger than "add
Sekki Vosh" — the whole founder cast, starting stock, and scenario identity for the shipped
save are outstanding, not just one founder. Recommend: keep open, `needs=owner` (whether to
redo the flight from a properly-started Utinni-scenario game, or hand-build the founders/
stock directly into the existing tile-17007 save via the Character Editor + savegame
editing, is a real fork the owner should pick, not one for FOUNDRY to guess at overnight).

## What remains genuinely uncertain

- Whether the population living in the save *right now* (today, 2026-09-19) still matches
  what the original filing measured on 2026-09-18/19 — not re-checked here, no reason to
  expect it changed materially, but not reverified either.
- Whether the owner considers the world/tile/landing half sufficient to ship on its own
  with the founders retrofitted in place (cheaper) versus wanting a true from-scenario
  restart (matches spec exactly, loses the tile-17007 flight's provenance and the
  already-authored world dressing done since).
- Exact count/identity of today's non-Jawa colonists was not re-derived here (trusted from
  the original filing per this task's instructions).

Left in `doing`. Original filing's title stands (it correctly names the mismatch even
though "corruption" was never the right frame); no rename performed since the underlying
description of what's wrong was already accurate.

## ruling — owner, 2026-09-20

Verbatim: **"Hand-edit the founders in"**.

Do **not** redo the flight from a fresh `Scenario_Utinni` start. The six founders,
their starting stock and the opening story are hand-edited into the existing
`CANONICAL_ASHKARR_START_2026-09-12.rws`; the world progress already in that save
is kept.

Consequence for the sibling items: the save must therefore be made loadable, so
`CANONICAL_SAVE_MODLIST_DIVERGENCE_1` and `CANONICAL_SAVE_CUT_RESIDUE_1` are live
work, not moot. A full residue scrub is no longer speculative.

## executed, 2026-09-20

Backed up twice before touching anything (`.bak-pre-sekki-stock-edit-20260920T141947Z`
before the pawn/stock work, `.bak-pre-scenario-text-edit-20260920T142811Z` before the
raw text edit) — both still on disk in `Saves/`, neither deleted.

Loaded the live save via `rimworld/load_game` with `ignoreModCompatibility` (still
needed — the 18-mod divergence is `CANONICAL_SAVE_MODLIST_DIVERGENCE_1`'s to fix, not
touched here). Confirmed via `rimworld/list_colonists` before touching anything: only
**5** living colonists exist on the map right now (Captain/Keeper/The Hands/
First-Hatched/Twice-Kin) — the "many additional randomly-named colonists
(Hernan/Ashly/Brandy...)" the original filing measured are NOT present as living
player-faction pawns today. Not chased further here (could be dead, could be a
different read of the raw save than a live colonist list gives) — but it means there
was no "purge the extras" decision to make: the roster right now is exactly the 5
founders plus the gap this item names.

**Scope decision, made explicitly rather than assumed:** the ruling says "hand-edit
the six founders... in", which is read here as ADDING the missing sixth, not
retroactively rewriting the other five's already-played traits/skills to match
`SCENARIO_SPEC.md` exactly (their current traits and backstories have visibly
drifted from spec already, e.g. Yeku's `adulthood` is `Torturer37`, nothing to do
with Star Wars). Touching five already-played pawns' established identities is a
bigger, more destructive, more judgment-laden move than "world progress is kept"
plainly authorizes. Flagging this reading rather than silently picking it — if the
owner wants the other five corrected to spec too, that is a fresh, explicit ask.

**Sekki Vosh — the sixth founder, built:**
- Spawned `RUT_Jawa_Colonist` in faction `player`, forced `xenotype=RSW_MandrakeJawa`
  (`jawa/spawn_pawn`) — matches the other five's kind/xenotype exactly
  (`jawa/pawn_get` cross-checked against Yeku).
- Identity: first `Sekki`, last `Vosh`, nick `The Long Pot` (`jawa/set_pawn_identity`).
- Backstory: childhood `SewerKid57`, adulthood `HouseServant63` — chosen because
  `HouseServant63` is one of the few Adulthood backstories whose `workDisables` is
  exactly `Intellectual` (per spec) and it nudges Cooking, matching his role; flavour
  text is generic and not Star Wars-themed, same as the other five's own backstories
  already are (not a regression from an established norm).
- Skills set exactly per spec: Cooking 7 (Major), Plants 5 (Minor), Construction 2,
  Social 2 (`jawa/set_pawn_skill`). Other skills left at their random rolled values,
  same convention as the other five.
- Traits: added `Gourmand` and `Neurotic` (degree 1, the plain "neurotic" label, not
  "very neurotic") on top of whatever the generator rolled (`Insomniac`, `Bisexual`,
  `Wimp`) — the other five founders also carry random extra traits beyond their
  named ones, so this is consistent, not a violation.
- Gear: `guy762_Robes_jawa` + `guy762_JawaHood` worn (same defNames the other five
  wear), `MeleeWeapon_Knife` equipped as primary. No gun, per spec.
- Ideo set to `the Ascendant Genome`, matching the rest of the colony.
- Age: spawned at 32; spec says 29 but `set_pawn_age` is forward-only and the
  backwards path skips every `BirthdayBiological` (a documented corruption risk) —
  left at 32 rather than risk that for a 3-year cosmetic difference.

**Starting stock topped up** (checked live counts first — Steel was already 444,
**above** the 300 target, left untouched; everything else read zero):
`ComponentIndustrial` 20, `MealSurvivalPack` 30 (3×10 stacks, vanilla stack cap),
`MedicineIndustrial` 15, `guy762_ionpistol` ×2, `guy762_ionrifle` ×1 — spawned loose
near the base rather than force-equipped onto the existing five colonists (same
scope reasoning as above: adding is authorized, rewriting established pawns is not).
`guy762_ionpistol`/`guy762_ionrifle` are from "Jawa Armoury Rebalance" (`guy762`), the
same weapon pack already carrying this campaign's other Jawa gear — picked for
thematic consistency since the spec names no exact defName for "ion sidearm"/"rifle".

**Pack animal and ikee:** spawned `AA_Eyeling` (the ikee) and `RSW_Dewback` (this
mod's own dewback, not the donor `Dewback`) into the player faction, bonded the
ikee to Yeku (`Thing_Human470530`) via `jawa/pawn_relations` `action=add
relation=Bond` — matches "bonded to Yeku" and the scenario def's own
`bondToRandomPlayerPawnChance` intent, made specific rather than random since we
know which founder the spec means.

**Opening story:** `Scenario_Utinni.xml`'s own `ScenPart_GameStartDialog` text is
correct but was only ever shown at a true game start, which never happened for this
save — replaying it is not possible. The closest achievable fix: the save's own
`<game><scenario><name>`/`<summary>` read `Crashlanded` / "Three crashlanded
survivors - the classic RimWorld experience." — corrected by a byte-exact binary
find-replace (⚠️ a first attempt via Python text-mode I/O silently collapsed every
CRLF to LF across the whole 17.5 MB file, a 500 KB size drop from touching two
short strings — caught by checking the size delta, reverted from the backup, redone
in binary mode; **any future raw edit to this save must open it `"rb"`/`"wb"`, never
text mode**) to `the opened hull` / "Wake the dead ship. Leave before the owners
arrive." — `Scenario_Utinni`'s own name/summary, verbatim.

**Verified, not assumed:** saved via `rimworld/save_game` with the exact existing
filename, then **reloaded the save fresh** (`rimworld/load_game`,
`ignoreModCompatibility` again) to prove the file round-trips — `list_colonists`
showed all 6 names (`Captain, First-Hatched, Keeper, The Hands, The Long Pot,
Twice-Kin`), every stock defName's count matched what was added, and the ikee/dewback
both resolved via `jawa/list_things` `includePawns=true`. The scenario text edit
survived the reload (parsed with `xml.etree.ElementTree` before and after).

**Not done, and why:** the 18-missing-mod divergence and its ~4,828 dead reference
lines (`CANONICAL_SAVE_MODLIST_DIVERGENCE_1` / `CANONICAL_SAVE_CUT_RESIDUE_1`) — a
separate, larger piece of surgery on the same file, sequenced next rather than
combined with this one so each is independently attributable if something goes
wrong.

## needs: game-up

Closing is reasonable once the sibling residue-scrub items are also resolved (they
touch the same file and a human review of the whole result together makes more
sense than three separate small looks) — left open rather than closed solo.
