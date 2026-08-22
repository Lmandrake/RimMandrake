## spec
🔴 **`src/RimMandrake/Utils/jawavoice/genideo.py` will silently revert 94 gate strings to a
pawnkind that no longer exists, and its success line will look normal.**

Found 2026-08-21 by a sweep for the failure that
`gen_pawnkind_roster.py` had (`BUILDABLE.md` 11), and it is the same class caught a
different way — **the count matches and the content does not.**

| | |
|---|---|
| generator's `CONDS` | `INITIATOR_kind==OuterRim_Jawa` / `OuterRim_JawaTribal` |
| committed `src/Jawa/JawaVoice/Patches/JawaVoice_Ideology.xml` | 47 + 47 occurrences of **`RimMandrake_Jawa`** / **`RimMandrake_JawaTribal`** |

The output was updated to the `RimMandrake_` names; the generator was not. Its sibling
`genxml.py` **was** updated, which is the tell — this is a half-finished rename, not a
deliberate divergence.

⚠️ **A count check would not have caught it.** 14 Operations and 188 `<li>` before and
after, and the success line reads `14 defs, 47 lines -> 188 rules` either way.

**Do one of:**
- update `CONDS` to the `RimMandrake_` names, re-run, and confirm the diff is empty; or
- if the generator is dead, say so at the top of the file and stop it running.

⛔ **Do not re-run it as it stands.** Verify which pawnkind names are live first — the
`OuterRim_Jawa` kinds may or may not still exist, and a gate naming a dead kind never
fires and logs nothing.

## verify
`grep -c RimMandrake_Jawa` on the committed XML is unchanged after a re-run, or the
generator refuses to run at all. `git diff` on `JawaVoice_Ideology.xml` after the re-run
is empty.

## criteria
Re-running every generator under `src/RimMandrake/Utils/` leaves the working tree clean.
