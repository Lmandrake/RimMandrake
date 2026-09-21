# FOUNDERS_IMPORTER_OWED_1 — the round trip works, but only if you know four things nobody wrote down

## what this is

`FOUNDERS_EXPORT_TO_REPO_1` proved the round trip live on 2026-09-21: all 6 founders and
both named colony animals were spliced into a **foreign** save (different world, different
player faction, 69 colonists of its own) and arrived intact — **5 of 8 identical in every
field**, the other 3 differing only by `ageChronologicalYears +1` (different in-game date)
and one hediff the receiving game adds itself. The five-way relation clique and both animal
bonds resolved.

**So the fragments are sound and need no re-export.** What is missing is the **importer**.

## 🔴 why prose caveats are not enough — the failure that proves it

MEASURED 2026-09-21, attempt 1: **the `Wimp` trait was silently dropped from 5 of the 6
founders. Nothing in `Player.log`.**

`Wimp` is the only trait on these pawns carried with a non-null `<sourceGene>`, and gene
`loadID`s are **save-local indices, exactly like `Faction_21`**. The destination save had
already issued gene loadIDs 0–1633, so the fragments' `Gene_342/382/422/462/814` resolved
**successfully** — into the destination's *own, unrelated* genes.

🔑 **A loadID collision does not error. It resolves to the wrong object.** The one founder
who kept the trait was Sekki, whose `Gene_2009` sits above the destination's issued range —
6 of 6 agree, including that negative case.

⇒ A reader following the export README's prose would have hit this, seen a clean load, and
believed the backup was good.

## what the README did not say, and now does

- **`Ideo_20` is a save-local index too** and was absent from the README's remap list
  (corrected at `0a5cb3c1d`, along with its claim that no live re-import had been attempted).
- The working remap, from attempt 2: faction `21→17`, ideo `20→12`, positions,
  `nextThingID 22801→800000`, `nextGeneID`/`nextHediffID`/`nextJobID → 2,000,000`, and
  **every `<loadID>` offset by +1,000,000 with every `Gene_<n>` reference rewritten to match**.
  Map index unchanged.

## what is owed

A committed `import_founders.py` beside the fragments that performs **all four** remaps
against a named destination save, so the knowledge lives in code rather than in a caveat.

⚠️ **Do not re-export the fragments.** They are correct. Measured: 169 def-bearing
references across the 8 fragments (134 `<def>`) — **0 unresolved** against the live 618-mod
set, checked with a negative control. 62 `Thing_*` references — **0 dangling**, all inside
the 22 ids the fragments declare, so nothing else from the source save has to travel with
them.

## spec

1. `import_founders.py <destination.rws>`: splice the 8 fragments into the destination's
   `things`, applying the four remaps and bumping `uniqueIDsManager`.
2. It must **allocate** ids above the destination's issued ranges rather than using a fixed
   +1,000,000 offset — a hardcoded offset is the same class of bug as the collision it fixes.
3. ⛔ **Binary mode only** for any `.rws` write; a text-mode write converts LF→CRLF and
   silently corrupts the save. Check the size delta.
4. It must refuse to write to a keeper save by name (`CANONICAL_ASHKARR_START_*`,
   `ASHKARR_FALLLINE_*`).
5. A selftest that asserts the `Wimp`/`sourceGene` case specifically — that is the regression
   this item exists for.

## verify

Run the importer against a fresh copy of a foreign save, load it, and confirm via the bridge
that all 6 founders carry `Wimp` and their relation clique. The two evidence saves from the
2026-09-21 pass are the fixtures: `FOUNDER_ROUNDTRIP_V2_2026-09-21` (clean) and
`FOUNDER_ROUNDTRIP_2026-09-21` (loses the trait).

## criteria

Someone who has never read this item can restore the founders into a new world with one
command and lose nothing.

## built 2026-09-21

`design/Jawa/worldbuilding/founders/import_founders.py` — one command, all four
remaps, plus two the spec did not name (ability ids, and Thing ids when the
destination forces it). Guard: `src/RimMandrake/Utils/selftest_import_founders.py`,
28 cases. Repo runner 67/68 before (1 pre-existing failure,
`selftest_deployed_biome_refs.py`) → **68/69 after**, same one failure.

**Allocation is computed, per destination, per class:**
`base = max(destination counter, highest id the destination actually issued) + 1`,
both read by PARSING the destination. The counter alone is not enough — a counter
can sit behind an id already in the file — and the issued maximum alone is not
enough either, since the receiving game is about to hand out from the counter.
Against `XENOTYPE_SKIN_REVIEW_2026-09-20.rws` that yields gene base 1634 (its
`nextGeneID`; issued max 1633), hediff 527, job 4, ability 136. The selftest proves
it is not a constant by splicing into a destination whose genes run **past
1,000,000**, where the proving run's +1,000,000 would collide, and finding it clean.

