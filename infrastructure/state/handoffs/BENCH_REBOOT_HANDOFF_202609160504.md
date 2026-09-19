# BENCH_REBOOT_HANDOFF_202609160504 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609132330`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**The canon reference library is now the art-validation instrument, and the owner ruled
that CANON ITSELF is the target — an empty `## ruling` section means canon stands
unopposed, NOT that the entry is unusable.** 112 of 137 entries are unruled and every one
of them is still usable. Do not wait for his sign-off to judge a regen.

`design/RimStarWars/canon_references/` — 137 entries (45 creatures, 69 species, 23 droid
chassis). Each carries sourced canon text, a visual brief written against real reference
images, source URLs on every fact, and now **`## Must show`** (3–6 testable checkbox items)
plus **`## Engine limits`**. `AGENT_BRIEF.md` in that directory is the operating doc: read
it before touching the library, and it holds every trap this wave paid for.

🔑 **Three classes of defect that look identical in a bug report and have nothing in common
as fixes** — this is the distinction to carry:

| class | meaning | fix |
|---|---|---|
| **missing gene** | the def does not carry the trait | edit the def |
| **engine limit** | shader/mask cannot express it | new art, or more mask channels |
| **rig limit** | the pawn skeleton cannot express it | nothing — retarget the goal |

Only ~25 of 137 entries have a real limit; the rest are `none known`. Rig limits
(Ithorian neck, Kaminoan proportions, Muun body, Lasat digitigrade legs) can never be
fixed by art, and commissioning art for them is pure waste.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1. **`XENOTYPE_CANON_CORRECTION_1` — two of nine patterns still need his ruling.**
   Aptitudes (pattern 7) and invented lifespans (pattern 5) may be deliberate balance
   choices rather than errors. Everything else is either cleared or gated.
2. 🔴 **He ruled cosmetics are OFF LIMITS without asking** — *"Cosmetics require asking
   permission, as they may mess with animated faces."* That gates patterns 2, 6, 8b and 10,
   i.e. most of the visually interesting findings. `XENOTYPE_NONCOSMETIC_FIXES_1` carries
   only the released set.
3. **Four species heads set `useSkinShader: false` over a bare greyscale mask** — Bothan,
   Gungan, Duros, Twi'lek; the last two have no mask file at all. **Nobody has confirmed
   what actually renders**, and it cannot be checked from the laptop. This is the top item
   for the next time the game is up.
4. **The 0.75 `_Refurbished` tier does not exist and must be authored.** `_Repaired` is
   donor-identical, which makes it the 1.0 rung, so it is NOT the 0.75 one. Ladder is
   Wrecked 0.001 / Kludged 0.2 / Refurbished 0.75 / the original 1.0, and "repaired" is not
   a level name at all.
5. **Rekko's canon body-vision is now settings-dependent.** *"Full restoration of the
   original"* is undeliverable at a 0.75 cap and deliverable with the 1.0 mod option on, so
   whether the god of repair can ever be satisfied depends on a player's toggle. Filed, not
   resolved.
6. **The droid era column is FINISHED at 2.7%, not unfinished.** He was offered a derived
   column and chose to stop at what canon states. 1,709 of 1,757 articles genuinely have no
   era. ⛔ Do not "complete" it — that reverses a ruling.
7. **Orphan art worth wiring up:** `Textures/KotOR/Droid/gonk/` is referenced by no def
   anywhere and is the better of the two gonk assets.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `ART_PAINTERLY_RESTORATION_1` — **not touched this session.** State unchanged from
  FOUNDRY's work (`doing`, needs offline). This seat spent the window on the canon
  libraries and the Rakatan design, never on art regeneration. Next action: read the item;
  do not infer its state from this handoff.
- `PIT_TRAP_VISUAL_REDESIGN_1` — **not touched this session.** Still `doing`, `needs owner`.
  It wants his eye on the three directions already filed, and he was never asked this
  window. Next action: put the three directions to him as a question card.

