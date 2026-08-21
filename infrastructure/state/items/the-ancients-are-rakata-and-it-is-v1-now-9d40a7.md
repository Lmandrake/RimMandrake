## spec
📄 **The whole build is already written: `design/Jawa/worldbuilding/ANCIENTS_AS_RAKATA_SPEC.md`,
528 lines. Follow it — do not re-derive any of it.** Read the new ruling block at
the head first, then R-A2 through R-A10.
🔑 **IT IS NOT A FACTION CHANGE (R-A7).** The `Ancients` FactionDef is not touched
at all — vanilla `Ancients` cannot host a faction, which is why the Ascendant Helix
was authored fresh. Ancient sleepers are cryptosleep caskets, not a faction you
meet, so **the six pawn kinds' xenotype is the entire surface.**
⛔ Do NOT touch `hidden`, `settlementGenerationWeight` or `canMakeRandomly`.
**(a)** Force `RimMandrakeRakata` at 100% on the six ancient pawn kinds — R-A2
(scope, two tiers) and R-A3 (mechanism).
🪤 **R-A4 names two XML traps that have ALREADY shipped broken in this repo:**
`xenotypeChances` is **dictionary-keyed** and an `<li>` there discards the whole
def silently (B56's bug); and a child's list is **appended** to its parent's, not
substituted, so `Inherit="False"` is load-bearing. Use the Remove-then-Add
operation in R-A4, not a bare Add.
**(b)** ⭐ **LABELS ARE NOW IN SCOPE.** R-A9 held them back as the owner's separate
call and he has made it. The sleepers read as Rakatan precursors, not "ancients".
**(c)** R-A8 still stands: **appearance only, the encounter must play exactly as
before.** Do not alter the six kinds' combat behaviour, gear or difficulty.
⚠️ **`RimMandrakeRakata` is one of the six species that exist NOWHERE but in our own
output** (`queue/DECIDE.md` `...4f81c9`). **A generator run that drops it by name
kills this feature.** The guard must refuse it by name, not merely refuse a shrink.
⚠️ R-A1's historical table is struck and corrected — the def **exists** and is
deployed. The `FACTION_SPEC.md` R27 broken-reference finding at the end of that
table is real and still owed.

## verify
`validate_patch.py --defs` clean; the six kinds resolve `RimMandrakeRakata` at
100%; `xenotypeChances` is dictionary-keyed with no `<li>`; the ancient encounter
spawns the same count and gear as before.

## criteria
a cracked casket produces a Rakatan, the encounter plays identically, and no
`Could not resolve cross-reference` names the xenotype.

## notes
**from:** DECIDE, 2026-08-20, on the owner's ruling *"let's go all out for v1 here.
'Ancients' is so boring! Let's get us some precursor Rakata in cold storage."*
⚠️ **LORE CORRECTION, same day — read it before writing any label text.** DECIDE
first recorded the Rakata as the AUTHOR of the ancient bioweapon. **That is wrong.**
Owner: *"The Rakata were nearly wiped out by their bioweapon-wielding ASSAILANT,
they didn't release the bioweapons themselves. **They were terraformers and mega
builders.**"* ⇒ they are the **victims and the makers** — the people who terraformed
this world, brought the metal down from the asteroids and built the *Utinni*. The
bioweapon's author remains UNNAMED. ⛔ No label or description may imply otherwise.
⭐ **This REVERSES the v2 deferral in `D30 (5)`.** B61 has been struck in
`design/V2_DREAMS.md` and returned to v1; do not action it from that row.

**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

done 2026-08-20 (offline half). One new file,
`src/Jawa/Jawa_Patches/Patches/AncientsAreRakata.xml`, deployed and in sync.
verify output: `validate_patch.py --defs` against the 578-mod load set —
  `OK - 0 errors, 18 warning(s)`
⚠️ **All 18 warnings are the same benign class** and the spec predicted them:
*"0 nodes in the on-disk Defs, but this node appears in a PatchOperation in
<16 other mods> — probably CREATED at runtime, make sure your mod loads AFTER
it."* `mandrake.jawa.patches` sits near the end of `ModsConfig.xml`, so it does.
🔴 **ONE MEASUREMENT IN THE SPEC NEEDED CORRECTING, and it caused 6 hard errors
on the first attempt.** R-A4 says to Remove-then-Add `useFactionXenotypes`
"if a node for it already exists — check each of the six rather than assuming".
Checked: **the def dump reports `useFactionXenotypes: True` on all six, and that
is the FIELD DEFAULT, not a written node.** Parsing the raw source shows no
`<useFactionXenotypes>` element on any of them, and no mod patches one in. So it
is an **Add only**; a Remove there matches nothing and the validator correctly
calls it an operation that would silently do nothing.
⇒ The op shape now differs per node, and the file says why in a table:
  `xenotypeSet` Remove+Add (16 mods patch it at runtime) ·
  `useFactionXenotypes` Add only · `label` Replace on the two Core/Odyssey kinds
  (verified present in raw source) · Remove+Add on the urban-ruins kinds, whose
  defs the validator cannot see at all.
⭐ **LABELS: shipped as "Forsaken", NOT "Rakatan".** The item put labels in scope;
the owner's naming ruling the same day decides the string — `Rakata` is the
ENDONYM, *"modern people on this planet just call them the Forgotten or the
Forsaken"*, and *"the word Rakata in a modern mouth is a scholar's word"*. A pawn
label is read by a player who is playing a Jawa. ⭐ **It also preserves the
discovery, which was R-A9's strongest argument against renaming at all** — the
xenotype label still reads "Rakata" in the bio and gene tab.
  `ancient soldier` → **Forsaken soldier** · `ancient captain` → **Forsaken
  captain** · `ancient special unit` ×2 → **Forsaken special unit**
⛔ `AncientMallGuards` ("Fashion guy") and `AncientSlaughter` ("slaughter") keep
their labels — renaming a joke label is authoring and DECIDE's register call.
Their xenotype is patched exactly like the other four. Filed to DECIDE.
R-A9 has been superseded in place, in its own file.
⏳ **The live half is owed and is CHECK's**: the def dump must read the xenotype
set back, and a cracked casket must produce a Rakatan with the encounter playing
identically. Filed as `RAKATA_SLEEPERS_LOOK_RIGHT_1` in `queue/CHECK.md`.
