🔴 **STRUCK AS DISPROVEN — OWNER, 2026-08-26.** Verbatim: *"we have disproven this item
multiple times. Strike immediately as disproven. NO REGRET. Simply destroy it."*

⇒ **Painting under a live colony destroys THAT COLONY and nothing else.** Make a new one and
the game continues. The 2026-08-21 session — "could not make a new colony", "UI buttons lost
icons" — is struck: one unreproduced observation, contradicted repeatedly since.

⛔ **Nothing may cite this item as evidence for anything.** The item is dropped in the ledger.
✅ **The `--despite-map` guard and `w9_run.py`'s `mapCount > 0` refusal STAY** — the colony loss is
real and a guard that costs a colony is cheap. Their message is about the COLONY, not the game.

---

## spec

🔴 **OWNER'S CORRECTION, 2026-08-23, and it demotes this item's headline — verbatim:**
*"I think painting under a player colony is actually fine to do... it just destroys the
player colony. So you must create a new one in order to continue in the game... I did
this recently and it worked fine. So let's please not record that we cannot paint into
an existing game... that must still be verified true if we are to believe it, and I
think it may in fact be false. I am happy to do this test with you when you are ready."*

⇒ **The title of this item is now a HYPOTHESIS, not a measurement.** Split what was
recorded on 2026-08-21 into the part he agrees with and the part he disputes:

| observed 2026-08-21 | status after his correction |
|---|---|
| the colony/map was destroyed | ✅ **AGREED, and it is EXPECTED, not damage.** Paint moves the ground out from under a generated map; that map cannot survive it. Make a new colony and carry on |
| the game could no longer create a new colony | ❓ **DISPUTED.** He has since painted under a colony and made a new one without trouble |
| UI buttons lost icons and names | ❓ **UNVERIFIED.** One observation, one session, never reproduced |
| the preset lost `myLittlePlanetSubcount 7` / `planetCoverage 1` | ❓ **SEPARATE ITEM** — `PRESET_ONSCREEN_CHECK_UNVERIFIED_1`. May have its own cause and must not be used as evidence for this one |

⛔ **Do not write, cite or act on "we cannot paint into an existing game."** That
sentence is not established, the owner believes it is false, and this item is where the
claim came from. Anything downstream that leans on it is leaning on one unreproduced
session.

⚠️ **The `--despite-map` guard and `w9_run.py`'s `mapCount > 0` refusal stay for now** —
a guard that costs a colony is cheap and the colony loss IS real. But its message must
say *"this will destroy the current colony; make a new one"*, **not** *"this destroys
the game"*.

🔑 **THE TEST IS OFFERED AND UNBLOCKED.** He said he is happy to run it together. It is
cheap on a scratch quicktest: paint under a live map, then try to make a new colony and
drive the UI. Until that runs, everything below is a single observation.

---

### The 2026-08-21 observation, kept verbatim as the thing to be re-tested

🔴 **MEASURED 2026-08-21, on the owner's own screen. This is no longer a warning inherited
from 2026-08-18 — it happened again, and it was watched happening.**

The world paint was run with `--despite-map` against a game holding one live colony map.
Every stage reported success and the planet painted correctly. Then:

- the **colony was destroyed** and the game could no longer create a new one
- the game state became **unstable** — "I could no longer make a new colony"
- **UI buttons lost their icons and their names**, which is the render/atlas layer failing,
  not a gameplay bug
- remaking the world from inside that broken session produced a planet that had **lost
  `myLittlePlanetSubcount 7` and `planetCoverage 1`** — see `PRESET_ONSCREEN_CHECK_UNVERIFIED_1`
- the owner took the game DOWN

⚠️ **The paint itself was faithful.** Seven tiles read back from the engine matched the CSV
to the digit, lint fell 3,529 → 86, and the picture was right. The damage is not that the
paint was wrong. **The damage is that the paint moved the ground out from under a map that
had already been generated from it**, and RimWorld has no mechanism to reconcile the two.

🔑 **The cost is not just the map.** Everything measured after the paint in that session is
now suspect, because a half-broken game answers the bridge normally — that is the zombie
state `RT_PROBE_LOAD_ABORTS_ON_578_1` documents. The findings recorded before the paint
(the log harvest, the def dump) stand; the ones after it want re-proving on a clean load.

## verify
`w9_run.py` refuses on `mapCount > 0` — that guard was added on 2026-08-21 and is what
should have stopped this. `--despite-map` must survive as an escape hatch, but its help
text and the run sheet must both carry the measured outcome rather than a caution.

The next paint runs against a world generated fresh with **no map ever instantiated**, and
`mapCount` is read and recorded as 0 before stage 1.

## criteria
- `w9_run.py --despite-map` prints the measured consequence, not a general warning
- `WORLDPAINT_REHEARSAL.md` §7 names this run as the evidence
- the next paint records `maps 0` in its report before stage 1, and the owner reaches a
  colony afterwards without the game misbehaving

## notes
Filed by CHECK, 2026-08-21. The owner authorised `--despite-map` explicitly and I ran it;
the guard existed and was overridden knowingly. What was NOT known, and is now, is that the
failure is not confined to the map — it takes the session's UI and its ability to start a
new colony with it. That is worth more than the map was.