**Filed this window and NOT started** (both for FOUNDRY, both cleared to run):
- `XENOTYPE_NONCOSMETIC_FIXES_1` — the released non-cosmetic fixes. Fixes belong in
  `src/RimMandrake/Utils/gen_races_mod.py`, never in the generated XML. ⚠️ Labels only,
  never defNames, without a further ruling — a defName change ripples into faction xenotype
  lists and any existing save, and this campaign ships as a frozen savegame.
- `TWILEK_TROPE_GENES_MOVE_1` — move the submissive-aggression, high-libido and beautiful
  genes off the xenotype onto individual pawns. A mechanism change, not a gene-list edit.

**Also unbuilt, from `design/RimMandrake/ancient_machines_design.md`** (now reconciled, 1027
lines, 13 UNVERIFIED collected in §8): layer 1 must publish a neutral grade-changed signal
because Ninefold's repair hook fires on full hit points and never on a grade step; Ninefold
needs the authorized generic external-impulse API for Mood; and WreckedMachines needs its
first assembly for Mod Settings.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. Also file these to LESSONS_INBOX.md. -->
All eight are in `infrastructure/state/LESSONS_INBOX.md` (commit `12ddc9ae0`). The two
that decide whether this kind of work succeeds:

- 🔴 **Backgrounded agents are killed by a stream watchdog at ~600s with no progress, and
  one died on an API ConnectionRefused with ~8 running at once.** Measured across 14 agents:
  the two large single agents lost nearly everything; **every batch told to flush output to
  disk as it went survived its own death.** Never let an agent hold results in memory.
- 🔴 **For 1,000+ fetches, have the agent WRITE A SCRIPT and run it.** A script did all
  1,757 droid articles in ~22 minutes; turn-by-turn agents died at 10 minutes having done a
  handful.

Silent tool limits that cost real work:
- **Fetcher truncates at 50,000 chars with no marker in the output** — `core/handlers.py:65`
  is a hard slice, nothing says content was cut. It ate two species' Biology sections. The
  cap is deliberate; the silence is the bug, and the owner is fixing it in another window.
- **Viewing an image >2000px in either dimension ABORTS an agent run** and killed a batch
  with 2 of 5 species unwritten. Check `sips -g pixelWidth -g pixelHeight`, view a `/tmp`
  downscale.
- **Wookieepedia: `curl` to `api.php?action=parse&prop=wikitext` works fine** — only the
  rendered HTML is Cloudflare-walled, and curl has no size cap. Page titles lie (the Rakata
  article is titled "Rakatan") and a stub main page often has its substance at
  `<Name>/Legends`.
- **zsh does NOT word-split an unquoted variable**, so `dirs="a b"; git add $dirs` passes ONE
  pathspec and fails. Loop and add one path at a time.
- **The `chore(sync)` sweep can commit your work before you do**, replacing your message
  with a generic one. It took 9 droid entries at 20:20. Commit each unit as it lands.
- 🔑 **An index column can be CONFIDENTLY WRONG rather than merely empty, which is worse.**
  The droid index's continuity was wrong on **1,273 of 1,757 rows** (72%), and its `in repo`
  column mapped a repo sprite to entirely the wrong canon droid. When detailed entry-writing
  contradicts a summary table, suspect the table.
- **A blind rename hits quoted text too.** `s/Defunct/Wrecked/` rewrote words inside the
  owner's own verbatim quotes. Pre-`git show 432e4410f` has the original wording.

## Closed since the last handoff (2)

- `BACTA_PAWNINTANK_RECON_1` — fdca467f3f0c787fd07e6ebb340b682022bd32ad
- `SPECIES_CANON_LIBRARY_1` — 47de84d5f

## Filed and still open (11) — the next seat's queue

