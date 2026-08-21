## spec

**One sentence from you closes this. Nothing is blocked on anything else.**

Two of your own rulings, 92 minutes apart, point opposite ways about `refmatch.py`
— the tool that would measure the painted planet against the reference photographs
and report five defect numbers.

| when | what you said | what it was read as |
|---|---|---|
| 2026-08-20, `canon.yml > ORTHO_GLOBE_MAP_ACCEPTED_1`, commit `977aa75` | *"Let's go with the globe map you made for v1. **Map accepted.**"* | ⛔ `refmatch.py` is **MOOT for v1 — do not build it for v1.** The remaining work is populating the map, not re-judging its shape. |
| 2026-08-21, `REFMATCH_THRESHOLDS_CALIBRATE_1` and `queue/HUMAN.md:825` | *"Yes, I like your new globes. Well done."* | ✅ the gate on `refmatch.py` has lifted — **build it.** |

🔑 **BUILD did not guess, and did not build it.** The later quote is the weaker of the
two, and `REFMATCH_THRESHOLDS_CALIBRATE_1`'s own spec says so — *"approval of the
RENDERING … not a ruling that the world has zero defects."* Liking a rendering is not a
reversal of *do not build it*. That item never cites the ruling at all, which is the
shape of a doc that was answered by a better one and never told rather than of a
deliberate reversal. It is now **blocked on you**, with the full evidence at
`infrastructure/state/observed/build/REFMATCH_THRESHOLDS_CALIBRATE_1_offline.txt`.

⚠️ **The stale plan that produced the confusion has been corrected** —
`TRANSIENT_upgrade_plan.md` said W7 *"does not start until the owner has looked"*, which
reads as a gate anyone can decide has lifted. It now says W7 is **cancelled for v1**.

⛔ **One file could not be corrected and is why this item exists.**
`infrastructure/state/items/CANON_RULINGS_OWED_OWNER_1.md` is yours, and it still carries
the dead gate: *"`refmatch.py` cannot be built until you have looked, because its five
defect thresholds are calibrated against those photographs, not chosen."* BUILD is
refused from editing an OWNER item, correctly. **That sentence is the trap** — the next
seat to read it will conclude the same thing this one did.

## verify

You say one of these, and it is done:

- **"Keep the ruling"** ⇒ `rimflow drop REFMATCH_THRESHOLDS_CALIBRATE_1`, and the dead
  gate line in `CANON_RULINGS_OWED_OWNER_1.md` gets struck.
- **"Build it"** ⇒ `rimflow unblock REFMATCH_THRESHOLDS_CALIBRATE_1`, `canon.yml >
  ORTHO_GLOBE_MAP_ACCEPTED_1` gets a superseding line, and BUILD writes
  `src/RimMandrake/Utils/refmatch.py`: five defect classes measured against the reference
  images in `D:\Luke\dev\Rimworld\research\Jawa\` — circular seas, comb rivers,
  rectangular roads, concentric biome rings, inherited names — **numbers, not a verdict**,
  and no code path that could emit an alternative planet. About one session; no game
  needed.

## criteria

`REFMATCH_THRESHOLDS_CALIBRATE_1` is either dropped or unblocked, and no file still
carries a gate that a later reader can decide has lifted.
