# Jetty and bridge art: his seven picks, installed

Item: `RIMMANDRAKE_INSTALL_JETTY_BRIDGE_PICKS_HEAVY_B_CHOSEN_TWO_PICKS_OPEN`. Written 2026-11-22.

## His picks (2026-11-22) and where each one draws

| pick | ThingStyleDef that draws it | post sprite | cable |
|---|---|---|---|
| steel jetty B | `RM_SuspensionJetty_Steel_Industrial` | steel_jetty_B | galvanised |
| heavy jetty B | `RM_SuspensionJetty_Heavy_Industrial` | heavy_jetty_B | black steel |
| heavy bridge B | `RM_SuspensionDeck_Heavy_Industrial` | heavy_jetty_A (concrete pylons, as generated) | black steel |
| bridge Scrapper C | `RM_SuspensionDeck_Steel_Scrapper` | Scrapper_C | chain |
| bridge Industrial A | `RM_SuspensionDeck_Steel_Industrial` | Industrial_A | black steel |
| bridge Modern A | `RM_SuspensionDeck_Steel_Modern` | Modern_A | galvanised |
| bridge Futuristic A | `RM_SuspensionDeck_Steel_Futuristic` | Futuristic_A | cyan |

39 files went in through `art.py install` (28 deck pieces, 7 posts, 4 cables) under
`Textures/RimMandrake/FlowWorks/SuspensionBridge/<Look>/` and `.../Cables/`. Each equals the generated file by sha256
(`selftest_flowworks_deck_strips.py`).

## How the game draws them (`Source/Pits/Suspension/RM_DeckArt.cs`)

- Each picked style carries `RM_DeckArtExtension`: the piece, post and cable paths and the geometry numbers the option was
  generated on (`art_source/JettyBridgeRedesign/gen_render.py spec_for`). A style without it draws exactly as before.
- A deck square draws its ROOT, MID, TIP or SOLO piece by its place on the record, turned to the deck's direction.
- The anchor at each end (lane 0) prints the posts (upright, rising north), the backstays, and the cables: a jetty's from
  the post heads to its tip (and mid, for steel B); a bridge's sagging main cable and hangers, each end printing its own
  half. Cables print only when every deck square is built and down. Cables print at `PawnUnused`, posts at `BuildingOnTop`,
  shadows just under `Building`.
- `RM_SuspensionProofs.ProofDeckArt "x,z"` reads which piece each square draws. `ProofJetty` takes an optional look (5th
  field); `ProofLook` takes `;heavy` for the heavy bridge.

## Not changed, and why

- **The jetties' other three looks** (Scrapper, Modern, Futuristic) were not generated. Since
  RIMMANDRAKE_JOIN_JETTY_SQUARES_SEAMLESS_STILL_TWO_BLOCKS (his walk 2026-11-25: stations 78/79 "still look like two blocks
  stuck together") each draws its own look's picture re-cut into one seamless strip (`art_source/JettyBridgeRedesign/seam_strips.py`),
  with the post and cable of his picked steel bridge in that look; `selftest_flowworks_jetty_seams.py` checks every jetty
  look. **The default look is Scrapper**, so a heavy bridge built without picking a look still draws the old art.
- The anchor blocks keep their current pictures (the generated scenes used placeholders). The new posts stand on them.
- Drawbridges, raid planks and grated decks are not changed. A bridge with towers draws one main cable end to end.
- The four steel-bridge looks share one silhouette (polish line on `design/concepts/FlowWorks/version/polish.md`).

## Untested: the live look is UNRUN

ArchSmall was held by another run for the whole hour this run waited (17:51-18:51 PST). The command:

```
python3 src/RimMandrake/rimflow/game_lock.py claim ArchSmall --for "jetty/bridge picks live look"
eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"
python3 src/RimMandrake/Utils/game_instance.py stop --instance ArchSmall
python3 src/RimMandrake/Utils/modset_builder.py --tier flowworks --apply
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks --instance ArchSmall --apply
python3 src/RimMandrake/Utils/game_instance.py launch ArchSmall --wait   # then a quicktest map (rimworld/start_debug_game_ready)
python3 src/RimMandrake/FlowWorks/northstar/live_deck_art_picks.py       # captures + readings.json in Transient/deck_art_picks
```

Look for: seams between pieces; cables drawn over the walking colonist (the `PawnUnused` sort is [guess ~80%]); the faint
panel joint on box-girder decks longer than 2 squares; posts rising over the deck on north/south bridges.
The offline port of the draw code (`D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_INSTALL_JETTY_BRIDGE_PICKS_HEAVY_B_CHOSEN_TWO_PICKS_OPEN\before_after_offline.png`)
matches his pick images east/west; it is not a game capture.
