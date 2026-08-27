# DUMP_DERIVED_SHEETS_SHOW_CUT_1 Every dump-derived sheet and census silently includes cut content

## spec

🔴 **The def dump is captured BEFORE Cherry Picker removes anything.** A cut that WORKED is
**present** in the dump, so the dump cannot answer *"is this cut"* in either direction. The
evidence, all three readings, is `infrastructure/state/facts/dump-is-pre-cherrypicker.md`.

**Filed by the OWNER, 2026-08-23, reviewing the creature art sheet:** *"I had really thought I
had already removed all of these terrestrial animals somewhere already."* ⭐ **He had. The sheet
was wrong, not his memory** — he spent a review pass judging animals the game no longer has, and
asked a question that read as a memory failure and was an instrument failure.

⚠️ **The headline number is stale and the direction matters.** Filed at **1,162** ThingDef cuts
still visible; re-measured 2026-08-27 the kill list is **1,342 defs** — 1,292 `ThingDef`, 26
`BiomeDef`, 8 `IncidentDef`, 7 `PawnKindDef`, 5 `HediffDef`, 2 `RecipeDef`, 2 `GeneDef`. It grows
every time he reviews a category, so **no artifact may hard-code a count**; read the list.

## What landed, 2026-08-27

**`src/RimMandrake/Utils/cherrypicker.py`** — one reader, because eight scripts had each grown
their own regex over the settings file and that is the drift machine `CLAUDE.md` names. It
exposes `load()` / `from_log()` → a `Cuts` object with `.cut(type, name)`, `.filter(rows, key)`
and **`.provenance(suppressed)`**, the line an artifact must carry.

- 🔑 **It distinguishes INTENT from RUNTIME TRUTH and says which it used.** The settings file is
  what the next load *will* remove — and three of Cherry Picker's four failure modes are silent,
  so a key there can resolve to nothing and never say so. `from_log()` reads the removal block
  out of `Player.log`, which is the only source that proves a key resolved. ⚠️ That log is
  destroyed at the next launch.
- ⛔ **It never returns an empty set when it could not look.** With neither file readable it
  raises, because *"nothing is cut"* and *"I could not look"* reading alike is the same class of
  bug this item exists to kill.

**Both contact sheets filter, and both say so.** `thing_contact_sheet.py` (weapons · apparel ·
items · buildings · plants) and `animal_contact_sheet.py` drop cut rows by default, print the
provenance line, and carry a `cut` column in the summary. `--include-cut` opts out and labels the
sheet as showing defs the running game does not have.

⭐ **Stating the number is half the fix, not a courtesy.** A sheet that silently shows fewer
things is the same instrument failure wearing the other hat — he cannot tell *"this mod ships
nothing"* from *"I cut it all"*.

## verify

The fact file names the pair, and **it is the pair that IS the bug — both must hold at once:**
a def the log removed must be **absent** from any sheet shown to a human and **present** in the
dump. Measured 2026-08-27 against `observed/inventory/animals.csv`:

```
cut list: 1342 defs, live settings, 2026-08-23 11:33   |  341 rows suppressed as cut
animals.csv rows 1239 -> 898 shown, 341 suppressed
  Cat              in animals.csv=True   shown=False
  YorkshireTerrier in animals.csv=True   shown=False
  Alphabeaver      in animals.csv=True   shown=False
  BlackBear        in animals.csv=True   shown=False
  Muffalo          in animals.csv=True   shown=True     <- the control
```

## criteria

- [x] Dump-derived rosters filter against the kill list — the two contact sheets do.
- [x] Each such artifact states how many rows it suppressed (`Cuts.provenance`).
- [x] One reader, not a ninth parser.
- [ ] The other six readers move onto `cherrypicker.py` and delete their own regex.
- [ ] **`measure` / `defs.sqlite` still say nothing about which question they answer.** A
  `measure count ThingDef` counts what the DUMP holds, not what the game runs. That is not
  wrong — it is a different question — but nothing currently labels it, and the instrument
  lives outside this repo (`D:\Luke\dev\measuring-large-artifacts`).

## Watch out

⛔ **Do not "fix" this by re-capturing the dump later in load.** The dump's job is the authored
def set; the kill list's job is what survives. Two questions, two instruments — joining them is
the fix, collapsing them is a new bug.
