# Mod-list swap — CHECK owns this

The live list is
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`.

🔴 **`ModsConfig.FULL.LATEST.xml` is the owner's real list. Restore it before he plays.
Nothing here is authoritative about the game until it is copied back.**

⛔ **This file does not state the count, on purpose.** It moved 583 → 578 → 576 → 577
between 2026-08-13 and 00:52 on 2026-08-20 — twice within eleven minutes. Any number
written here is stale before it is read. **Count it:**

```bash
python3 -c "import xml.etree.ElementTree as ET,sys; \
print(len(ET.parse(sys.argv[1]).getroot().find('activeMods').findall('li')))" \
  infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml
```

⚠️ `grep -c '<li>'` does NOT work on these files — the elements are not one per line,
and it also counts the 5 `knownExpansions`. On the live file it returns **6**.
Timestamped siblings are history; `LATEST` is the one to restore.

```
python3 src/RimMandrake/Utils/modlist_swap.py --status
python3 src/RimMandrake/Utils/modlist_swap.py --minimal    # swap to the test list
python3 src/RimMandrake/Utils/modlist_swap.py --restore    # put the owner's list back
```

⚠️ **RimSort and RimWorld both write this file and neither tells the other.** Do the swap
with the game DOWN and RimSort not mid-edit, and re-capture FULL if the owner has changed
his list since the timestamp above.

🔴 **A packageId rename does not change the mod SET, so nothing here warns you.**
Both saved lists are plain id lists with no folder, name or version beside them: an id
that no longer exists is dropped by RimWorld at startup **silently**, and every count in
this directory still reads 585. `modlist_swap.py --status` shows `UNRECOGNISED`, which is
the same thing it says when the owner adds a mod — indistinguishable. ⇒ **After any
`packageId` change, re-capture `FULL.LATEST` from live and hand-map `MINIMAL`, in the
same commit as the rename.** The check that actually proves it is resolving every id in
a list against the `<packageId>` in every installed `About/About.xml` (Workshop root
included) — a count cannot.

---

## 🔴 CURRENT MOD SET — three-tier packageId rename, 2026-08-31

**Both saved lists held PRE-RENAME packageIds** (`RENAME_VERIFY_WINDOW_1`, FOUNDRY).
Naming Phase 2 renamed 23 of our 24 active `mandrake.*` ids to `mandrake.<tier>.<name>`
and rewrote the live `ModsConfig.xml` — but neither saved snapshot was updated, so a
`--restore` would have written 23 dead ids and silently deactivated every renamed mod of
ours, and the 19-mod `MINIMAL` list would have loaded without Inhabited, JawaIonWeapons
or Droidworks.

- `FULL.LATEST.xml` re-captured from live (md5 `e9819939`, 585 mods either way). The
  pre-rename file is preserved at `ModsConfig.FULL.20260830_pre_rename.xml`.
- `MINIMAL.xml` hand-mapped: `mandrake.inhabited` → `mandrake.rm.inhabited`,
  `mandrake.jawaionweapons` → `mandrake.rsw.ionweapons`, `mandrake.droidworks` →
  `mandrake.rsw.droidworks`.

**Live is the authority here, and it was checked rather than assumed:** all 24 `mandrake.*`
ids in the live file resolve to an installed mod's own `About.xml` packageId, the
non-`mandrake` 561 entries are byte-order-identical to the pre-rename list, and the
old↔new mapping is 23-for-23 with `mandrake.jawa.patches` deliberately unrenamed
(Jawa_Patches is parked for Phase 3).

| out (23, pre-rename) | in (23, renamed) |
|---|---|
| `mandrake.inhabited` · `mandrake.jawafactionslate` · `mandrake.jawaplantgrowth` · `mandrake.jawarules` · `mandrake.msedroidfix` · `mandrake.empirepursuit` · `mandrake.strandedquest` · `mandrake.ashkarrlandmarkart` · `mandrake.sauridfrillfix` · `mandrake.jawavoice` · `mandrake.gravshipastronautfix` · `mandrake.planetpresetprime` · `mandrake.toolbeltfix` · `mandrake.blastdoorframeasyncfix` · `mandrake.researchkiteastfix` · `mandrake.desertvehiclereskin` · `mandrake.jawa.doctrine` · `mandrake.starwarsraces` · `mandrake.jawa.armoury` · `mandrake.jawaikee` · `mandrake.jawaionweapons` · `mandrake.jawapawnflavor` · `mandrake.rimdefdump` | `mandrake.rm.inhabited` · `mandrake.rut.factionslate` · `mandrake.rut.plantgrowth` · `mandrake.rsw.jawarules` · `mandrake.rsw.msedroidfix` · `mandrake.rut.empirepursuit` · `mandrake.rm.strandedquest` · `mandrake.rut.ashkarrlandmarkart` · `mandrake.rm.sauridfrillfix` · `mandrake.rsw.jawavoice` · `mandrake.rm.gravshipastronautfix` · `mandrake.rm.planetpresetprime` · `mandrake.rm.toolbeltfix` · `mandrake.rsw.blastdoorframeasyncfix` · `mandrake.rm.researchkiteastfix` · `mandrake.rm.desertvehiclereskin` · `mandrake.rut.doctrine` · `mandrake.rsw.starwarsraces` · `mandrake.rsw.armoury` · `mandrake.rsw.jawaikee` · `mandrake.rsw.ionweapons` · `mandrake.rut.pawnflavor` · `mandrake.rm.rimdefdump` |

---

## 🔴 CURRENT MOD SET — empirepursuit fork swapped in, 2026-08-30

**`FULL.LATEST.xml` was stale against live** (`FOUNDRY`, found while prepping a
Droidworks quicktest — `which_is_live()` read UNRECOGNISED). The divergence was the
already-known `EMPIRE_PURSUIT_SURVEY_SHADOW_1` fork swap, done live on 2026-08-29 with
its own pre-swap backup already saved (`ModsConfig_2026-08-29_pre_empirepursuit_swap.xml`,
byte-identical to the stale `FULL.LATEST`) — never propagated to `LATEST` until now.
Re-captured from live (md5 `41cda74e`), 585 mods either way.

| out (1) | in (1) |
|---|---|
| `matathias.ruthlessmechanoids` | `mandrake.empirepursuit` |

## 🔴 CURRENT MOD SET — two aesthetic mods added, 2026-08-29

**The owner added two aesthetic mods via RimSort and re-sorted** (BENCH, at his
instruction). `ModsConfig.FULL.LATEST.xml` holds the result and is byte-identical
to the live `ModsConfig.xml` (md5 `3c40801c`). The predecessor is preserved at
`ModsConfig.FULL.20260826_070210.xml`.

| out (0) | in (2) |
|---|---|
| | `mlie.showmeyourhands` |
| | `meathax.showmeyourtools` |

The re-sort moved 407 relative positions but broke no ordering we depend on: every
`mandrake.*` mod still loads after its declared targets (`mandrake.msedroidfix`
before Droid Depot is deliberate — its own About.xml documents why loose-file art
needs no load order), and `mandrake.rimdefdump` is still dead last. The official
dump re-freeze against this list waits on the next full cold load
(`OFFICIAL_DUMP_REFREEZE_1`).

## 🔴 Superseded — the worldmap/terrain texture swap, 2026-08-20

**The owner changed the worldmap and terrain texture mods.** `ModsConfig.FULL.LATEST.xml`
holds the result and is **byte-identical to the live `ModsConfig.xml`** (md5 `5cb68571`,
both 00:52). The 578-mod predecessor is preserved at
`ModsConfig.FULL.20260819_201527.xml`.

⚠️ **This settled in two steps, and the first was recorded here as final — it was not.**
At 00:41 the swap read 578 → 576 with four mods out. At 00:49 `zal.worldmapenhanced`
was put back, and a RimSort re-sort at 00:49 changed the ORDER without changing the set
(`PRESWAP.resort_20260820.xml`, same 577 mods, different md5). **The net is three out,
two in.**

| out (4) | in (2) |
|---|---|
| `noxilie.regrow.wmb.advancedbiomes` | `grimterra.terrainretexturemod` |
| `noxilie.regrow.wmb.alphabiomes` | `grimterra.worldmap` |
| `noxilie.regrow.wmb.morevanillabiomes` | |

⇒ **578 → 577.** ~~`zal.worldmapenhanced`~~ was removed at 00:41 and **restored at
00:49** — it is IN. Any doc quoting 583, 578 or 576 is stale.

✅ **This cannot have orphaned a biome, and that was checked rather than assumed.** All
four departing mods define **zero `BiomeDef`s** — they are pure texture packs (127, 93,
63 and 231 PNGs respectively, no `Defs/` biome entries). So no biome defName left the
game, the hand-authored planet's tiles still resolve, and the three `world/*.rws` files
hold no reference that died with them.

⚠️ **What a texture swap CAN still do:** a loose PNG at the same texture path is resolved
by LOAD ORDER, not by intent, and a texture that loses to another texture **produces no
log line at all**. If the world map or terrain looks wrong after this, that is an
ordering question, not a missing-file question — see `skills/rimworld-start-prep/`.

⚠️ `ModsConfig.FULL.20260819_201527.xml` is **no longer a duplicate** of `FULL.LATEST`
(it was, until this change). `queue/BUILD.md` B-SWAP1 says otherwise; that half of the
item is now void — it is the only copy of the 578 list.
