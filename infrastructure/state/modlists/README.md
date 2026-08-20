# Mod-list swap — CHECK owns this

The live list is
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`.

🔴 **`ModsConfig.FULL.LATEST.xml` is the owner's real 583-mod list. Restore it before he
plays. Nothing here is authoritative about the game until it is copied back.**

Captured 2026-08-19 20:15, 583 active, md5 `5a9a4d3a958ad96dad442bedfc926f5c`.
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

## 🔴 CURRENT MOD SET — 576 active, captured 2026-08-20 00:41

**The owner changed the worldmap and terrain texture mods.** `ModsConfig.FULL.LATEST.xml`
holds it and is **byte-for-byte identical to the live `ModsConfig.xml`**, verified
2026-08-20. The previous 578-mod list is preserved at
`ModsConfig.FULL.20260819_201527.xml`.

| out (4) | in (2) |
|---|---|
| `noxilie.regrow.wmb.advancedbiomes` | `grimterra.terrainretexturemod` |
| `noxilie.regrow.wmb.alphabiomes` | `grimterra.worldmap` |
| `noxilie.regrow.wmb.morevanillabiomes` | |
| `zal.worldmapenhanced` | |

⇒ **578 → 576.** Any doc still saying 578 is stale.

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
