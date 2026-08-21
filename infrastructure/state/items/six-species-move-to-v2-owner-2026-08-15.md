## spec
🔴 **OWNER RULING 2026-08-15. Six species left v1 for v2 — then FIVE, not six.**
⭐ **SUPERSEDED IN PART, same day: the ORTOLAN CAME BACK INTO v1.** Owner,
verbatim: *"We have a working Ortolan! Make that as done for now and confirmed,
not v2 after all."* It spawned in the 70/70 grid and he examined it on screen.
`RimMandrakeOrtolan` is **v1, DONE and CONFIRMED** — nothing to restore, nothing
to schedule. Herglic, Anzati, Muun, SithZ and Togorian are unaffected.
*"Herglic is now v2. So are Anzati, Muun, Sithz, Togorian. The Ortolan we
sorely want them, but for now they are also in v2. Mark the Ortolan as a
high priority for v2."*

**EXACT defNames, verified against the shipped XML — do not retype them:**

| species | xenotype | pawn kind |
|---|---|---|
| Herglic | `RimMandrakeHerglic` | `RimMandrakeHerglic_Kind` |
| Anzati | `RimMandrakeAnzati` | `RimMandrakeAnzati_Kind` |
| Muun | `RimMandrakeMuun` | `RimMandrakeMuun_Kind` |
| **Sithz** | `RimMandrakeSithZ` | `RimMandrakeSithZ_Kind` |
| Togorian | `RimMandrakeTogorian` | `RimMandrakeTogorian_Kind` |
| ~~Ortolan~~ ✅ **v1** | `RimMandrakeOrtolan` | `RimMandrakeOrtolan_Kind` |

⚠️ **`Sithz` is spelled `SithZ` in the def — capital Z.** It is the one name
here that does not match the owner's spelling, and a lowercase `z` silently
matches nothing. ⚠️ Do not confuse it with `RimMandrakeSithMassassi` or
`RimMandrakeSithKissaiPureblood`, which are DIFFERENT species and **stay in v1**.

~~⭐ **ORTOLAN IS HIGH PRIORITY FOR v2**~~ — ⛔ **STRUCK 2026-08-15. WRONG, and a
reader acting on it would defer a species that is already finished and in v1.**
Superseded by the ruling at the head of this item. Closes both
`ortolan-is-v1-again-supersedes-the-v2-deferral-1a7f30` and `D-RACE`'s
cross-reference — the correction is made ONCE, here.

🔑 **MEASURED, and it changes what BUILD has to do:** only **Herglic** is in the
generator's 65-species roster. The other five are **NOT** — they ship from some
other write path. So `DROP_SPECIES` (which keys on the roster name) reaches
Herglic and **cannot reach the other five**. Find the path that writes them
before assuming one mechanism covers all six.
🔴 **THIS IS A SANCTIONED SHRINK AND IT COLLIDES WITH THE GUARD.**
`_guard_species_regression` refuses to write a smaller catalogue — correctly,
it caught a real defect this morning. This ruling makes the catalogue smaller
**on purpose**. ⛔ **DO NOT WEAKEN OR DISABLE THE GUARD.** Lower its BASELINE by
exactly these six, deliberately and in the same commit, so it still refuses
every shrink nobody authorised.

## verify
none of the six defNames appears in the deployed mod; `_guard_species_regression`
is still present and still refuses an unlisted shrink; the shipped xenotype count
drops by exactly 6.

## criteria
the six do not generate, and no `Could not resolve cross-reference` names them.

## notes
**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

✅ CLOSED — owner ruling, filed.
