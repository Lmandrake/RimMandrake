# STARWARS_DONOR_PORT_LABEL_COLLISIONS_1 — 62 label collisions between donor SW-animal-collection defNames and their RSW_ ports

Filed by FOUNDRY, 2026-09-23, as a side finding while closing
`DUPLICATE_CANON_DEFNAME_PAIRS_1` (gizka/kreetle/nuna/worrt — owner-ruled merge
onto the RSW_ port, done at `7562e534e`). That item's own step 4 asked for "a
selftest that flags two defs whose label matches while their defName differs" —
built as `src/RimMandrake/Utils/label_collision_check.py` +
`selftest_label_collision_check.py`. Its first live run against the current
(pre-reload) `defs.sqlite` found **62 label collisions**, not 4. This item is
that finding — nothing here has been fixed.

## What the checker measures

For every `ThingDef` carrying a `race` block, its `label`. For every `BiomeDef`
in the dump, every `animal` entry in `wildAnimals`/`coastalWildAnimals`/
`pollutionWildAnimals` (the three arrays `BiomeDef.CommonalityOfAnimal()`
walks — the actual reachability mechanism, not just "the def exists"). Any
label backed by >1 distinct CAST defName is reported. A donor def that still
exists but is no longer cast by anything (the post-fix state for gizka etc.)
is correctly NOT reported — see the selftest's own unit test for that case.

Run it: `python3 src/RimMandrake/Utils/label_collision_check.py` (exit 1 if
any collision exists; the list below will drift as biomes change, so re-run
rather than trusting this snapshot).

## What the 62 look like — two different shapes, not one bug

**Shape A (the gizka/kreetle/nuna/worrt shape, likely small in number):** WE
hand-wired the donor's bare defName into one of our own `RUT_`/`RM_` BiomeDef
files, alongside the RSW_ port wired into a different one. This is what
`DUPLICATE_CANON_DEFNAME_PAIRS_1` fixed for 4 animals — the fix was a
same-repo defName repoint, no design call needed once the survivor was picked.

**Shape B (most of the 62, looks structurally different):** the donor mod
(`mlie.starwarsanimalcollection`) patches its OWN bare defName into biomes
that are **not ours** — `GlacialPlain`, `Glowforest`, `Grasslands`,
`LavaField`, `Scarlands`, and a long `ZBiome_*` list (another donor's biome
set, "Biomes! Islands" or similar, not confirmed here) — while our RSW_ port
is cast only inside `RUT_*`/`RM_*` files we own. Example (`ronto`):

```
RSW_Ronto   cast in: RUT_Desert
Ronto       cast in: GlacialPlain, Glowforest, Grasslands, LavaField,
                      RUT_AridShrubland, Scarlands, ZBiome_AlpineMeadow, ...
                      (14 biomes total, only one of which — RUT_AridShrubland
                      — is ours)
```

This is NOT something a same-repo XML repoint can fully close: the donor
mod's own patches (outside this repo, in its Workshop folder) are the ones
casting the bare defName into those 13 non-ours biomes, and we do not own
that content. Suppressing it would mean either (a) a `FindMod`-gated
counter-patch stripping the donor's bare defName from every biome
(ours and not), or (b) accepting that as long as that donor mod is active,
its own creature roster and ours will always double up somewhere, and the
real fix is narrower — just making sure OUR OWN biomes never wire the loser.

**`shiro`/`shiro-trap` are in this list too** — `DUPLICATE_CANON_DEFNAME_PAIRS_1`
named these explicitly out of scope ("Do not touch `Shiro`/`RSW_ShiroTrap`",
"the case to be careful with"), so whatever the resolution here turns out to
be, Shiro needs the same care that item gave it, not a blanket sweep.

**`deer`/`PoisonDeer`** is a different animal under a different pattern (not
an obvious donor/port pair by name) and should be checked separately before
assuming it belongs in the same bucket — flagging, not resolving.

## Full list (2026-09-23, pre-reload dump — will drift)

Re-run `python3 src/RimMandrake/Utils/label_collision_check.py` for the
current, authoritative list. 62 labels at filing time: Dragonsnake, Jamel,
Kwi, Peko-peko, anooba, bantha, beldon, bolotaur, clodhopper, convor, dalgo,
deer, dianoga, eopie, falumpaset, fambaa, feral grazer, frilled gorg,
gelagrub, gizka (now fixed), gorg, granite slug, greater krayt dragon,
gutkurr, hawk-bat, horax, hrumph, hssiss, iriaz, iridonian reek, jakobeast,
jimvu, k'lor'slug, kinrath, krayt dragon, kreetle (now fixed), krykna,
longtail gorg, lylek, mantrap, mott, nerf, nuna (now fixed), orray,
pustule hornet (3-way, RSW_-only — different shape, check separately),
pustule queen (2-way, RSW_-only — same), ronto, runyip, scurrier, shiro,
shiro-trap, shyrack, sketto, tee muss, uvak, varactyl, voorpak, war wyrm,
whisperbird, worrt (now fixed), wraid, zeer.

Note: `pustule hornet`/`pustule queen` collide between three/two **RSW_-only**
defNames (`RSW_ColonyPustuleHornet`/`RSW_PustuleHornet`/
`RSW_PustuleHornetSpawned`, `RSW_ColonyPustuleHornetQueen`/
`RSW_PustuleHornetQueen`), not a donor/port pair — likely a caste-naming
collision (worker/spawned/colony forms sharing one label deliberately?) rather
than the DUPLICATE_CANON_DEFNAME_PAIRS_1 defect shape. Check before assuming
it needs the same remedy.

## Watch out

- This needs a decision on the Shape B question above before any bulk fix —
  BENCH/owner call, not a FOUNDRY judgment call, since it may mean authoring
  a donor-wide counter-patch rather than N individual repoints.
- Don't reuse `DUPLICATE_CANON_DEFNAME_PAIRS_1`'s forensic pass as a template
  and blindly run it 58 more times — that pass's own conclusion (verbatim
  fields byte-identical) won't hold for every pair here; check each.
- The checker itself is not the risk here — it is unit-tested and
  conservative (only CAST defNames, never a bare "def exists" scan). The risk
  is scope creep: fixing 58 more animals without the same per-animal care
  `DUPLICATE_CANON_DEFNAME_PAIRS_1` used (which is exactly what excluded
  Shiro) would be the wrong kind of fast.
