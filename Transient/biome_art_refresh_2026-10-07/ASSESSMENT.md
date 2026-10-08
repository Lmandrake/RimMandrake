# Biome art refresh — Phase 1 assessment (2026-10-07)

Owner request ~19:20 PDT: refresh every biome art sheet after the WSL crash. First, check whether any art needs to be wired, deleted or moved.
The detail behind each line below is in the per-group files in this folder: `phase1_G1.md` (Abyss and the desert family), `phase1_G2.md` (Leaning Scrub, Lantern Deeps, Slime, Contagion, Nightside Ice), `phase1_G3.md` (the four seas), `phase1_G4.md` (Webwork, Pyrelands, Rust Cathedral, Sump, Warscar) and `phase1_G5.md` (orphans, dangling and misplaced textures).
The sheet URLs and counts are in `INDEX.md`.

## 1. Inventory
- There are 27 per-biome sheets in `Transient/biome_ffar/`.
  - 18 carry human decisions.
  - 9 were never reviewed and hold only the pre-fill: Cauldron, Feverwood, Flooded Canyon, Greentide, Miasma, The Forge, The Rot, Wasteland and Weeping Stones.
- The artpipe queue was empty (0 pending, 0 active).
- `art.py backfill artpipe` recorded the 3 renders that were not yet in the ledger.
- The census was regenerated. Rosters had moved since 10-05:
  - Abyss donor ports were renamed `AA_*` → `RM_*`.
  - `RSW_` → `RM_` moves happened in Leaning Scrub, Rot and Cauldron.
  - Lantern Deeps lost 13 rows.
  - Warscar ports were renamed.
  - The Scald → Twilight Sea moves went through.
  - Feverwood gained 6 rows.
- **Long Shade (`desert_sheet_2026-10-04`, 58 human decisions) had never been ingested.** The art ledger had 0 ruling events for it. It is now ingested (with `--defer-redo-jobs`, because its older jobs carry no verbatim note).

## 2. Owner rulings not yet executed
An audit of every human decision (pick / variant / redo / purge) against the bytes in `src/` and the artpipe jobs raised 131 leads. Most were false positives:
- kept "variants", which are recorded as protected in the ledger and by design are not installed;
- donor rows ported under new names;
- redo renders that finished but stay uninstalled until you pick them.

The real gaps:
- **Executed tonight:**
  - Ommok pick B was never installed (it still showed the Sandmaw art). Now installed.
  - Bokka pick B was never installed: the def still pointed at the donor Stoneback texPath, contrary to the structural note. The art is now installed in the RM tier and the def is repointed.
  - Stillsand LightPipeNub variant B is now installed into its Graphic_Random folder.
  - Shadows were refit for Bokka and Ommok.
- **Finished but uninstalled redo renders** are now on the sheets as new columns, flagged "NEW ART since your … ruling". The redos for Dulloth, Kollavane, Norrveth, Vennick, Noothelm, Hollu (waveglass) and the 40 Long Shade rows are waiting for your pick there. None was installed blind.
- **Kept variants that cannot install today:** 17 Leaning Scrub creature variant sets (51 PNGs) and 2 catch items (HessalCatch, AluunCatch). Their defs have no variant slot, so they need `alternateGraphics` / Graphic_Random wiring. That is build work, not a ruling. The commands are in `phase1_G2.md` and `phase1_G3.md`.

## 3. Finished art not on any sheet / not installed
- After the rebuild, every finished render that joins a row by texPath or by name is on its sheet.
- The failed tooke-trap redo v3 is on the Webwork sheet as column D.

## 4. Orphans, dangling texPaths, misplaced and uncommitted textures (`phase1_G5.md`)
- **Untracked textures:** 9 PNGs (FlowWorks Doors ×4, Excavation wall faces ×2, WreckedMachines distillation ×3). They were generated 2026-10-06 and are in the ledger. **No def or C# references any of them**, and none was ruled. They were left uncommitted.
- **Dangling texPaths:** 24 distinct paths in our namespace resolve to no file. Among them:
  - Cauldron dew flowers;
  - Greentide Kaddrath and Greatbole;
  - YearningFruit harvest;
  - Miasma Ismerrow and Braskeen;
  - Long Shade GreatDevourer and Groundrunner variants, and the Dakkra rest pose;
  - Stillsand Drazzik swim pose;
  - `RSW_ZakkroEgg`.
