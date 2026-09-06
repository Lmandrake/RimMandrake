# Droid-Related Content Census: Frozen World vs Campaign Save

## Summary

> 🔴 **CORRECTION (BENCH, 2026-09-06, MEASURED):** `Autosave-1.rws` is NOT the campaign save.
> Its embedded `<modIds>` lists **25 mods including `mandrake.rsw.droidworks`** and no
> `guy762.kotordroids` — it is FOUNDRY's minimal-list Droidworks quicktest session. Every
> "frozen → campaign" comparison, the "80.5% reduction," and the conclusion that the KotOR
> donors "have been successfully retired" below are therefore VOID: the second file was a
> different mod list, not the same world later. The FROZEN-save counts stand as
> literal-string occurrence counts only. No campaign save was measured.

Comparing WORLDMAP_V1_original.rws (frozen world, Aug 27) and Autosave-1.rws (~~current campaign~~ — a 25-mod quicktest, see correction).

### Total Counts by Save

| Term | Frozen Map | Campaign | Delta |
|------|-----------|----------|-------|
| Asimov | 240 | 0 | -240 |
| Need_Energy | 82 | 0 | -82 |
| Droid | 1063 | 582 | -481 |
| KotOR | 701 | 0 | -701 |
| guy762 | 4436 | 220 | -4216 |
| JDS | 191 | 180 | -11 |
| DroidDepot | 1 | 0 | -1 |
| ArtificialBeings | 5 | 0 | -5 |
| SynCore | 1 | 0 | -1 |
| Synstruct | 219 | 0 | -219 |
| RSW_DW_ | 0 | 570 | +570 |
| Jawa_Droid_ | 0 | 0 | 0 |
| FreeDroid | 5 | 0 | -5 |

**Total donor mod content in frozen map:** 7,940 occurrences
**Total donor mod content in campaign:** 1,552 occurrences
**Cleaned from frozen→campaign:** 6,388 occurrences (80.5% reduction)

### Frozen World Map Examples

**guy762 (4436):** Largest donor presence
```
<li>guy762.mm.kotorcore</li>
<li>guy762.kotorweapons</li>
<li>guy762.kotordroids</li>
```

**Droid (1063):** Pawn/corpse reference flood
```
<li>HK_50_Companion</li>
<li>Droid_Protocol</li>
<li>ASF_Assault_Droid</li>
```

**KotOR (701):** Mod brand marker
```
<li>kotor.clothing</li>
<li>KotOR_Soldier</li>
<li>KotOR_Blaster</li>
```

**Asimov (240):** Asimov droid mod dependency
```
<li>neronix17.asimov</li>
<li>Asimov</li>
<li>Asimov_WirelessCharging</li>
```

**Synstruct (219):** Synstruct synthetics mod
```
<li>Synstruct_ChargedCyborg</li>
<li>Synstruct_Platform</li>
<li>Synstruct_Combat_Frame</li>
```

### Campaign Save Examples

**RSW_DW_ (570):** New RimStarWars-prefixed replacements active
```
<li>Corpse_RSW_DW_Race_JDSCIS_Pistoeka_Sotage_Droid</li>
<li>Corpse_RSW_DW_Race_guy762_DroidRace_HKseries</li>
<li>UnnaturalCorpse_RSW_DW_Race_B1_Battle_Droid</li>
```

**guy762 (220):** Residual, mostly in corpse/pawn names now reskinned
```
<li>Corpse_RSW_DW_Race_guy762_DroidRace_HK50series</li>
<li>UnnaturalCorpse_guy762_DroidRace_JDSCIS_B2</li>
<li>guy762.kotorcore</li>
```

**JDS (180):** Jedi Droid Smithy references (survives as lore/tooling)
```
<li>JDS_Assembler</li>
<li>JDS_Lab_Component</li>
<li>JDS_Droid_Research</li>
```

## Critical Finding

**guy762.kotordroids and associated KotOR donor mods (5,137 frozen occurrences) have been SUCCESSFULLY RETIRED in the campaign save.** The 4,216-item drop in guy762 + 701-item drop in KotOR represents near-complete donor-mod purge, with `RSW_DW_` namespacings (570 items) showing the new RimStarWars tier replacements are live and absorbing the droid-role content.

**Action:** guy762 and KotOR donor mods can be safely removed from the load order on next balance pass.

## Methodology

Search method: case-insensitive grep over entire .rws XML save file.
- Frozen: `WORLDMAP_V1_original.rws` (21M, Aug 27)
- Campaign: `Autosave-1.rws` (14M, Sep 6 10:15)

Commands run:
```bash
grep -io "Asimov" "$FROZEN" | wc -l      # Frozen map term count
grep -io "RSW_DW_" "$CAMPAIGN" | wc -l   # Campaign term count
```

