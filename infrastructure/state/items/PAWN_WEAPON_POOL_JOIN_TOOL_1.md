# PAWN_WEAPON_POOL_JOIN_TOOL_1 — attributing which of the 23 bare-producing kinds fails which way

Filed 2026-08-29T01:13:03Z, `caused_by: PAWN_WEAPON_GEN_TAG_POOL_READ_1`. Full spec was already
attached (not a thin item) — see the ledger `file` event for the verbatim ask.

## What was built

`src/RimMandrake/Utils/weapon_pool_join.py` — joins each of the 23 bare-producing kinds'
`weaponTags` (read off the emitted roster XML, same source `weapon_affordability.py` uses and
for the same reason: the generator's dead `R` shadow table drifted before) against the full
weapon roster's `IsRangedWeapon` (derived from `verbs[].verbClass`, since melee weapons here
carry no `verbs` entry at all) and `generateAllowChance` (read from `defs.sqlite` directly, by
name, only for weapons that actually appear in one of the 23 pools).

**Reused, not reinvented:** pricing (`base_market_value`, `load_roster`) is imported straight
from `weapon_affordability.py` — that file already solved and calibrated the hard part
(recipe-recursive `costList` pricing, UNMEASURED-not-zero on a missing `MarketValue`). This
script only adds the two fields that file never needed.

🔴 **First run was wrong and caught itself**: `game_paths.DEF_DUMP` resolves to the newest
`captures/<id>/` subfolder, not the flat root where `defs.sqlite` actually lives
(`DUMP_ROOT/defs.sqlite`) — the general form of `FLAT_MANIFEST_READER_SWEEP_1`. Every kind
read `ranged 0` including `Jawa_Empire_Grunt` (a stormtrooper who obviously carries a blaster),
which is what flagged it. Fixed to `DUMP_ROOT`; re-ran and got sane per-kind numbers.

## Result — `infrastructure/state/facts/weapon_pool_join_2026-08-29.json`, full per-kind detail

**18 of 23 kinds are RANGED-ONLY within budget** — their entire within-budget, tag-matching
pool is ranged weapons, zero melee. For these, `WorkTagIsDisabled(WorkTags.Shooting)` (any
trait/backstory that disables Shooting, independent of the `Violent` check already ruled out)
is sufficient by itself to explain a bare pawn — no `generateAllowChance` roll needed:

```
Jawa_Hutt_Heavy · Jawa_Hutt_Grunt · Jawa_Hutt_Specialist · Jawa_Helix_Leader ·
Jawa_Wildsteam_Leader · Jawa_Empire_Leader · Jawa_Geonosian_Grunt · Jawa_Homestead_Leader ·
Jawa_Empire_Specialist · Jawa_DeepDesert_Specialist · Jawa_Helix_Heavy · Jawa_TradeMoot_Heavy ·
Jawa_Homestead_DesertRanger · Jawa_Empire_Heavy · Jawa_Geonosian_Specialist ·
Jawa_Geonosian_Heavy · Jawa_Empire_Grunt · Jawa_Homestead_Specialist
```

**0 of 23 have a within-budget pool of ≤2 with a `generateAllowChance<1` entry** — the
guaranteed-near-empty shape named in the parent item does not occur among these 23 as scoped.

**5 kinds match NEITHER named mechanism** — their within-budget pool has real melee weapons
(OuterRim Vibro-series, mostly), so ranged-only does not explain them, and no low-chance entry
sits in a pool small enough to matter structurally:

```
Jawa_Deepwater_Leader · Jawa_Junkers_Grunt · Jawa_Deepwater_Specialist ·
Jawa_DeepDesert_Heavy · Jawa_Wildsteam_Specialist
```

⭐ **One of the 5 has a real lead anyway, outside the ≤2 scope:** `Jawa_Junkers_Grunt`'s
"cheapest eligible" weapon named in this item's own parent facts doc — `BMT_ResourceBlueCrystal
@1` — carries `generateAllowChance: 0.0`. It can **never** actually generate; the facts doc's
"floor − cheapest = +59" headroom claim rests on a weapon that is permanently excluded by the
stochastic gate, so the REAL cheapest reachable price for this kind is unmeasured-from-this-join
and likely much closer to its floor than reported. Worth a follow-up read of what the next
cheapest ACTUALLY-reachable weapon is, but that is a new, narrower question, not this item's.

## Watch out
⚠️ **"within budget" here is `price <= weaponMoney.max`** — the pool reachable on the most
generous roll, not the exact per-pawn roll. Correct for "is this kind EVER only-ranged", which
is what the criteria asks; not a per-pawn probability.
⚠️ **Mod drift**: the dump captured 582 mods; the live list (checked via `refresh.py`, same
session) has grown to 584 (`+meathax.showmeyourtools`, `+mlie.showmeyourhands`) — neither is a
weapon-adding mod by name, low risk, not re-verified against a fresh dump.

## criteria
- [x] Offline script built, joining weaponTags against roster IsRangedWeapon/generateAllowChance
      for the 23 kinds, reusing `weapon_affordability.py`'s pricing rather than re-deriving it.
- [x] Per-kind attribution: 18/23 ranged-only (Shooting-incapability sufficient), 0/23 hit the
      named ≤2-pool-with-low-chance shape, 5/23 explained by neither (one of those five has an
      unrelated generateAllowChance:0 lead worth a narrower follow-up).
- [ ] Not this item's scope, named for whoever picks up the mitigation
      (`PAWN_WEAPON_GEN_TAG_POOL_READ_1`'s own note: "which tags to add is a canon/faction-
      identity call, not mine to make for 23 kinds unilaterally; needs: owner"): giving the
      18 ranged-only kinds a melee fallback tag.
