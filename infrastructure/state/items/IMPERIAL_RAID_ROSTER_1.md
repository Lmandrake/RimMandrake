## spec
`src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml:31-110` authors four
Imperial pawn kinds. `grep -rn "Jawa_Empire_" src/ | grep -v JawaFactionRoster` returns
**empty** — nothing spawns them. `defaultFactionDef` does not create a spawn route; only a
`pawnGroupMaker` does. Separately, `grep -rn "fixedLeaderKinds" src/` returns **empty**, so
the Galactic Empire's leader still generates as Royalty's `Empire_Royal_Stellarch`.

Edit `src/Jawa/Jawa_Patches/Patches/GalacticEmpire.xml` only. Three changes.

**1. Replace the COMMON combat group's options.** Same xpath already in the file:
`/Defs/FactionDef[defName="Empire"]/pawnGroupMakers/li[kindDef="Combat"][commonality="100"]/options`

```xml
<options>
  <Jawa_Empire_Grunt>5</Jawa_Empire_Grunt>
  <Jawa_Empire_Heavy>2</Jawa_Empire_Heavy>
  <Jawa_Empire_Specialist>1.5</Jawa_Empire_Specialist>
</options>
```

**2. Replace the RARE combat group's options** (`[commonality="10"]`) — ours plus the three
Outer Rim specialists, which stay because they are the flavour the authored four do not
carry:

```xml
<options>
  <Jawa_Empire_Grunt>5</Jawa_Empire_Grunt>
  <Jawa_Empire_Heavy>2</Jawa_Empire_Heavy>
  <Jawa_Empire_Specialist>1.5</Jawa_Empire_Specialist>
  <OuterRim_ImpRangeTrooper MayRequire="Neronix17.OuterRim.GalacticEmpire">2</OuterRim_ImpRangeTrooper>
  <OuterRim_ImpDeathTrooper MayRequire="Neronix17.OuterRim.GalacticEmpire">1.5</OuterRim_ImpDeathTrooper>
  <OuterRim_ImpISBAgent MayRequire="Neronix17.OuterRim.GalacticEmpire">1</OuterRim_ImpISBAgent>
</options>
```

**3. Add `fixedLeaderKinds`** — it is PRESENT on the vessel
(`Data/Royalty/Defs/FactionDefs/Faction_Empire.xml:100`, `<li>Empire_Royal_Stellarch</li>`),
so this is a **Replace**, not an Add:

```xml
<li Class="PatchOperationReplace">
  <xpath>/Defs/FactionDef[defName="Empire"]/fixedLeaderKinds</xpath>
  <value><fixedLeaderKinds><li>Jawa_Empire_Leader</li></fixedLeaderKinds></value>
</li>
```

⚠️ **Ops 1 and 2 must stay inside the existing `PatchOperationFindMod` for
"Outer Rim - Galactic Empire".** Our own kinds carry
`apparelRequired` on `OuterRim_StormtrooperCuirass`/`Helmet`, so without that mod the whole
group is wrong anyway. **Op 3 goes OUTSIDE it** — `Jawa_Empire_Leader` is ours and needs no
gate.

⛔ **Do NOT touch the Trader or Settlement groups.** They keep Royalty's villagers,
janissaries and cataphracts by design — `FACTION_SPEC.md:130` and
`EMPIRE_GAP_AUDIT.md` §3.

✅ **While the file is open**, `src/Jawa/Jawa_Patches/About/About.xml:32` still describes
`permanentEnemy` as **true**; the shipped patch sets it **false**. One-line prose fix.

## verify
- `python3 skills/rimworld-modding/scripts/validate_patch.py src/Jawa/Jawa_Patches/Patches/GalacticEmpire.xml --defs ...` clean
- `grep -rn "Jawa_Empire_" src/ | grep -v JawaFactionRoster` is **no longer empty** and
  names all four kinds
- `grep -rn "fixedLeaderKinds" src/` returns exactly one hit, in `GalacticEmpire.xml`
- 🔴 **the tag check, which is the one that fails silently:** every `weaponTags` entry on
  the four kinds — `ORImperialStandard`, `ORImperialLight`, `ORImperialHeavy`,
  `ORHeavyWeapon`, `ORPistol`, `ORImperialSniper` — must resolve to at least one surviving
  weapon after cherrypicking. A tag at zero spawns the pawn **bare-handed** and logs
  nothing.

## criteria
An Imperial raid fields stormtroopers, heavy troopers and officers — **armed** — and the
Empire's leader reads *Emperor Palpatine*, not a high stellarch.
