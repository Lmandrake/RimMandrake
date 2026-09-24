# OASIS_MAKER_MACHINES_1 — ancient machines that grow oases, slowly

RULED by the owner, typed 2026-09-24, redirecting the shine portfolio's
"Machines That Weep" (`weeping_stones_shine_options_2026-09-24.md` ⚖️ head,
verdict 3, verbatim there): *"machines that create oases slowly when placed
near shaded terrain near rocks. Placement is key. We should guide it with
green red area selections. Like placing water based generators. I know there
was a mod that used to grow terraforming slowly so we could base it on that.
Makes obtaining the ancient machines a treasure type. Unfortunately it's not
very important for the Jawa utinni scenario but it's a nice mod component. We
would need to weave it into some quests to obtain or sabotage them."*

## scope

- **A treasure-class ancient machine** (building) that, once placed, grows an
  oasis around itself SLOWLY — terrain conversion over long time, not a pump.
- **Placement is the game**: valid near shaded terrain near rocks; guided by
  green/red cell overlay at placement, like water-based generator placement
  (vanilla `PlaceWorker_WatermillGenerator` shape; our
  `RM_MapComponent_ShadeGrid` already computes shade).
- **Slow-terraform base to study: Terramorph** — a `TerramorphArtOverride`
  mod already ships in the live Mods folder, so the donor is in-list; verify
  its actual mechanism before building (study the pattern, port nothing
  verbatim without a license check).
- **Acquisition is treasure**: not craftable; found/quested. Owner: weave
  into quests to obtain or sabotage them — quest hooks are owed but ride the
  quest family passes, not this item's v1.
- Tier: RimMandrake mod component (owner: *"not very important for the Jawa
  utinni scenario but it's a nice mod component"*) — build for the
  `RM_WeepingStones` kit with the cross-biome Mod Settings gate like every
  biome mechanic.

## bounds

- ⛔ No worldgen, no planet repaint — map-scale terrain conversion only.
- R21: the oasis it grows is condensate-fed fiction; zero any rain terms.
- The dead option 2 ("Born and Dying Water", owner: *"nah too much"*) stays
  dead — this machine GROWS an oasis; no oasis-death/overdraw simulation
  rides in with it.

## next

Fable design draft (backgrounded from BENCH): machine states, growth rings
and rates, placement validity rules + overlay, treasure sourcing table, quest
hook stubs, Terramorph mechanism study. Then BENCH cards opens; then FOUNDRY
build item.
