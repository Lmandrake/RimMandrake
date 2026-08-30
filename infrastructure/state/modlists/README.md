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
