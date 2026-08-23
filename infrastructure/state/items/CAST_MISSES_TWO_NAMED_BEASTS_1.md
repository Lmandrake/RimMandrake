## spec
Filed by BUILD from `CREATURE_NAMES_APPLY_1`, 2026-08-23: `creature_names_ashkarr.md` names 41
creatures but only 37 renames generate, because `gen_name_patch.py` maps a doc row to a
defName THROUGH `cast_assignment.csv`. DECIDE's call: do the misses belong in the cast, or
should the names doc say they were deliberately excluded?

⭐ **BUILD was right not to widen the generator.** Renaming past the cast would rename
creatures nobody decided to place.

## ✅ RULED 2026-08-23 — 2 dead, 2 reserve, cast NOT re-opened

**And BUILD's count was right where the doc was wrong.** The doc asserted *"All four exist in
the dump."* Measured against the live capture `2026-08-23T07-12-04Z` **and** the 2026-08-21
database, both empty:

| name | exists | ruling |
|---|---|---|
| `Protovermes` → ssik | 🔴 **NO** | ⛔ **DEAD** — its mod is not installed. Not a reserve; the name holds nothing and is free to re-use |
| `Compsognathus` → sskek | 🔴 **NO** | ⛔ **DEAD** |
| `Dinornis` → kessik | ✅ yes | ⏸️ **RESERVE — not cast** |
| `Sivatherium` → obbakar | ✅ yes | ⏸️ **RESERVE — not cast** |

🔑 **"Reserve" and "dead" are different states and the doc had merged them.**

### Why neither live one enters the cast

| | `Dinornis` | `Sivatherium` |
|---|---|---|
| bodySize | 5 | **8** — SUPER-class (24 cast SUPERs median 8.2) |
| sprite | 2,851 px | 2,526 px |
| its band's weak line | 2,884 (huge) | 3,311 (SUPER) |
| comfy temperature | −30 … **40** | −20 … **40** |
| Ash'karr biomes at commonality > 0 | 4, all **0.004 – 0.01** | 🔴 **none** |

- **`Sivatherium` fails on all three counts** — no native reach here, `ComfyTemperatureMax 40`
  excludes the hot desert that is 35% of the ground, and at bodySize 8 with a 2,526 px sprite
  it would enter as an immediate shrink candidate under `CREATURE_RESIZE_PATCH_1`.
- **`Dinornis` is closer and still short** — native reach that rounds to never, and a sprite
  below its own band's weak line.
- 🔑 **The cast is settled.** The owner approved creature sizes against it the same day;
  re-opening it for two marginal animals would invalidate a decision hours old for nothing the
  world can see.

✅ Both names stay reserve, in-clade and ready. `obbakar` is the bestiary's elder-form of
`obbak`, and **`Diprotodon`, which carries `obbak`, IS cast** — the pairing is waiting.

## two traps recorded while measuring

- ⚠️ **TWO defs are called sivatherium**: `Sivatherium` (Megafauna, bodySize 8) and
  `MA_Sivatherium` (Mythic Ages, bodySize 3.3). The doc row means the Megafauna one. A
  generator matching on label would pick either.
- ⚠️ **`Sivatherium`'s label carries a trailing space** in the dump — `'sivatherium '`.

## verify
    python3 design/Jawa/fauna/gen_name_patch.py

**PASS = 37 renames and a warning naming the four**, unchanged. ⛔ 41 would mean someone
widened the generator past the cast, which is what this ruling refuses.

## criteria
- [x] Each of the four resolved: 2 dead, 2 reserve, with the measurement behind each.
- [x] The doc's "all four exist" corrected in place, in the doc.
- [x] Cast left alone; no re-run.
