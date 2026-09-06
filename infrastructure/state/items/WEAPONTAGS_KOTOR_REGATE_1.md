# WEAPONTAGS_KOTOR_REGATE_1 — 67 stale-donor retag gates + 135 stale-donor absorption gates, all removed

Two sub-bugs, same root cause, both confirmed by reading the mechanism before
touching anything — never guessed.

## Ground truth checked first

**`guy762.KotORWeapons` (the KotOR Weapons and Armor donor mod) is absent from
the live `ModsConfig.xml`** — confirmed by grep against the real file, not
assumed from a doc. `guy762.mm.kotorcore` and `guy762.kotordroids` are still
active; only the weapons/armor pack itself retired. This is the single fact
that makes every fix below safe: no donor means no duplicate-defName risk from
un-gating Armoury's own absorbed copies.

## Bug 1 — 135 `MayRequire="guy762.KotORWeapons"` self-gates in Armoury

Every one of the 62 distinct defNames these gates reference (`guy762_energyshield`,
ten `KOTOR_*Crystal_*` resources, 51 `guy762_*` weapon-part defs, etc.) is
independently, unconditionally defined elsewhere in `Armoury/Defs/Absorbed_*`
with no gate of its own — verified per-name via
`<defName>X</defName>` search, the same check that confirmed
`guy762_KotORWorkbench`'s absorption. So every `MayRequire` gate on a
*reference* to one of these names (a `<li>`, a `mineableThing`, a weighted
crystal-resource entry) was evaluating false and silently dropping that list
entry — junk piles missing loot options, crystal map generation missing
colours — even though the target content has been sitting in Armoury,
permanently, all along.

Fix: stripped `MayRequire="guy762.KotORWeapons"` from all 135 occurrences
across 17 files. Verified count via grep before (135) and after (0), XML
well-formedness on all 272 Armoury XML files (0 bad), and that the referenced
defNames still resolve (unconditionally now). Deployed via
`deploy_custom_mods.py --mod Armoury --apply` (20 files, verified in sync).

## Bug 2 — 67 `PatchOperationFindMod` retag ops inert in `WeaponTags_Renormalise.xml`

Each of the 67 `guy762_*` weapon-tag retag operations in
`src/RimStarWars/StarWarsPatches/Patches/WeaponTags_Renormalise.xml` was
wrapped in `PatchOperationFindMod` gated on the mod display name "Star Wars
KotOR Weapons and Armor" — correct while the donor was live, now permanently
false since it retired, so every one of these ops was skipped outright. The
guy762 weapons themselves live on (absorbed into Armoury, defNames verbatim)
but never received the vanilla-vocabulary tags (`AssaultRifle`, `SimpleGun`,
etc.) this file exists to backfill — the exact "spawns bare-handed" bug class
this file's own header describes, just for a second wave of weapons.

**Root cause was deeper than the 67 ops**: the generator
(`src/RimMandrake/Utils/weapon_tag_audit.py`)'s `CANON_PATCH` constant still
pointed at the pre-tier-migration path `src/Jawa/Jawa_Patches/Patches/...`,
which no longer exists. Both of the generator's safety guards
(`refuse_shrink`, `preserved_block`) read `CANON_PATCH` specifically so a
scratch-path `--emit-patch` run can't fool them (see the generator's own
2026-08-22 postmortem comment) — but a *nonexistent* `CANON_PATCH` fools them
the same way: `existing_targets()` returns empty, so `refuse_shrink` would see
nothing to lose, and `preserved_block()` finds no BEGIN/END markers and would
silently drop the entire ~450-line hand-authored tail (`Tribal_Archer_Fire`,
`AncientSoldier`, the xenotype-hunter ops, etc.) on the next real
`--emit-patch`. Fixed `CANON_PATCH` to the real current location before
touching anything else.

Fix: promoted each of the 67 `PatchOperationFindMod` wrappers' inner
`PatchOperationConditional` to a bare top-level `<Operation>` — exactly what
the current generator emits unconditionally for any classified weapon (its
`emit_patch` no longer emits `FindMod` wrapping at all; these 67 were legacy
leftovers from before that rewrite, orphaned because the broken `CANON_PATCH`
meant no regeneration ever touched them). 63 of the 67 sat in the
auto-generated section; 4 (`guy762_brifle_dmr` and three siblings) sat inside
the hand-authored `BIG_WEAPON_XENOTYPE_AUDIT_1` block, gated the same
stale way — fixed identically, tag values and xpaths left untouched.

**Left alone, correctly**: 8 remaining `PatchOperationFindMod` ops in the
hand-authored block, gated on other still-active or not-yet-retired mods
(`Outer Rim - Core`, `Vanilla Factions Expanded - Tribals`, etc.) — a
different, ungated-by-this-item concern; touching them wasn't asked for and
their donor mods are still live.

Verified: substitution count (67), well-formed XML
(`xml.etree.ElementTree.fromstring`), `PatchOperationFindMod` count dropped
from 75 to 8 (the correct legitimate remainder), zero remaining occurrences of
the retired donor's display name, `guy762` weapon references still present
(content preserved, only the gate removed). Deployed via
`deploy_custom_mods.py --mod StarWarsPatches --apply`.

## What's still owed

**No live in-game verification** — the bridge was held by BENCH for the
duration of this item (owner-confirmed bridge contention earlier this
session), so this couldn't be proven against a running game or the offline
def dump (which is FROZEN, owner-only to refresh). The fix is a deterministic
XML-attribute removal, not new game logic: verified statically via exact-count
grep, XML well-formedness, and the ModsConfig ground-truth check that makes
it safe. **Owed**: once the bridge is free, confirm live via `jawa/get_defs`
that a previously-gated `guy762_*` weapon now carries its vanilla tag, and
that a previously-empty `KotORResource_JunkPile` mineable slot now resolves.

## criteria
- [x] Ground truth checked first: donor mod confirmed retired from live
      ModsConfig, not assumed.
- [x] All 135 `MayRequire="guy762.KotORWeapons"` gates verified stale
      per-defName (each target independently absorbed elsewhere) before
      removal, not bulk-stripped on a guess.
- [x] All 67 `PatchOperationFindMod` retag ops fixed, including the 4 hidden
      inside hand-authored content — found by reading the mechanism, not by
      trusting the item's literal count.
- [x] Root cause of why regeneration never caught this (stale `CANON_PATCH`)
      found and fixed, not just the symptom.
- [x] The 8 legitimately-still-gated `PatchOperationFindMod` ops (other,
      still-active donor mods) identified and left untouched.
- [x] Both fixes deployed to the live Mods folder; XML verified well-formed.
- [ ] Full live in-game confirmation (bridge unavailable this session).