- **Orphans:** 321 PNGs are unreferenced. Most are legitimate (225 donor-path overrides, 24 ArtOverride mods). 68 in our own namespace are unknown, and 4 are stale Pyrelands quickgrass copies. Nothing was deleted.
- **Misplaced:** 38 real cross-mod texture dependencies. Greentide/TerminalBiomes/TheSump depend on UtinniPatches, and Long Shade depends on SWBestiary's BMT_Caverns paths.

## 5. Mechanical fixes done
- `94dc78ef8`: **Fixed the browser gate hang.**
  - Cause: the flip-book player re-requested a 404ing frame every 66 ms in the gate's image-less copy, so headless Edge never settled. Every sheet with a flip-book row failed requirement 13 by a 20-minute timeout.
  - The player now advances only after a frame has loaded, with a selftest.
  - Sheets also now flag rows whose art is new since your ruling.
  - The census was regenerated in the same commit.
- `70ec8378e`: Long Shade ingest; Ommok B, Bokka B and LightPipeNub variant B installed through `art install --ruling`; Bokka texPath repointed; shadows refit. Not deployed, because the game is loading.
- Decisions carried to renamed rows (31). Each decisions file was backed up as `*.bak-carry-20261007`.

## Needs owner
1. Abyss Ossumatha north/south and Olumetha south: the v4 renders failed the "pitch black" gate. Accept them or requeue?
2. Abyss NightMule puppy, baby and female extra-graphic picks: these graphics were not carried to RM_Aveluthia. Re-pick there?
3. Purge `a25f92f19950` (Ossik north) is still live in Long Shade, SWBestiary and AncientShieldedTurret. Purging it strips all three. Blue Desert's Ossivel variant D is the same picture.
4. Stillsand Duumma north/south, and the KraytDragon redo.
5. Long Shade Dewback, Falumpaset and TeeMuss redos failed the canon gate as near-passes. Accept, or requeue with a stronger note?
6. The textures of cut creatures are still on disk: MatureFleshbeast, Ossik, Kudda, Thurra. `art.py` has no retire verb, so removing them needs your words through `artledger.retire`.
7. Leaning Scrub Vurra: your main click was the donor A, but your by-name pick was B. Install B and repoint the def?
8. Venomvine Thicket pick C would go into the Graphic_Random folder shared by 7 other venomvines, so they would all gain it. OK?
9. The Brambles and CreepStern renders go to the owned ports, but the Arid Shrubland roster still spawns the donor defs.
10. Anooba, Kreetle, Massiff and Qormot redos are partial (some facings failed).
11. The Grank, Lothcat, Whisperbird and Nysyllin redos failed the canon gate, and no later render exists.
12. Contagion Ikee: you clicked B (a fresh render), but your note asks for the earlier art, which is what is live.
13. Scurrier by-name C has no slot. Gorg E and Longtail B are swim renders kept as body variants.
14. Twilight Lunoowa: you both kept and purged the same bytes.
15. RSW_Faa: the old art is owed to the new "Scaa Lumsigh" fish before the redo overwrites it.
16. RSW_Mee: the north/south redos failed canon, and the old art is owed to a new Greentide river fish.
17. Webwork Brimlock purge: the purged bytes are also the live Venomvine and Kudda east art.
18. Rust Cathedral Vozzik C purge hits the live RM_Vozzik (Stillsand, Warscar, Nightside Ice).
19. Sump Dredgel purge is waiting for a replacement pick (the v2 renders are on the sheet).
20. The Webwork sheet is still not stamped `ruled`. Your 23 clicks are real. Stamp it?
21. The 9 untracked FlowWorks/Wreck PNGs are referenced by nothing. Wire them or bin them? (Another agent's work from 10-06.)
22. Wiring for kept variants: 17 creature sets and 2 catch items. Build it now, or leave the variants recorded only?

## Proposed regen (NOT queued)
- Sketto north/south, derived from the east you kept (the 10-06 v2 jobs failed with no render).
- FrilledGorg E and G, and Gorg H: each is east-only and needs derived north/south.
