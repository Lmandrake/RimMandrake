## spec
Filed by BUILD 2026-08-23: *"Five pirate factions need names, or the Blackstar needs a different
naming route."*

⭐ **BUILD ALREADY SOLVED THE ROUTE, and it is the right solution.** Read from their
`Namer_BlackstarCompany.xml`: `Pirate` is *also* `PirateBandBase` — vanilla gives it a `Name=`
attribute as well as a defName, so it is simultaneously a concrete faction and the abstract
parent of every other pirate. A single `fixedName` on it was therefore inherited by **six**
factions. They ruled out blanking (`<fixedName></fixedName>` resolves to the EMPTY string, and
`FactionGenerator.cs:149` tests `!= null`, not `NullOrEmpty` — five factions called *nothing*)
and `Inherit="False"` (clears child elements, cannot un-inherit a scalar), and moved the name to
a one-rule `factionNameMaker`, which **is** overridable per child.

⇒ **The route needs no decision. What is left is the half only DECIDE can answer: do the other
five get AUTHORED names, or is a generated one good enough?**

## 🔴 DECIDE'S RULING — author all five. A vanilla pirate name breaks the setting.

**After BUILD's fix the five fall back to generated namers**, and what those generate is
`NamerFactionPirate`-flavoured — *"The Iron Fist Gang"*, *"Sky Reavers"* — generic sci-fi that
belongs to no galaxy in particular. 🔑 **That is the same defect as an Earth crop name**, which
this project spent 2026-08-23 removing: it is not wrong, it is *not this world*. And
`XENOTYPE_ROSTER_PURE_SW_1` points the same way — non-canon is cut, not tolerated.

⭐ **And the five are not interchangeable, which is what makes authoring them worth doing.**
Each is a mechanically distinct raider flavour already shipped and already working. Naming them
individually **uses content we already have** instead of flattening six identities into one.

| FactionDef | its mechanical flavour | name | why |
|---|---|---|---|
| `Pirate` | Core baseline — **the only one placed**: 4 settlements + an authored cast roster | **Blackstar Company** | ⛔ **unchanged.** It is established, sited and cast |
| `PirateWaster` | Biotech — pollution-adapted wasters | **Nova Blades** | canon pirate gang; "nova" reads irradiated |
| `PirateYttakin` | Biotech — hairy, cold-adapted brutes | **the Ohnaka Gang** | canon Weequay pirates: rough, boisterous, exactly this |
| `CannibalPirate` | Ideology — cannibal ideoligion | **Crimson Dawn** | canon syndicate, blood-coded and sinister |
| `AG_XenohumanPirates` | Alpha Genes — gene-modified xenohumans | **Black Sun** | canon elite syndicate; its cosmopolitan reach fits xenohuman |
| `DV_PirateKeshig` | Det's Keshig xenotype | **Kanjiklub** | canon hard warrior gang; matches the Keshig register |

All five are canon Star Wars criminal organisations, so this is the same **canon-for-what-the-
player-reads** register ruled for the plant renames earlier today.

⚠️ **Scope, honestly: only `Pirate` has settlements**, so these five surface in raid letters, the
faction tab and comms — not on the world map. Worth doing anyway; a raid letter is read far more
often than a map label.

## verify
Six pirate factions, six different names, none of them empty. 🔴 **The empty-string failure is
the one to check for** — `FactionGenerator.cs:149` tests `!= null`, so a blanked name yields a
faction called `""` and looks like a UI bug rather than a def bug.

## criteria
- [ ] Each of the five carries its own one-rule namer, per BUILD's pattern.
- [ ] `Pirate` still reads **Blackstar Company**.
- [ ] No faction generates an empty name.

## Watch out
⛔ **Do not put any of these on `fixedName`.** That is the exact bug this closes — `Pirate` is
`PirateBandBase` and anything on it is inherited by all six.
⚠️ **`DV_PirateKeshig` and the two Biotech kinds already override `factionNameMaker`** with
their own namers; those overrides are the hook to replace, not to add beside.
