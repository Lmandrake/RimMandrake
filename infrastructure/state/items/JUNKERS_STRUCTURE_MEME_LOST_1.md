## spec
The Junkers' runtime ideo `the Weight` carries **9 memes where `JawaJunkers.xml`
forces 4**. The five extras are byte-identical to Blackstar Company's entire
authored `forcedMemes` list (`Patches/BlackstarCompany.xml:118-124`):
`Structure_Ideological`, `Guilty`, `Individualist`, `VME_Bushido`, `VME_Anonymity`.

⇒ The ideo holds **two structure memes**, and the effective one is
`Structure_Ideological`, **not** the authored `AM_Structure_Scavenger`.
`jawa/ideo_of` reports `structureMeme: Structure_Ideological`. The scavenger
structure the faith was designed around is not the one the game uses.

Reproduced identically on two dev-quicktest worlds, 578 mods.
Evidence: `infrastructure/state/observed/2026-08-21/B54_faction_faiths/`.

## the mechanism — DIAGNOSED, and this item first said it was not
🔴 **My own first filing said "`Jawa_Junkers` is `ParentName="PirateBandBase"` and the
Blackstar patch targets `FactionDef[defName="Pirate"]`, which are siblings, so plain
def inheritance does not explain it." That reasoning was wrong and the correction is
the whole point of this item.**

`Core/Defs/FactionDefs/Factions_Misc.xml:510` reads:

    <FactionDef Name="PirateBandBase" ParentName="FactionBase">
      <defName>Pirate</defName>

**`Pirate` IS `PirateBandBase`.** One def is both the concrete vanilla pirate faction
and the abstract root every other pirate def inherits from. So
`BlackstarCompany.xml`'s `PatchOperationAdd` at `/Defs/FactionDef[defName="Pirate"]`
does not patch one faction — **it patches the parent of every pirate faction in the
game**, ours included.

🔑 **And that is why the damage is shaped the way it is.** RimWorld's def inheritance
**overrides a scalar and APPENDS a list**:

| field | kind | result on `Jawa_Junkers` |
|---|---|---|
| `fixedName` | scalar | the Junkers' own wins — the faction is still named "the Junkers" |
| `forcedMemes` | list | **appended** — Blackstar's 5 land on top of the Junkers' 4 |

⇒ The name looks right, which is exactly why nobody caught the memes.

## blast radius — measured off the 2026-08-21 dump, not inferred
**Six FactionDefs now carry `fixedName: Blackstar Company`:** `Pirate`,
`CannibalPirate`, `PirateYttakin`, `PirateWaster`, `DV_PirateKeshig`,
`AG_XenohumanPirates`. Four of them generated in the quicktest world and all four
appear on the planet under that one name.

**Seven FactionDefs carry all five Blackstar memes:** the six above plus
`Jawa_Junkers`. `DV_PirateKeshig` shows the same append signature — 8 memes, its own
`ideoName: Truth of Power`, Blackstar's five underneath.

## criteria
`jawa/ideo_of` on a freshly generated world reports `the Weight` with
`structureMeme: AM_Structure_Scavenger` and **4** memes, and no faction other than the
intended one wears `fixedName: Blackstar Company`.

🔴 **This bakes.** An Ideo is generated once at world creation and cannot be
retrofitted, so it must be settled before the owner's worldgen click.
