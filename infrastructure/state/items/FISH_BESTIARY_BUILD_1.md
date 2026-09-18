## spec
Full spec: `design/Jawa/worldbuilding/fish_bestiary_commission_2026-09-10.md`
(the ratified proposal — 32 new `RUT_` species across 8 registers on 7
waters, 4 prize items, 6 rare-catch tables, the 4 owed defs: Scald
thermophile shoal, Cathedral coolant eel, Wasteland brine-battery, Twilight
shoal). That doc's `## 6. Questions for the owner` is now fully ruled (see
its own `### Rulings (owner, 2026-09-18)` block) — read it before starting,
it settles every open call this build would otherwise have to guess at.

## verify
- Every fished water has its proposed table (buckets, weights, rare
  catches) built and validated.
- `RUT_MeeCatch`/`FaaCatch`/`LaaCatch` exist as our own items with our own
  art (not Mlie's `swfish_Faa`/`swfish_Laa`) — the ruling was OURS, not a
  MayRequire fallback pairing.
- `GREENTIDE_FISH_ITEMS_FIX_1`'s engine bug (BiomeFishTypes_Greentide.xml
  wires race defs, not item defs, into `fishTypes` — a net makes a bare
  `Pawn`) is fixed as PART of this build, not left to its own item.
- The bladderboil catch (Scald, uncommon 0.5, per the hydrocarbon
  commission's own spec) ships with THIS mod, not that commission's.
- `swfish_` four (Burra/Daggert/Nyork/See) retired once the six Weeping
  Stones RUT species land — don't retire early, don't ship both.
- `validate_patch.py` clean; live-quicktest a fishing pass on at least the
  Weeping Stones and Greentide waters (the two that changed mechanism, not
  just roster) before calling this done.

## criteria
A correct v1: all 32 species + 4 owed defs exist, wired into the correct
per-biome mod (see Watch out), every catch table resolves to a real item on
a live fishing pass, and the Greentide creature-instead-of-item bug is gone.

## Watch out
- **Mod shape is per-biome, not one shared fish mod.** The owner ruled
  "Biomes" then clarified "per-biome mods" when asked — each water's fish
  defs belong alongside that water's OWN existing biome mod (Pyrelands-style
  precedent), not a new `AshkarrWaters` mod and not folded wholesale into
  `UtinniPatches`. If a water has no dedicated biome mod yet, that's a real
  open question this build has to answer per-water, not by inventing one
  shared home to dodge it.
- **Names are final as shipped nicknames** — *coolant eel*, *the silver*,
  *the owner*, *the sailor* for the 4 owed defs. No rename pass owed; don't
  hold the build waiting on "real" names that were explicitly declined.
- The BMT pair (Cracked Lands) is now PERMANENT — don't build any
  retirement/placeholder-swap logic for it.
- `RUT_LungerFry` ships now, ahead of the Lunger creature existing in the
  roster — its parent-creature link is a forward reference, not a bug.
- Both optional hediffs (veen coolant load, drazz raw shock) ship in v1 —
  don't defer them as a "v2 polish" item.
