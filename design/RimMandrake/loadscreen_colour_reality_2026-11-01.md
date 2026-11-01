# Ash'karr loadscreen: world-map colour to orbital reality

Item `PLANETARY_LOADSCREEN_RENDERS_2`, spec step 2. Every biome on `world/ASHKARR_WORLDMAP_tiles.csv` (the record, not the
live planet), the colour its face wears in the seeds (`biome_worldfaces.py`, base colour), and what the ground would look
like from orbit, written from the palette of its frozen sheet. `src/RimMandrake/Utils/art/loadscreen_candidates.py` reads
this table into the prompt and refuses a missing biome. Names are the record's; `world_beauty_render.py` maps them to faces.

Planet facts carried by the prompt: tidally locked (substellar point at 0,0; terminator 90 degrees of arc from it); one
sun, never a binary pair; a desert world, not Mars: pale ochre sand and salt rather than a rust-red disc, with an equatorial
war-debris ring at 1.4 to 2.0 planet radii (`deployed/config/Mod_3272330410_AtmosphereMod.TRUE-GLORIOUS-RING.xml`). The sun
lies in the ring plane, so the ring throws no broad shadow band across the disc.

| record biome | face | seed colour | seen from orbit | frozen sheet |
|---|---|---|---|---|
| RUT_ExtremeDesert | Stillsand | pale tan | pale gold and bone dune sheets, machined-regular ripple, glass glints, utterly dry | deep_desert.md |
| RUT_Desert | LongShade | warm tan | amber and ochre sand with rust outcrops and long cool blue shadows near the terminator | desert.md |
| RUT_AridShrubland | LeaningScrub | olive tan | root-bound dun crust with a dusty grey-olive scrub fuzz | arid_shrubland.md |
| RUT_Wasteland | Wasteland | putty grey | salt white and ash-grey flats with vitrified black-green scars | wastes.md |
| RUT_CrackedLands | CrackedLands | brick red | grey-white cracked clay pans with red-brown flood stain | the_cracked_lands.md |
| RUT_RustCathedral | RustCathedral | deep rust with dark grid | rust film over a dark buried metal lattice, a vast derelict machine plain with verdigris streaks | the_rust_cathedral.md |
| RUT_Scarlands | Warscar | dark mauve-brown | black glassed war scars with rust and acid-bright pools | the_scarlands.md |
| RUT_TheForge | Forge | charcoal | basalt black and obsidian with thin glowing red lava seams under ash grey | the_forge.md |
| RUT_TheScald | Scald | turquoise | a perfectly round crater ocean, scald cyan water with boiling white steam and a dark basalt rim | the_scald.md |
| RUT_Greentide | Greentide | saturated green | dense wet jungle of every green with white steam and black mud | the_greentide.md |
| ZBiome_Grasslands | Pyrelands | khaki | grass-gold plains crossed by migrating ash-black burn bands and week-old green regrowth | the_pyrelands.md |
| RUT_WeepingStones | WeepingStones | bone white | bone-white sunlit stone with wet black streaks and green held in shade | weeping_stones.md |
| RUT_Contagion | Contagion | dusty rose | red water and red fog over grey-white husk ground | the_contagion.md |
| RUT_Webwork | Webwork | dark green | every dark green veiled in dead white silk | the_webwork.md |
| RUT_Miasma | Miasma | muddy olive | muck-brown and mangrove green swamp with salt crust on its sea edge | the_miasma.md |
| RUT_FeverWood | FeverWood | moss green | a raised table of living-wood brown and moss green forest | the_fever_wood.md |
| RUT_TwilightSea | TwilightSea | deep navy | a torn, elongated dark sea, deep green and kelp-bronze water, near the terminator | the_twilight_deep.md |
| RUT_GreySea | GreySea | slate blue | a torn, elongated grey sea, salt-encrusted and shrinking, bone-pale shoals, near the terminator | the_grey_deep.md |
| RUT_PoisonForest | Cauldron | slate olive | wet black and slate ground with bone-pale forest, a dark margin against the ochre | cauldron.md |
| RUT_Sump | Sump | near black | every black, wet and glassy, with amber horizon glints | the_sump.md |
| RUT_BlueDesert | BlueDesert | slate blue-grey | pale blue-white water-ice sand and blue ice fields in dim twilight | the_blue_desert.md |
| RUT_TheRot | TheRot | violet | wet dark ground under bone white, lilac and milk-white growth with faint glow-blue and lantern gold | the_rot.md |
| RUT_NightsideIce | SleepingIce | pale grey | dirty white ice sheet over blue-black rock at the fractures, faint aurora | sleeping_ice.md |
| RUT_Umbra | Umbra | dark slate | dark frozen nightside under perpetual green and violet aurora | the_propane_lakes.md |
| RUT_ForsakenCrags | Abyss | black | obsidian-black crags with rime-frost grey and tiny glow-blue points | abyss.md |
| RUT_Slime | Slime | yellow-green | translucent green and amber living film over dark ground | the_slime.md |
| RUT_PropaneLake | Chill | night blue | black mirror lakes of liquid fuel, frost white at the edges, aurora reflected | the_propane_lakes.md |