**Tested against** a scratch copy of the same foreign save the 2026-09-21 run used:
8 of 8 pawns arrive, faction `Faction_17`, ideo `Ideo_12`, **0 gene loadIDs shared
with the destination's 1,633**, all 6 `Wimp` `sourceGene` refs resolving inside the
founders' own 240 genes, 0 lone LF in 11,003,021 bytes.

**The detector is calibrated on the evidence saves**, so it is known to see the real
defect and not merely to agree with itself: `FOUNDER_ROUNDTRIP_2026-09-21.rws`
(attempt 1) reports **200 colliding gene loadIDs and 5 of 6 colliding `Wimp`
sourceGenes** — exactly the five founders that lost the trait, Sekki the one
survivor; `FOUNDER_ROUNDTRIP_V2_2026-09-21.rws` reports 0. Neither fixture was
written to. ⚠️ A count assertion cannot catch this: the broken save still holds 6
`Wimp` elements. The selftest carries that as an explicit control case.

⚠️ **Two traps found while building it, both silent.** The fragments' provenance
comment contains the literal text `<li Class="Pawn">`, so `data.index(b"<li")` cuts
inside the comment; and `<loadID>` is not always an integer — verb loadIDs are
strings like `Thing_RSW_Dewback669123_0_Smash`. A blind text substitution of
`<loadID>N</loadID>` is wrong for a third reason too: gene and hediff ranges
overlap, so the same integer is two different ids and the class must come from the
element's path.

**Still owed:** a live load of an importer-produced save. The offline evidence is
strong (byte-identical detector agreement with the V2 save that WAS loaded live on
2026-09-21) but the importer's own output has not itself been through a game.
Keeper md5s re-verified unchanged: `CANONICAL_ASHKARR_START_2026-09-12.rws`
`75be9ecd4764a397e9802d997bb9e0b9`, `ASHKARR_FALLLINE_LABEL26_2026-09-21.rws`
`31c981515d9e90dcacdb1f2110068527`.

## live-test artifact is READY — one load closes this item

Produced 2026-09-21 by BENCH, offline, from the shipped importer:

```
python3 design/Jawa/worldbuilding/founders/import_founders.py \
  "<Saves>/XENOTYPE_SKIN_REVIEW_2026-09-20.rws" \
  --out "<Saves>/FOUNDER_IMPORTER_LIVETEST_2026-09-21.rws"
```

`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FOUNDER_IMPORTER_LIVETEST_2026-09-21.rws`
(11,003,021 bytes)

**VERIFIED OFFLINE by BENCH, against the produced file itself — not the importer's report:**

- Destination's issued gene max **1633**; the importer allocated base **1634** and moved
  every founder's genes above it (Nekko 329..368 → 1634..1673, … Sekki 1996..2035 →
  1834..1873).
- 🔴 **All 6 `Wimp` traits carry a `sourceGene` in 1647 / 1687 / 1727 / 1767 / 1807 /
  1847 — every one ≥ 1634.** The collision that silently lost this trait from 5 of 6
  founders is provably absent. That is the regression this item exists for.
- Line endings consistent: 336,865 CR and 336,865 LF, so no lone LF — the binary-mode
  requirement held and the file is not CRLF-corrupted.
- The destination `XENOTYPE_SKIN_REVIEW_2026-09-20.rws` is **untouched** (10,723,960 bytes,
  Sep 20 14:47) — `--out` was used.
- Keepers re-verified unchanged: `CANONICAL_ASHKARR_START_2026-09-12.rws` md5
  `75be9ecd4764a397e9802d997bb9e0b9`, `ASHKARR_FALLLINE_LABEL26_2026-09-21.rws` md5
  `31c981515d9e90dcacdb1f2110068527`.
- `selftest_import_founders.py` **28/28**, runner 67/68 → **68/69** (the one failure is the
  pre-existing, unrelated `selftest_deployed_biome_refs.py` timeout).

### the only thing left

⚠️ **The importer's own output has never been through a game.** Offline evidence is strong
but it is not a load.

⇒ Load `FOUNDER_IMPORTER_LIVETEST_2026-09-21` and confirm via the bridge that all 6
founders are present and **all 6 carry `Wimp`** (`jawa/pawn_traits`), plus their relation
clique. That is the whole remaining step.

🔴 It was NOT done in this sitting because the bridge was held by the other window for an
unrelated live-verify batch, and ⛔ taking it would have ended their session. The game was
already up on the full 618-mod list — so whoever gets the next bridge window should spend
it here first; the artifact is built and waiting.
