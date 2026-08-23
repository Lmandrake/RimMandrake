## spec
`src/Jawa/Jawa_Patches/Patches/AncientArsenal_Ashkarr.xml` operation 1 was rewritten by DECIDE at `347b841e`.
It no longer tries to `PatchOperationRemove` the `Gun` tag from `MA_CapryakScatterbow` — that operation
matched nothing and said nothing for as long as it existed. It now sets `Inherit="False"` on the def's
`weaponTags` node, which severs the append from Core's abstract `BaseHumanMakeableGun`.

**The change is committed and validated offline** (`validate_patch.py`: 0 errors; the 3 warnings are the
file's intentional add-if-missing patterns). ⛔ **It is not deployed** — that is yours, and DECIDE does not
run `--apply`.

## verify
1. `deploy_custom_mods.py --mod Jawa_Patches` then `--apply`.
2. After the next load, a capture whose `modCount` matches `ModsConfig.xml`, then:
   `MA_CapryakScatterbow` must carry `NeolithicRangedAdvanced` and **must not carry `Gun`**.

```
select t.tag from def_tags t join defs d on d.id=t.def_id
where d.def_name='MA_CapryakScatterbow' and d.def_type='ThingDef' and t.kind='weaponTags'
```

## criteria
- [ ] `Gun` absent from the scatterbow's resolved `weaponTags`.
- [ ] `NeolithicRangedAdvanced` still present — neolithic kinds must not lose the weapon.
- [ ] No new red error naming `AncientArsenal_Ashkarr` or `MA_CapryakScatterbow`.

## Watch out
🔴 **The previous version of this operation PASSED every offline check and did nothing.** `validate_patch.py`
without `--defs` cannot see that an xpath matches no node, and `PatchOperationConditional` returns true on no
match, so the log was clean too. ⛔ **Do not accept "it validated" as proof here** — only a capture taken
after the deploy settles it.

⚠️ **`Inherit="False"` severs the WHOLE parent list, not just `Gun`.** That is intended: the parent's list
holds `Gun` and nothing else. If a future Core or mod update adds a second item to `BaseHumanMakeableGun`'s
`weaponTags`, the scatterbow silently stops receiving that too. Cheap to re-read; worth knowing.

⚠️ **`VEE_HunterNeolithicWeapon` reaches this node from another mod's patch, not from the def.** `AttributeSet`
was chosen over replacing the node precisely so that tag survives regardless of load order — if the capture
comes back missing it, the operation was changed to a Replace and that is the regression, not the sever.

🔑 **The budget half of the parent item needs nothing.** `AncientSoldier` 1200~2600 and `AncientSoldier_Leader`
2500~6000 are already live and already correct; do not re-raise them while you are in this file.
