## spec
✅ **OWNER'S RULING, 2026-08-22 11:00: all nine remaining NPC faiths get a full
`ideoDescription`.** He chose it over "only the factions the player meets" and over "let the
engine roll them", knowing the cost: *"it's the only authored prose that reaches a player
about these factions, and it cannot be added after the freeze."*

🔴 **This is STEP 3 of his four-step sequence and it bakes at game initiation.** An Ideo is
generated once at world creation and cannot be retrofitted. It does **not** wait for the map
(steps 1–2); it runs in parallel.

## what is owed
`design/Jawa/worldbuilding/faction_religions_spec.md` — **9 of 11 entries have no
`ideoDescription`.** Two are written (the Empire's *the Rising Order*, the Hutts' *the
Reckoning of Debts*) and are the pattern to follow.

**Per entry:**
1. `ideoDescription` — **one paragraph, 250–500 characters.** Calibrated against shipped
   examples: vanilla `HoraxCult` is 287, `DV_PirateKeshig` is 472. Longer is not richer; it
   is a scroll bar.
2. `deityPresets` — **name/type pairs, but ONLY where the structure meme's `deityCount`
   forces them.** `Structure_TheistEmbodied` is `IntRange(2,4)`, so the minimum is **two**,
   not one. `AM_Structure_Scavenger` is `deityCount 0` and must get none.
3. `ideoName` — already set on all eleven; do not churn them.

## 🔑 the constraint that decides the writing
**The engine renders exactly three things:** `ideoName`, `ideoDescription`, and the deity
name/type pairs. Precept labels, meme labels, ritual text, the "three doctrines" and the
taboo are **design register only — nobody ever reads them.**

⇒ **The paragraph IS the deliverable.** Everything else in an entry is briefing material for
us and reaches a player only through those three fields or not at all.

⛔ **`hiddenIdeo: true` deletes the entire budget** — the vanilla Horax cult sets it, which
is why its excellent 287-character description is read by nobody. **Leave `hiddenIdeo` unset
on all eleven.**

## register
Write from **inside** the faith, not about it — the Empire entry is written from inside a
stormtrooper's helmet by someone who will never see the god-king, and that is why it works.
A description that reads as an encyclopedia entry has wasted the only paragraph available.

## verify
`validate_ideoligion.py` passes on all eleven (pass `--mods-config` if a minimal mod list is
live, or every modded meme reads INVALID), and each `ideoDescription` measures 250–500
characters.

## criteria
Eleven of eleven authored faiths carry an `ideoDescription` in band, with `deityPresets`
present wherever the structure meme's `deityCount` minimum is above zero.

## watch out
⚠️ The spec cut rituals, deities and precept counts across all eleven on an **admittedly
unmeasured** assumption — *"NPC religion rarely surfaces in play."* The owner's answer here
does not ratify that assumption; it only settles the prose. If `jawa/ideo_of` is ever run,
the number that tests it is **`otherOnMap`**, not a total that our own colony inflates.
⚠️ Nine entries have never been audited against the `defaultSelectionWeight` rule and should
be assumed optimistic about which precepts actually exist.