- `PYRELANDS_ANIMALS_GENSTEP_1` — GenStep_Animals NREs on Pyrelands mapgen (BiomeDef.CommonalityOfAnimal ArgumentNullException via Alpha Animals commonality postfix) — wild fauna genst
- `PYRELANDS_MAPGEN_SCRUB_1` — Pyrelands mapgen: no ancient dangers, no scattered rock chunks
- `ANOOBA_DRAWSIZE_FIX_1` — Anooba renders far oversized on Pyrelands map
- `FIREHAWK_FLIGHT_BEHAVIOR_1` — FireHawk and all flying fauna get donor-style flight animation
- `BOOMSNAKE_CUT_CONFLICT_1` — GR_Boomsnake wired live while its ThingDef is Cherry Picker cut
- `ECOSYSTEM_PYRAMID_LAW_1` — Food-pyramid law: small critters outnumber large in every biome roster
- `NARRATIVE_DICTIONARY_PILOT_1` — Narrative dictionary pilot (batch 1): featurize ~30 placeable objects by claim/mood/Lynch-spatial-function/ISO-communicative-act/state, author ~8 vign
- `EVENT_TRACE_PROPS_LIBRARY_1` — Design a props library of event traces: blaster marks, burn/scorch marks, floor scrapings, drag trails, impact spall and other signs of something havi
- `RAKATAN_ARCHOTECH_MACHINES_1` — Design session with the owner: extend Wrecked Machines into the core Rakatan tech trait - robust, survives, degrades gracefully; mobile structures inc
- `DROID_CANON_LIBRARY_1` — Broad canon reference library for Star Wars droids - deliberately wider than current game content since droids are candidates for addition - adding ma
- `XENOTYPE_CANON_CORRECTION_1` — Nine patterns of xenotype defs disagreeing with canon, found by the species library - wrong-species namers, borrowed heads, placeholder descriptions, 

## Commits

