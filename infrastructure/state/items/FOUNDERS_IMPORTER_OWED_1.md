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