```
e13c6148c All 137 checklists in place, and the continuity fork restored on evidence
4af7a7567 Checklists for the n-s entries
f64c4430b Sprite skill never said what north and south MEAN — that omission has a price
d52031fe8 Symmetry is a free facing check, and the donor art beats ours on it
3b406be89 h-m checklists, and a third class of limit: the pawn rig
ebdbdfe8e Checklists for the a-c entries, including a Bothan that checks negatives
226aa15ef Must-show checklists and engine limits for the d-g entries
d6873f167 Height measured on haze, not silhouette — two rows I cleared are the worst two
8e93eb153 Canon is the validation target, and every entry gains two checkable sections
4f6ee61d2 chore(sync): laptop 2026-09-15T21:39:10-07:00 — Transient/pyrelands_art_review/pyrelands_art_decisions.json
dfa55ba9a All twelve checks refuse, inside the artpipe — so the retry loop needs a cap
ab7883b91 Art review as facts, not scores — the twelve rules and why two tiers
0e742dbe3 Cuisine ingredients go wide: his quantifiers are the spec, not a shortlist
bc53af332 Five lessons from the Pyrelands art sheet, chiefly: don't restart a sidecar
5e3a2a586 Droid index continuity was wrong on 72% of rows
ccc60ff61 Pyrelands art sheet: three facings a row, and the facing law is still broken
68ab65f61 Ladder settled: Wrecked, Kludged, Refurbished, and the original at 1.0
0c91c6629 chore(sync): laptop 2026-09-15T21:02:18-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 6 more
432e4410f Reconcile the ancient machines spec with rulings made after it was written
12ddc9ae0 Bank eight operational lessons from the canon-library sweep
e3341827c All 23 droid chassis done, plus orphan gonk art nothing references
cec1a65a3 Specialist droid chassis, and four errors in our own index
c6e96b4ad Utility droid chassis, and two index pairs proven to be one chassis each
8e12e7bf6 Three more droid chassis: B1A, DSD1 dwarf spider, KX-series
7f6f43ca8 chore(sync): laptop 2026-09-15T20:20:49-07:00
fe5fe7c59 Extend the brief to droids: one entry per chassis, not per canon variant
6e733c9cd Record that the droid era column is finished at 2.7%, not unfinished
6261d3538 Era fill returns a negative result: canon does not record it for 97% of droids
a1cbe6490 chore(sync): laptop 2026-09-15T19:29:12-07:00
32ec82c2e Cosmetic genes are off limits: gate most of the findings, release the rest
2e813982e chore(sync): laptop 2026-09-15T19:11:56-07:00
f84143b34 Close the species canon library: 69 of 69
47de84d5f Species library complete: all 69 entries, and montrals that are decoration
422ce08ab Batch E: a fourth aquatic species that cannot breathe water
eeddc3484 Batch H, and a Duros head nothing can colour
0150b31d1 File the xenotype canon findings as nine patterns, not sixty mistakes
6b822500f Batch J, and skin colour that never reaches the face
be792759a Zabrak and the roster: a Mimbanese wearing a Tusken's head
75f8339ca Four more entries: the canon pages omit the traits these species are known for
279bfd4f0 Six more entries, and a Kaminoan with no neck
6a13b9079 Oversized images kill a run, so check dimensions before viewing one
3bae44878 Fourteen more entries, including a species canon refuses to draw
a88a65a72 Note Fetcher's 50,000-character cap, since it silently ate two Biology sections
d211f3acc Ten more species entries, and two aquatic races that cannot breathe water
9bb1c5eef Seven more species entries: anzati, aqualish, chagrian, herglic, nautolan, pantoran, snivvian
6cf288bd6 curl reaches the wiki API directly, so stop routing every fetch through Fetcher
01a6ea4a4 11 more species entries, and they found real art bugs in the shipped defs
cc431b9d8 Droid index QA: 1766 -> 1757 rows, and the build was already clean
cf5d56d00 Write the species-entry brief down once instead of re-briefing every batch
bd34ff636 Droid index at 1,768 rows, the race roster, and 14 image-only entries
7ce3aee14 1.0 is the ordinary modern machine, so 'exceeds modern' is withdrawn
6e149cd77 chore(sync): laptop 2026-09-15T17:22:10-07:00
b5899b14d 11 race canon entries, plus the revised grade ratios
0ac41611a WreckedMachines is not a texture reskin, so remove its false settings exemption
f9478c297 Ancient machines: one spec for the three layers and the grade ladder
da5cee683 File the two canon-library research items
cec752071 Rakatan: three layers, and no Rakatan word below the middle one
808c06960 Rakatan: three grades with real ratios, and the mod splits in two
80ddfdd1f Rakatan design session: nine rulings banked, chief among them that nothing equals the original
fc1373743 chore(sync): laptop 2026-09-15T12:06:45-07:00
86308d312 narrative dictionary: implementation plan for batch 1
6bc96eaf7 Archotech is Rakatan: land the ruling and propagate it
8ff4bd8a5 Narrative dictionary: design approved, pilot filed, Rakatan archotech captured
6e9c884b2 chore(sync): laptop 2026-09-15T05:52:19-07:00
e5bd51e9b chore(sync): laptop 2026-09-14T20:40:50-07:00
107ac16c0 Gizka 0.3 -> 1.0: pyramid law puts the grain on top (owner: 'Yes on Gizka')
8ac82bd03 BOOMFAMILY_PAWNKIND_CUTS_1: close (ledger sync)
cc582d632 BOOMFAMILY_PAWNKIND_CUTS_1 + BOOMSNAKE_CUT_CONFLICT_1: close the pawnkind gap, resolve the timeline conflict
0390c772b Barbslinger south facing wired (r3) — facing regen wave complete
5087c0f19 BOOMALOPE_CUT_EVERYWHERE_1: propagate the owner's "Absolutely no boomalopes"
dd83d8a36 PYRELANDS_FACING_REGRESSION_1: wire 5 of 6 facing-fixed regens, refuse 1
54e2fa209 PYRELANDS_FACING_REGRESSION_1: file painterly regen jobs for the wrong-facing sprites
c6e21d2d2 artpipe facing prompts spell out the camera convention; canon regen item repointed
4afc6923e PIT_TRAP_VISUAL_REDESIGN_1: pit trap visual interface spec, 3 directions for Thursday
139c4342e ART_PAINTERLY_RESTORATION_1: propagate the restored painterly law into artpipe code+docs
1f1b8ab19 PYRELANDS_FACING_REGRESSION_1 + ANOOBA_DRAWSIZE_FIX_1: Boomsnake east mirror fix, Anooba oversized-drawSize patch
fc10912f3 Scorch-fruit pod: four half-buried candidates for owner review
20387631a Pyrelands flora: drago tree, agave, dandelion evicted from wildPlants
776b07f96 Quickgrass approved art installed: tall green-gold variants live, tint removed
c6c82063a Quickgrass green-gold stage sprite candidates for owner review
08b53e328 Furnace-beast fireproof stats + capacitor lore; razorjack -> sytheclaw identity patch
9fc17ad90 Quickgrass growDays 1 — owner revised the 3-day call same day
10165d659 Pyrelands: mapgen scrub (preventGenSteps), quickgrass growDays 3, clear_chunks.py
c1bbb05cd Pyrelands: preventGenSteps blocks RockChunks+ScatterShrines; clear_chunks.py library script
cb06457c2 PYRELANDS_GRASS_SATURATION_1 filed; palette ruling noted on PYRELANDS_FLORA_ART_IDENTITY_1
40dd4d168 DROIDWORKS_FORMAT_TIERS_1: live re-test, box 1 confirmed, root cause found
83d23ae4f BIOME_KITS_PUSH_TO_TEST_1: record final status after the offline push
63d29b530 Rebuild RimMandrake.EnvironmentalHazards.dll after Greentide M3/M7
035c903af mark-clean GREENTIDE_MECHANICS_2 M3/M7 build pass files
3bcf80ccf GREENTIDE_MECHANICS_2: M3/M7 build pass, steam devil vortex + Lunger ambush
d5d55c63a Rebuild RimMandrake.EnvironmentalHazards.dll after Greentide M4/M5
1c0eedc96 mark-clean GREENTIDE_MECHANICS_2 M4/M5 build pass files
6f7f5ff61 GREENTIDE_MECHANICS_2: M4/M5 build pass, the Roil + Breaklight
00ee47b00 rimflow: bridge released after Pyrelands walk staging
88cdc3b2f PYRELANDS_CREATURE_RERENDER_1: wave-2 tally, deploy holds, Codex weekly wall Sep 19
751ac722d ART_PAINTERLY_RESTORATION_1: Zeer + Dalgo full painterly sets, rear-view norths, canon-library-cited
91f69301c ART_PAINTERLY_RESTORATION_1: Mantistanis E+N (rear-view north) + Boomsnake E painterly; sets incomplete, deploy held
3a255e2bb ART_PAINTERLY_RESTORATION_1: Razorjack full set + Nuna (m N/S interim-copied from f) + Gizka easts, painterly via Codex before weekly quota wall
06e04cc0b ART_PAINTERLY_RESTORATION_1: EmberGrass A/B/C repainted painterly (Codex) before weekly quota wall
d10a23cae Rebuild RimMandrake.EnvironmentalHazards.dll after Fever Wood F6/F7 + Greentide M6
b6799ab8a mark-clean GREENTIDE_MECHANICS_2 M6 build pass files
0dedc6cfa GREENTIDE_MECHANICS_2: M6 build pass, three-feller tree fall
1c47392bb mark-clean FEVER_WOOD_MECHANICS_1 F6/F7 build pass files
1741b389a FEVER_WOOD_MECHANICS_1: F6/F7 build pass, boughway network + fever trunks
ff348403a Rebuild RimMandrake.EnvironmentalHazards.dll after Greentide M1/M2 + M9/M12
647b306fe mark-clean GREENTIDE_MECHANICS_2 M9/M12 build pass files
07118c4e6 GREENTIDE_MECHANICS_2: M9/M12 build pass, root causeways + the Greatbole
9a4890127 mark-clean GREENTIDE_MECHANICS_2 M1/M2 build pass files
946fc0b04 GREENTIDE_MECHANICS_2: M1/M2 build pass, wet-bulb overwhelm + dry-air blower
58cd1139a Rebuild RimMandrake.EnvironmentalHazards.dll after Scarlands build pass
2c3737cba mark-clean SCARLANDS_MECHANICS_2 build pass files
52c8c982c SCARLANDS_MECHANICS_2: build pass, §2/§3/§4/§5 wired to real content
9cc0cd8e1 Rebuild RimMandrake.EnvironmentalHazards.dll after Miasma M3, Scald S5, Sump S4
735d5bef7 mark-clean SUMP_MECHANICS_1 S4 files (dread field, wander JobGiver, filth trail, placeholder mouse, filth-acceptance patch)
b3a646c3f SUMP_MECHANICS_1 S4 build pass: mouse-line telegraphy
ea9d3aedd mark-clean SCALD_MECHANICS_1 S5 files (sail scatterer validator, GenStepDef, register patch, IncidentDef, translation)
a90656d07 SCALD_MECHANICS_1 S5 build pass: bubble-sailor scatterer + walker-surfacing incident
92a5c740c mark-clean MIASMA_MECHANICS_1 M3 files (stranding pools, JobGiver, ThinkTree)
c76fc40a0 MIASMA_MECHANICS_1 M3 build pass: stranding pools and the stranded
50e7917cc rimflow: close BACTA_PAWNINTANK_RECON_1
fdca467f3 BACTA_PAWNINTANK_RECON_1: close with findings (growth-vat renderer re-entry; MIT BioReactor Continued fork)
cc382ee92 Rebuild RimMandrake.EnvironmentalHazards.dll after Forge F3/F4, Scarlands, Miasma M2
34e253cf7 mark-clean MIASMA_MECHANICS_1 M2 files (gradient axis, repaint, surge extension, surge condition)
3901f320b MIASMA_MECHANICS_1 M2 build pass: breath-tide surge
6b6231bb4 PYRELANDS_CREATURE_RERENDER_1: walk relocated to daylight tile 59952 (104504 is polar-dark); staging route + open owner questions; two lessons
28961d188 mark-clean FORGE_MECHANICS_1 F4 files (channels, biome validator, entrance/floor/scatter defs)
378f67436 FORGE_MECHANICS_1 F4 build pass: foundry tower dungeon shell (single-floor)
bc306ddc1 mark-clean SCARLANDS_MECHANICS_2 files (RC5 filter, severity floor, Sentinel lord)
8801d8429 SCARLANDS_MECHANICS_2 spike pass: RC5 scaria-arm filter, mark severity floor, Sentinel defend-only lord
83cb8f92b mark-clean FORGE_MECHANICS_1 F3 files (vapor columns, drifter, wander JobGiver, wiring patch)
0cdbc22b8 FORGE_MECHANICS_1 F3 build pass: vapor-column pasture-binding for sky fauna
6b987d33c File BIOME_KITS_PUSH_TO_TEST_1: umbrella tracker for the biome-kits push
7c9f2c7b7 Revert "ART_PAINTERLY_RESTORATION_1: Iriaz/Nuna/Gizka regenerated painterly, rear-view norths (Iriaz UNGATED - no canon library entry; Nuna/Gizka cite starwars_iconic_creatures.md)"
02a4d5ec1 mark-clean SUMP_MECHANICS_1 S3 files (bulge, wake relay, station eater, gen step, register, job)
212775b67 SUMP_MECHANICS_1 S3 build pass: tar beast set-pieces (placement + wake + eater scaffold)
f209d892c ART_PAINTERLY_RESTORATION_1: Iriaz/Nuna/Gizka regenerated painterly, rear-view norths (Iriaz UNGATED - no canon library entry; Nuna/Gizka cite starwars_iconic_creatures.md)
3ade11b7a mark-clean 15 files: FORGE_MECHANICS_1 F2/F5/F6 build pass
b62604fad mark-clean M6 files (creche scatterer, marker, despoil memory)
ce17e0865 lesson: pathspec commits are mandatory in the shared worktree
935cbe93e rimflow sync: file PYRELANDS_ANIMALS_GENSTEP_1; two lessons (player-map regen route, staged-index sweep)
645b93f2e ART_PAINTERLY_RESTORATION_1: revert Anooba/Orray/FireHawk/FurnaceBeast to painterly v1 (owner ordered Pyrelands-wide painterly regen 2026-09-14)
197746425 mark-clean RM_WeatherOverlay_GreentideRoil.cs (GREENTIDE_MECHANICS_2)
dd56bb453 GREENTIDE_MECHANICS_2: file+spike the Greentide kit build, reconcile against already-shipped M3/M5/M8/M11
```

## Game / bridge / tree state at wrap

- <could not run /Users/mandrake/dev/RimMaster/game: [Errno 13] Permission denied: '/Users/mandrake/dev/RimMaster/game'>
- Bridge: FREE    since 2026-09-14T18:25:31Z

Working tree clean apart from untracked `Transient/`.

