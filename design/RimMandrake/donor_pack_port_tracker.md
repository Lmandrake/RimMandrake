# Donor pack port tracker: mlie.starwarsanimalcollection (160 species)

Item `DONOR_DEFS_PORT_TO_OURS_1`; plan `design/RimMandrake/donor_pack_port_plan_2026-10-14.md`. Script: `src/RimMandrake/Utils/donor_pack_port.py` (`diff` = W0, `rosters`, `repoint` = W1). One row per donor race. `class` is the 2026-10-14 census class; `W0` is the twin-vs-donor diff (MATCH / DIFF with the differences / NO_TWIN); `rows` is donor-named roster rows still left; `status` is this pass's outcome; `sha` the commit that did it.

Art (Part B, 2026-10-14; adult texPaths, live sha vs the art ledger): RENDERED_ON_SHEET (new render passed canon, awaiting his pick on the review sheet) · OURS (adult picture is not donor bytes) · OWNER_KEPT (an owner keep, trust=ruled, on the live donor picture) · EXISTING_RENDER (regenerated renders/jobs already exist: never re-queued) · KEEP_DONOR_ART_FOR_NOW (graded against the canon entry's Must show and passes) · COMMISSIONED (artpipe job filed) · COMMISSIONED_BY_SECOND_WORKER.

Statuses: DONE_ALREADY_OWNED (twin existed; only roster rows repointed, art and defs untouched) · PORTED (new RSW_ def this pass) · ART_BLOCKED · OWNER_QUESTION · DECLINED · OWED (not reached).

| species | class | twin | W0 | canon entry | rows left | status | sha | note | art | art note |
|---|---|---|---|---|---:|---|---|---|---|---|
| Acklay | TWIN_NOT_WIRED | RSW_Acklay | MATCH; namer | acklay | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | EXISTING_RENDER | regenerated art already exists, not re-queued: canon_acklay_v1, canonregen_rsw_acklay_v1 |
| Aiwha | DROPPED_BY_OWNER_2026-10-15 ("Retire the Aiwha in our mods. Too much trouble.") | RSW_Aiwha (removed) | NO_TWIN | aiwha (new) | 0 | PORTED | cb1d215241e1 (W3c) | donor art extracted; unrostered (placement belongs to the biome sittings); canon says it flies: real flight owed (MaxFlightTime + flip-book; never live-test without the owner) | ART_ON_SHEET | v1-v4 whole-animal renders all FAIL canon 3/4 on "span many times the body length" (1.2-3 body lengths, grader wants 5). Owner card 2026-10-14 "Redraw with a wing-first prompt": wings and body generated apart (aiwha_wingfirst_wings_v1, _body_v1, _body_ns_v1, _body_s_v2; 5 generations, none failed), joined by `src/RimMandrake/Utils/aiwha_composite.py` at 5.5 body lengths on 768x384 → aiwha_wingfirst_composite_v1 east/south/north each canon PASS 4/4 (record `design/RimMandrake/aiwha_wingfirst_2026-10-14_composite.json`). On sheet aiwha_wingfirst_sheet_2026-10-15; nothing installed; drawSize (8,4) still held as `donor_pack_aiwha_wide_drawsize_2026-10-14.patch`, apply with the install |
| Akk | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Akk | NO_TWIN | akk (new; canon page "Akk dog") | 0 | PORTED | 39478dcd403f (W3d) | donor art extracted; unrostered (placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | agrees on every Must-show line |
| Anooba | TWIN_NOT_WIRED | RSW_Anooba | MATCH; namer | anooba | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Bantha | WIRED_DONOR_ROW | RSW_Bantha | MATCH; namer | bantha | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Behemoth | NOT_PORTED/SHARED_BODY | RSW_Behemoth | NO_TWIN | behemoth (new; canon page "Sith war behemoth") | 0 | PORTED | cb1d215241e1 (W3c) | donor art extracted; unrostered (placement belongs to the biome sittings); ships our JawaBehemoth up-res (BehemothArtUpres patch baked), which lives in StarWarsPatches, not SWBestiary | OURS | adult art is ours in the art ledger |
| Beldon | TWIN_NOT_WIRED | RSW_Beldon | MATCH; namer | beldon | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| Blarth | TWIN_NOT_WIRED | RSW_Blarth | MATCH; namer | blarth | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| Blixus | TWIN_NOT_WIRED | RSW_Blixus | MATCH; namer | blixus | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| Blurrg | TWIN_NOT_WIRED | RSW_Blurrg | DIFF: stat CaravanRidingSpeedFactor: donor None ours 1.5; stat MeatAmount: donor None ours 350; namer | blurrg | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is ours in the art ledger |
| Boarwolf | NOT_PORTED/PLAIN | RSW_Boarwolf | NO_TWIN | boarwolf (new) | 0 | PORTED | 695812d5ec72 (W2b) | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings); canon is a 3 m predator; the donor def/sprite is a farm-boar: reported in the entry | REDRAWS_ON_SHEET2 | adult installed (owner pick, b104142ef); juvenile Boarwolf_j redrawn as enact_redo_boarwolf_j_v2 (512, adult as anchor; v1 failed canon on fangs) canon PASS, graded PASS; on donor_pack_redraws_sheet_2026-10-14 |
| Bogwing | TWIN_NOT_WIRED | RSW_Bogwing | MATCH; namer | bogwing | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| Bolotaur | PORTED_WIRED | RSW_Bolotaur | MATCH; namer | bolotaur | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| Boma | TWIN_NOT_WIRED | RSW_Boma | MATCH; namer | boma | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Borcatu | TWIN_NOT_WIRED | RSW_Borcatu | MATCH; donor-only refs: Borcatu; namer | borcatu | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Bordok | NOT_PORTED/PLAIN | RSW_Bordok | NO_TWIN | bordok (new) | 0 | PORTED | 695812d5ec72 (W2b) | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | horns, mane, olive body agree |
| Brezak | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Brezak | NO_TWIN | brezak (new) | 0 | PORTED | 39478dcd403f (W3d) | donor art extracted; unrostered (placement belongs to the biome sittings); a glider in canon | KEEP_DONOR_ART_FOR_NOW | flaps, colour agree |
| Bursa | NOT_PORTED/PLAIN | RSW_Bursa | NO_TWIN | bursa (new) | 0 | PORTED | 695812d5ec72 (W2b) | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings); canon entry is Legends-only | KEEP_DONOR_ART_FOR_NOW | shape, crest, brown spotted coat agree; green crest tint minor |
| CanCell | TWIN_NOT_WIRED | RSW_CanCell | MATCH; namer | cancell | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | EXISTING_RENDER | regenerated art already exists, not re-queued: canon_cancell_v1, canonregen_rsw_cancell_v1, canonregen_rsw_cancell_v2 |
| Cannok | TWIN_NOT_WIRED | RSW_Cannok | MATCH; namer | cannok | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| ChrysalideRancor | NOT_PORTED/SHARED_BODY_ITEMS | RSW_ChrysalideRancor | NO_TWIN | chrysaliderancor (new) | 0 | PORTED | ec18766ffd09 (W3a) | donor art extracted; unrostered (placement belongs to the biome sittings); canon is the Legends page "Chrysalide" (green skin); the greyscale donor sprites are tinted green in game (CutoutComplex def colours) | KEEP_DONOR_ART_FOR_NOW | tint mask: def tints it green (CutoutComplex colours), bony growths drawn; the earlier 'white/grey' report was the raw PNG |
| Clodhopper | WIRED_DONOR_ROW | RSW_Clodhopper | MATCH; namer | clodhopper | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | EXISTING_RENDER | regenerated art already exists, not re-queued: desertportb_clodhopper, longshade_rsw_clodhopper_v1 |
| Convor | TWIN_NOT_WIRED | RSW_Convor | MATCH; namer | convor | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| CorellianHound | NOT_PORTED/PLAIN | RSW_CorellianHound | NO_TWIN | corellianhound (new) | 0 | PORTED | 695812d5ec72 (W2b) | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings); BodyDef RSW_CorellianHound already existed (Grank port); reused | KEEP_DONOR_ART_FOR_NOW | hairless pale hound, crest, underbite agree |
| Corinathoth | TWIN_NOT_WIRED | RSW_Corinathoth | MATCH; namer | corinathoth | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Dactillion | TWIN_NOT_WIRED | RSW_Dactillion | MATCH; namer | dactillion | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Dalgo | TWIN_NOT_WIRED | RSW_Dalgo | MATCH; donor-only refs: SW_Spur; namer | dalgo | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Devourers | NOT_PORTED/SHARED_BODY | RSW_Devourers | NO_TWIN | devourer (new) | 0 | PORTED | cb1d215241e1 (W3c) | donor art extracted; unrostered (placement belongs to the biome sittings); vanilla Anomaly has an unrelated PawnGroupKindDef "Devourers" | RENDERED_ON_SHEET | donorport_devourer_v1 3/3 PASS; graded PASS; on donor_pack_port_sheet_2026-10-14 |
| Dewback | TWIN_NOT_WIRED | RSW_Dewback | MATCH; namer | dewback | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Dianoga | TWIN_NOT_WIRED | RSW_Dianoga | MATCH; namer | dianoga | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | EXISTING_RENDER | regenerated art already exists, not re-queued: canon_dianoga_v1, canonregen_rsw_dianoga_v1 |
| Dragonsnake | TWIN_NOT_WIRED | RSW_Dragonsnake | MATCH; donor-only refs: Dragonsnake; namer | dragonsnake | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Drexl | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Drexl | NO_TWIN | drexl (new) | 0 | PORTED | 39478dcd403f (W3d) | donor art extracted; unrostered (placement belongs to the biome sittings); canon says winged flier: real flight owed (MaxFlightTime + flip-book; never live-test without the owner) | KEEP_DONOR_ART_FOR_NOW | wings ARE drawn (east/south); grey-violet horned reptile agrees |
| EnergySpider | NOT_PORTED/SHARED_BODY_ITEMS | RSW_EnergySpider | NO_TWIN | energyspider (new; page "Spice spider/Legends") | 0 | PORTED | 39478dcd403f (W3d) | donor art extracted; unrostered (placement belongs to the biome sittings); carries the donor Glitterstim drug chain, ported as RSW_ (ThingDef, ChemicalDef, NeedDef, hediffs, thought, effecter); the donor recipes are not reachable from the race and were not ported | KEEP_DONOR_ART_FOR_NOW | agrees |
| Eopie | WIRED_DONOR_ROW | RSW_Eopie | MATCH; donor-only refs: Cameloid_Meat, SW_Spit; namer | eopie | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Falumpaset | WIRED_DONOR_ROW | RSW_Falumpaset | MATCH; donor-only refs: Cameloid_Meat, SW_Spur; namer | falumpaset | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | EXISTING_RENDER | regenerated art already exists, not re-queued: desertportb_falumpaset, regen_ls_canon_falumpaset_v1, regen_ls_canon_falumpaset_v1_ns |
| Fambaa | TWIN_NOT_WIRED | RSW_Fambaa | MATCH; namer | fambaa | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Fanback | TWIN_NOT_WIRED | RSW_Fanback | MATCH; namer | fanback | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| FeralGrazer | PORTED_WIRED | RSW_FeralGrazer | MATCH; donor-only refs: Grazer; namer | grazer | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| FeralNerf | TWIN_NOT_WIRED | RSW_FeralNerf | MATCH; donor-only refs: Grazer, SW_Spit; namer | NONE | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| FrilledGorg | WIRED_DONOR_ROW | RSW_FrilledGorg | MATCH; namer | NONE | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| FrogDog | NOT_PORTED/SHARED_BODY | RSW_FrogDog | NO_TWIN | frogdog (new) | 0 | PORTED | cb1d215241e1 (W3c) | donor art extracted; unrostered (placement belongs to the biome sittings); canon frog-dogs are SENTIENT; ported as an animal, reported in the entry | KEEP_DONOR_ART_FOR_NOW | agrees on shape and teeth |
| Gelagrub | TWIN_NOT_WIRED | RSW_Gelagrub | MATCH; namer | gelagrub | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Gizka | PORTED_WIRED | RSW_Gizka | MATCH; namer | gizka | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is ours in the art ledger |
| Gorg | WIRED_DONOR_ROW | RSW_Gorg | DIFF: baseBodySize: donor 0.3 ours 0.21; namer | gorg | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Gornt | TWIN_NOT_WIRED | RSW_Gornt | MATCH; namer | gornt | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| GraniteSlug | WIRED_DONOR_ROW | RSW_GraniteSlug | MATCH; namer | graniteslug | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Grank | TWIN_NOT_WIRED | RSW_Grank | MATCH; donor-only refs: Grank; namer | grank | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Grazer | NOT_PORTED/PLAIN_DEPS | RSW_Grazer | NO_TWIN | grazer | 0 | PORTED | dd2dea5ffead (W2c) | donor art extracted; unrostered (placement belongs to the biome sittings); canon entry is the existing grazer/ entry (written for RSW_FeralGrazer; not edited) | KEEP_DONOR_ART_FOR_NOW | own canon entry written 2026-10-14: canon_references/grazerdomestic/ (Legends, one image); the donor blob lacks the gold rosette patches, legs and ears: a commission against that entry is owed if he wants one |
| GreaterKraytDragon | PORTED_WIRED | RSW_GreaterKraytDragon | MATCH; donor-only refs: KellDragon; namer | greaterkraytdragon | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| Gualaar | NOT_PORTED/PLAIN | RSW_Gualaar | NO_TWIN | gualaar (new) | 0 | PORTED | 695812d5ec72 (W2b) | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings); owner ArtFold art carried over; it contradicts canon (single big head horn, snout horns, white coat): reported in the entry, not changed | OURS | adult art is artpipe in the art ledger |
| Gullipud | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Gullipud | NO_TWIN | gullipud (new) | 0 | PORTED | 39478dcd403f (W3d) | donor art extracted; unrostered (placement belongs to the biome sittings); PathfindingFramework MovementExtension kept MayRequire-guarded | KEEP_DONOR_ART_FOR_NOW | agrees |
| Gundark | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Gundark | NO_TWIN | gundark (new) | 0 | PORTED | 39478dcd403f (W3d) | donor art extracted; unrostered (placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | agrees; the second arm pair is a sprite-size limit (Engine limits), not chased |
| Gutkurr | PORTED_WIRED | RSW_Gutkurr | MATCH; namer | gutkurr | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| HarvesterBeetle | NOT_PORTED/PLAIN_DEPS | RSW_HarvesterBeetle | NO_TWIN | harvesterbeetle (new) | 0 | PORTED | dd2dea5ffead (W2c) | donor art extracted; unrostered (placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | agrees |
| Hawkbat | TWIN_NOT_WIRED | RSW_Hawkbat | MATCH; namer | hawkbat | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe/conflict-sheet in the art ledger |
| Horax | PORTED_WIRED | RSW_Horax | MATCH; namer | horax | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| Hrumph | PORTED_WIRED | RSW_Hrumph | MATCH; namer | hrumph | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| Hssiss | TWIN_NOT_WIRED | RSW_Hssiss | MATCH; namer | hssiss | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | EXISTING_RENDER | regenerated art already exists, not re-queued: thesump_Hssiss_v2 |
| Igitz | TWIN_NOT_WIRED | RSW_Igitz | MATCH; namer | igitz | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Insectomorph | NOT_PORTED/SHARED_BODY | RSW_Insectomorph | NO_TWIN | insectomorph | 0 | PORTED | cb1d215241e1 (W3c) | donor art extracted; unrostered (placement belongs to the biome sittings); owner ArtFold art baked in; existing entry not edited | OURS | adult art is ours in the art ledger |
| Iriaz | WIRED_DONOR_ROW | RSW_Iriaz | MATCH; namer | iriaz | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| IridonianReek | PORTED_WIRED | RSW_IridonianReek | MATCH; donor-only refs: IthorianReek, Reek; namer | iridonianreek | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| IthorianReek | NOT_PORTED/PLAIN_DEPS | RSW_IthorianReek | NO_TWIN | ithorianreek (new) | 0 | PORTED | dd2dea5ffead (W2c) | donor art extracted; unrostered (placement belongs to the biome sittings); no page of its own: a section of Reek/Legends; juvenile shares swanimals/Reek/Reek_j with the reeks | KEEP_DONOR_ART_FOR_NOW | yellow heavy rhino form, small horns: agrees |
| Jakobeast | PORTED_WIRED | RSW_Jakobeast | MATCH; donor-only refs: SW_ForcePush; namer | jakobeast | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| Jamel | WIRED_DONOR_ROW | RSW_Jamel | MATCH; donor-only refs: Cameloid_Meat, Jamel; namer | jamel | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Jimvu | PORTED_WIRED | RSW_Jimvu | DIFF: lifeExpectancy: donor 22 ours 30; namer | jimvu | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| JungleRancor | NOT_PORTED/SHARED_BODY_ITEMS | RSW_JungleRancor | NO_TWIN | junglerancor (new) | 0 | PORTED | ec18766ffd09 (W3a) | donor art extracted; unrostered (placement belongs to the biome sittings); male draws the donor BullRancor sprite (grey, tusked), contradicting canon: reported in the entry | REDRAWS_ON_SHEET2 | owner sent back donorport_junglerancor_m_v1 (purple canon images not canon); junglerancor_brown_v2 from the brown/red image only, canon PASS, graded PASS; offered in the JungleRancor (female) slot on donor_pack_redraws_sheet_2026-10-14, bull has no render of its own |
| Kaadu | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Kaadu | NO_TWIN | kaadu (new) | 0 | PORTED | ec18766ffd09 (W3b) | donor art extracted; unrostered (placement belongs to the biome sittings); body RSW_Kaadu shared with PaintedSpat; PathfindingFramework MovementExtension kept MayRequire-guarded | REDRAWS_ON_SHEET2 | female installed (owner pick, b104142ef); male enact_a4b6e31c_kaadu_v1 canon PASS, graded MARGINAL (dark spots unlike the female, 256 vs her 512); male swimming enact_e51fcd28_kaadu_v1 canon PASS, graded FAIL (striding on land, not swimming; prefill keeps current); on donor_pack_redraws_sheet_2026-10-14 |
| Katarn | NOT_PORTED/SHARED_BODY | RSW_Katarn | NO_TWIN | katarn (new) | 0 | PORTED | cb1d215241e1 (W3c) | donor art extracted; unrostered (placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | agrees |
| KellDragon | NOT_PORTED/PLAIN_DEPS | RSW_KellDragon | NO_TWIN | kelldragon (new) | 0 | PORTED | dd2dea5ffead (W2c) | donor art extracted; unrostered (placement belongs to the biome sittings); canon entry Legends-only | KEEP_DONOR_ART_FOR_NOW | agrees |
| Kinrath | TWIN_NOT_WIRED | RSW_Kinrath | MATCH; namer | kinrath | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Klorslug | TWIN_NOT_WIRED | RSW_Klorslug | MATCH; namer | klorslug | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| KowakianMonkeyLizard | TWIN_NOT_WIRED | RSW_KowakianMonkeyLizard | MATCH; namer | kowakianmonkeylizard | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| KraytDragon | PORTED_WIRED | RSW_KraytDragon | MATCH; donor-only refs: KellDragon; namer | kraytdragon | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| Kreetle | PORTED_WIRED | RSW_Kreetle | MATCH; namer | kreetle | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| Krykna | PORTED_WIRED | RSW_Krykna | MATCH; namer | krykna | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| KwazelMaw | NOT_PORTED/SHARED_BODY_ITEMS | RSW_KwazelMaw | NO_TWIN | kwazelmaw (new) | 0 | PORTED | 39478dcd403f (W3d) | donor art extracted; unrostered (placement belongs to the biome sittings); PathfindingFramework MovementExtension kept MayRequire-guarded | REDRAWS_ON_SHEET2 | adult installed (owner pick, b104142ef); swimming redrawn as enact_redo_kwazelmaw_swim_v2 (1024 like the adult; v1 was 256 and its north/south failed canon on head and markings) canon PASS, graded MARGINAL (legs still show east); on donor_pack_redraws_sheet_2026-10-14 |
| Kwi | PORTED_WIRED | RSW_Kwi | MATCH; donor-only refs: Kwi, SW_Spur; namer | kwi | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| Kybuck | TWIN_NOT_WIRED | RSW_Kybuck | MATCH; namer | kybuck | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | EXISTING_RENDER | regenerated art already exists, not re-queued: desert_swaca_kybuck, leaningscrub_kybuck_v1, regen_ls2_canon_kybuck_v2 |
| LavaFlea | TWIN_NOT_WIRED | RSW_LavaFlea | MATCH; namer | lavaflea | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | EXISTING_RENDER | regenerated art already exists, not re-queued: canonregen_rsw_lavaflea_v1 |
| Leaftail | NOT_PORTED/PLAIN | RSW_Leaftail | NO_TWIN | leaftail (new) | 0 | PORTED | 695812d5ec72 (W2b) | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings) | RENDERED_ON_SHEET | donorport_leaftail_v1 3/3 PASS; graded PASS; on donor_pack_port_sheet_2026-10-14 |
| LongtailGorg | WIRED_DONOR_ROW | RSW_LongtailGorg | DIFF: baseBodySize: donor 0.6 ours 0.42; namer | longtailgorg | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| LothWolf | NOT_PORTED/PLAIN_DEPS | RSW_LothWolf | NO_TWIN | lothwolf (new) | 0 | PORTED | dd2dea5ffead (W2c) | donor art extracted; unrostered (placement belongs to the biome sittings); canon Loth-wolves are SENTIENT and speak Basic; ported as an animal, reported in the entry; ports SW_ForceChaosSkip as RSW_SW_ForceChaosSkip | KEEP_DONOR_ART_FOR_NOW | agrees (black coat is attested) |
| Lothcat | TWIN_NOT_WIRED | RSW_Lothcat | MATCH; namer | lothcat | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| Lylek | TWIN_NOT_WIRED | RSW_Lylek | MATCH; namer | lylek | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Maalraas | NOT_PORTED/PLAIN_DEPS | RSW_Maalraas | NO_TWIN | maalraas (new) | 0 | PORTED | dd2dea5ffead (W2c) | donor art extracted; unrostered (placement belongs to the biome sittings); ports SW_ForceInvisibility as RSW_SW_ForceInvisibility | KEEP_DONOR_ART_FOR_NOW | agrees with the concept art |
| Manka | NOT_PORTED/SHARED_BODY | RSW_Manka | NO_TWIN | manka (new; canon page "Manka cat") | 0 | PORTED | cb1d215241e1 (W3c) | donor art extracted; unrostered (placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | agrees |
| MarshHaunt | TWIN_NOT_WIRED | RSW_MarshHaunt | MATCH; namer | marshhaunt | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| Massiff | TWIN_NOT_WIRED | RSW_Massiff | MATCH; namer | massiff | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| MastiffPhalone | NOT_PORTED/SHARED_BODY_ITEMS | RSW_MastiffPhalone | NO_TWIN | mastiffphalone (new) | 0 | PORTED | 39478dcd403f (W3d) | donor art extracted; unrostered (placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | agrees |
| Mastmot | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Mastmot | NO_TWIN | mastmot (new) | 0 | PORTED | 39478dcd403f (W3d) | donor art extracted; unrostered (placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | cream shaggy, down-curving tusks drawn; hump and nasal horns understated (borderline pass) |
| Mawvorr | NOT_PORTED/SHARED_BODY | RSW_Mawvorr | NO_TWIN | mawvorr (new) | 0 | PORTED | cb1d215241e1 (W3c) | donor art extracted; unrostered (placement belongs to the biome sittings); canon page has no image: brief is text plus the donor sprite | KEEP_DONOR_ART_FOR_NOW | agrees; four eyes not readable at sprite size (size limit) |
| Mott | TWIN_NOT_WIRED | RSW_Mott | MATCH; namer | mott | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| Mudhorn | TWIN_NOT_WIRED | RSW_Mudhorn | MATCH; namer | mudhorn | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Mynock | DECLINED | RSW_Mynock | DECLINED | mynock | 2 | DECLINED |  | owner 2026-09-18: donor Mynock stays unported; RSW_Mynock is an unrelated owner-authored species | DECLINED |  |
| Narglatch | NOT_PORTED/PLAIN | RSW_Narglatch | NO_TWIN | narglatch (new) | 0 | PORTED | 695812d5ec72 (W2b) | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings) | REDRAWS_ON_SHEET2 | female installed (owner pick, b104142ef); male enact_32ab0b1b_narglatch_v1 canon PASS, graded PASS (256 vs her 512); on donor_pack_redraws_sheet_2026-10-14 |
| Neebray | TWIN_NOT_WIRED | RSW_Neebray | MATCH; namer | neebray | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| Nerf | PORTED_WIRED | RSW_Nerf | MATCH; donor-only refs: Grazer, SW_Spit; namer | nerf | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| Nexu | NOT_PORTED/SHARED_BODY | RSW_Nexu | NO_TWIN | nexu (new) | 0 | PORTED | cb1d215241e1 (W3c) | donor art extracted; unrostered (placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | tint mask over striped greyscale art; def alternates tint it tan/brown (one white alternate is a def tint question, not art) |
| Nuna | PORTED_WIRED | RSW_Nuna | MATCH; namer | nuna | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| Ollopom | TWIN_NOT_WIRED | RSW_Ollopom | MATCH; namer | ollopom | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Orray | TWIN_NOT_WIRED | RSW_Orray | MATCH; namer | orray | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| PaintedSpat | NOT_PORTED/SHARED_BODY_ITEMS | RSW_PaintedSpat | NO_TWIN | paintedspat (new) | 0 | PORTED | ec18766ffd09 (W3b) | donor art extracted; unrostered (placement belongs to the biome sittings); shares RSW_Kaadu body | KEEP_DONOR_ART_FOR_NOW | agrees |
| PekoPeko | TWIN_NOT_WIRED | RSW_PekoPeko | MATCH; namer | pekopeko | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| Pikobis | TWIN_NOT_WIRED | RSW_Pikobis | MATCH; namer | pikobis | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Porg | TWIN_NOT_WIRED | RSW_Porg | MATCH; namer | porg | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| Pufferpig | TWIN_NOT_WIRED | RSW_Pufferpig | MATCH; donor-only refs: Pufferpig; namer | pufferpig | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Qormot | TWIN_NOT_WIRED | RSW_Qormot | MATCH; namer | qormot | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Rancor | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Rancor | NO_TWIN | rancor (new) | 0 | PORTED | ec18766ffd09 (W3a) | donor art extracted; unrostered (placement belongs to the biome sittings); body RSW_Rancor shared by the three rancors; ports SW_ToxicSpew | KEEP_DONOR_ART_FOR_NOW | agrees |
| Raxshir | NOT_PORTED/PLAIN | RSW_Raxshir | NO_TWIN | raxshir (new) | 0 | PORTED | 695812d5ec72 (W2b) | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | agrees |
| Reek | NOT_PORTED/PLAIN_DEPS | RSW_Reek | NO_TWIN | reek (new) | 0 | PORTED | dd2dea5ffead (W2c) | donor art extracted; unrostered (placement belongs to the biome sittings) | REDRAWS_ON_SHEET2 | adult installed (owner pick, b104142ef); juvenile Reek_j redrawn as enact_redo_reek_j_v2 (512, adult as anchor; v1 failed canon on cheek horns) canon PASS, graded MARGINAL (reads as a small adult); on donor_pack_redraws_sheet_2026-10-14 |
| Rikknit | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Rikknit | NO_TWIN | rikknit (new; Legends only) | 0 | PORTED | e6d89d7d2eb0 (W3e) | donor art extracted; unrostered (placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | agrees |
| Roggwart | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Roggwart | NO_TWIN | roggwart (new) | 0 | PORTED | e6d89d7d2eb0 (W3e) | donor art extracted; unrostered (placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | agrees |
| Ronto | WIRED_DONOR_ROW | RSW_Ronto | MATCH; namer | ronto | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Runyip | WIRED_DONOR_ROW | RSW_Runyip | MATCH; namer | runyip | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Rycrit | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Rycrit | NO_TWIN | rycrit (new) | 0 | PORTED | e6d89d7d2eb0 (W3e) | donor art extracted; unrostered (placement belongs to the biome sittings); colour unsourced | KEEP_DONOR_ART_FOR_NOW | colour unsourced; shape agrees |
| Scavrat | TWIN_NOT_WIRED | RSW_Scavrat | MATCH; namer | NONE | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | EXISTING_RENDER | regenerated art already exists, not re-queued: desert_swaca_scavrat, legacy_79c497a0_scavrat_v1 |
| Scurrier | WIRED_DONOR_ROW | RSW_Scurrier | DIFF: texPath not in our tree: swanimals/Scurrier/Scurrier_m; namer | scurrier | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | rows repointed; owner by card 2026-10-14: COMMISSION a new male against the canon entry (the donor male art stays unused; the ledger refuses it, purged 16618daa21c9). Until it lands, swanimals/Scurrier/Scurrier_m binds only through the donor. | COMMISSIONED_BY_SECOND_WORKER | male only, owner card 2026-10-14; female/juvenile are ours |
| Shaak | PORTED_WIRED | RSW_Shaak | DIFF: baseBodySize: donor 2.0 ours 3; namer | shaaks | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| Shiro | TWIN_NOT_WIRED | RSW_Shiro | MATCH; namer | shiro | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is ours in the art ledger |
| ShiroTrap | WIRED_DONOR_ROW | RSW_ShiroTrap | MATCH; donor-only refs: RawTookeTrapRoot; namer | shirotrap | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Shyrack | WIRED_DONOR_ROW | RSW_Shyrack | MATCH; namer | shyrack | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Silooth | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Silooth | NO_TWIN | silooth | 0 | PORTED | e6d89d7d2eb0 (W3e) | donor art extracted; unrostered (placement belongs to the biome sittings); owner ArtFold art and the Silooth_Warbeast patch (RSW_SiloothAcidSpit) baked in; existing entry not edited; ports SW_AcidSpew | OURS | adult art is artpipe in the art ledger |
| Skalder | WIRED_DONOR_ROW | RSW_Skalder | MATCH; donor-only refs: SkalderTusk; namer | skalders | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Sketto | WIRED_DONOR_ROW | RSW_Sketto | MATCH; namer | sketto | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| Snoruuk | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Snoruuk | NO_TWIN | snoruuk | 0 | PORTED | (W4b) | owner pick by card 2026-10-14: adult art is artpipe render enact_6811876e_snoruuk_v1 (N/E/S) installed through the art ledger; juvenile, stationary, dessicated and egg art are extracted donor art; both TheRot rows repointed | OURS | adult is the owner's pick by card 2026-10-14 (enact_6811876e_snoruuk_v1); juvenile/stationary donor art stays |
| Squall | NOT_PORTED/PLAIN | RSW_Squall | NO_TWIN | squall (new) | 0 | PORTED | 695812d5ec72 (W2b) | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings); Wookieepedia title is "Squall (species)"; canon page is a stub | KEEP_DONOR_ART_FOR_NOW | tint mask: def alternates tint it brown (80%); shape and bushy tail agree |
| Stintaril | NOT_PORTED/PLAIN | RSW_Stintaril | NO_TWIN | stintaril (new) | 0 | PORTED | 695812d5ec72 (W2b) | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings) | RENDERED_ON_SHEET | donorport_stintaril_v1 3/3 PASS; graded MARGINAL (small thin figure, barely reads at game size); on donor_pack_port_sheet_2026-10-14 |
| Strill | TWIN_NOT_WIRED | RSW_Strill | MATCH; namer | strill | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Tach | NOT_PORTED/PLAIN | RSW_Tach | NO_TWIN | tach (new) | 0 | PORTED | 695812d5ec72 (W2b) | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | agrees |
| Taozin | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Taozin | NO_TWIN | taozin (new) | 0 | PORTED | e6d89d7d2eb0 (W3e) | donor art extracted; unrostered (placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | matches the Legends adult (red/cream rings, green eyes) |
| Tauntaun | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Tauntaun | NO_TWIN | tauntaun | 0 | PORTED | 584de64af490 (W2a) | owner canon art (Tauntaun_CanonArt patch) baked in; only the two dessicated textures are extracted donor art; NightsideIce row repointed, its FindMod guard moved to SWBestiary | OURS | adult art is artpipe in the art ledger |
| TeeMuss | PORTED_WIRED | RSW_TeeMuss | MATCH; namer | teemuss | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| TetnissCrab | NOT_PORTED/SHARED_BODY_ITEMS | RSW_TetnissCrab | NO_TWIN | tetnisscrab (new; canon species "Trash crab") | 0 | PORTED | e6d89d7d2eb0 (W3e) | donor art extracted; unrostered (placement belongs to the biome sittings); canon hints trash crabs may be sentient (a character's belief): reported | KEEP_DONOR_ART_FOR_NOW | agrees |
| Thranta | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Thranta | NO_TWIN | thranta (new) | 0 | PORTED | e6d89d7d2eb0 (W3e) | donor art extracted; unrostered (placement belongs to the biome sittings); canon says it flies: real flight owed (MaxFlightTime + flip-book; never live-test without the owner) | KEEP_DONOR_ART_FOR_NOW | agrees |
| Tibidee | NOT_PORTED/SHARED_BODY | RSW_Tibidee | NO_TWIN | tibidee | 0 | PORTED | 584de64af490 (W2a) | donor art extracted; canon says flier: real flight owed (MaxFlightTime + flip-book art; never live-test flight without the owner); TheForge row repointed | EXISTING_RENDER | regenerated art already exists, not re-queued: gapall_Tibidee_v1 |
| Tooke | NOT_PORTED/PLAIN | RSW_Tooke | NO_TWIN | tooke (new) | 0 | PORTED | 695812d5ec72 (W2b) | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | agrees |
| Torton | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Torton | NO_TWIN | torton (new) | 0 | PORTED | e6d89d7d2eb0 (W3e) | donor art extracted; unrostered (placement belongs to the biome sittings); canon text "red and green" vs brown images: reported | KEEP_DONOR_ART_FOR_NOW | agrees (brown is image-canon) |
| Tukata | NOT_PORTED/SHARED_BODY | RSW_Tukata | NO_TWIN | tukata (new; canon page "Tuk'ata") | 0 | PORTED | cb1d215241e1 (W3c) | donor art extracted; unrostered (placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | agrees |
| TuskCat | NOT_PORTED/PLAIN | RSW_TuskCat | NO_TWIN | tuskcat (new) | 0 | PORTED | 695812d5ec72 (W2b) | donor art extracted; unrostered (no roster names it; placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | agrees; colour unsourced |
| Urusai | TWIN_NOT_WIRED | RSW_Urusai | MATCH; namer | urusai | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Uvak | PORTED_WIRED | RSW_Uvak | MATCH; namer | uvak | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| Vapaad | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Vapaad | NO_TWIN | vaapad | 0 | PORTED | 584de64af490 (W2a) | owner Blue Desert art + canon description (Vapaad_BlueDesertArt patch) baked in; that art lives in UtinniPatches (RUT tier) while the def is RSW: tier smell, not moved; BlueDesert row repointed, FindMod guard moved to SWBestiary | OURS | adult art is artpipe in the art ledger |
| Varactyl | PORTED_WIRED | RSW_Varactyl | MATCH; namer | varactyl | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| Veermok | NOT_PORTED/SHARED_BODY | RSW_Veermok | NO_TWIN | veermok (new) | 0 | PORTED | cb1d215241e1 (W3c) | donor art extracted; unrostered (placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | agrees |
| Voorpak | WIRED_DONOR_ROW | RSW_Voorpak | MATCH; namer | voorpak | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Vornskyr | TWIN_NOT_WIRED | RSW_Vornskyr | MATCH; donor-only refs: Vornskyr; namer | vornskyr | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is ours in the art ledger |
| Vulptex | TWIN_NOT_WIRED | RSW_Vulptex | MATCH; namer | vulptex | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| Wampa | TWIN_NOT_WIRED | RSW_Wampa | MATCH; namer | wampa | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| WarWyrm | PORTED_WIRED | RSW_WarWyrm | DIFF: baseBodySize: donor 15.0 ours 22.5; donor-only refs: WarWyrmSkull; namer | sith_wyrm | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| Warbird | NOT_PORTED/SHARED_BODY_ITEMS | RSW_Warbird | NO_TWIN | warbird (new; canon page "Sith warbird") | 0 | PORTED | e6d89d7d2eb0 (W3e) | donor art extracted; unrostered (placement belongs to the biome sittings) | KEEP_DONOR_ART_FOR_NOW | agrees |
| Whisperbird | TWIN_NOT_WIRED | RSW_Whisperbird | MATCH; namer | whisperbird | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is artpipe in the art ledger |
| WompRat | TWIN_NOT_WIRED | RSW_WompRat | MATCH; namer | womprat | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | EXISTING_RENDER | regenerated art already exists, not re-queued: canonregen_rsw_womprat_v1, desert_swaca_womprat |
| Woolamander | TWIN_NOT_WIRED | RSW_Woolamander | MATCH; namer | woolamander | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OWNER_KEPT | owner keep ruling (trust=ruled) on the live donor picture |
| Worrt | PORTED_WIRED | RSW_Worrt | MATCH; namer | worrt | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| Wraid | PORTED_WIRED | RSW_Wraid | MATCH; namer | wraid | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |
| Wyyyschokk | NOT_PORTED/SHARED_BODY_ITEMS | RM_Ollathrix | NO_TWIN | wyyyschokk | 0 | DONE_ALREADY_OWNED | 584de64af490 (W2a) | not ported: owner 2026-10-03 ruled RM_Ollathrix is THE wyyyschokk (RSW_Wyyyschokk retired, WYYYSCHOKK_IDENTITY_COLLISION_1); the RUT_Webwork donor row is repointed to RM_Ollathrix (mandrake.rm.webwork) | OURS | adult art is artpipe in the art ledger |
| Yobshrimp | TWIN_NOT_WIRED | RSW_Yobshrimp | DIFF: stat ArmorRating_Blunt: donor 0.08 ours 0.10; stat ArmorRating_Sharp: donor 0.12 ours 0.20; stat ComfyTemperatureMax: donor 60 ours 55; stat ComfyTemperatureMin: donor -10 ours -5; stat LeatherAmount: donor 0 ours None; stat MarketValue: donor 60 ours 40; stat MoveSpeed: donor 2.5 ours 3.2; stat Wildness: donor 0.2 ours 0.8; baseBodySize: donor 0.4 ours 0.2; baseHealthScale: donor 0.4 ours 0.35; lifeExpectancy: donor 3 ours 8; body: donor Yobshrimp ours BeetleLike; lifeStageAges: donor [('AnimalBaby', '0'), ('AnimalJuvenile', '0.05'), ('AnimalAdult', '0.1')] ours [('AnimalBaby', '0'), ('AnimalJuvenile', '0.1'), ('AnimalAdult', '0.25')] | paleyobshrimp | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is ours in the art ledger |
| Zakkeg | TWIN_NOT_WIRED | RSW_Zakkeg | MATCH; namer | zakkeg | 0 | DONE_ALREADY_OWNED | deab5ccedac4 (W1) | donor roster rows repointed to the twin; defs and art untouched | OURS | adult art is ours in the art ledger |
| Zeer | PORTED_WIRED | RSW_Zeer | DIFF: baseBodySize: donor 3.0 ours 4.5; namer | zeer | 0 | DONE_ALREADY_OWNED | 5d97437d51ff (W0) | twin wired, no donor row; untouched | OURS | adult art is artpipe in the art ledger |

## W0 findings (2026-10-14)

`donor_pack_port.py diff`: 160 donor races; 91 twins MATCH the donor on statBases, body, bodySize, healthScale,
lifeExpectancy, lifeStageAges and PawnKind lifeStage count, with every texPath resolving in our tree; 9 DIFF;
59 have no twin; Mynock DECLINED. No twin is a stub. Nothing was rewritten.

| twin | difference | reading |
|---|---|---|
| RSW_Gorg, RSW_LongtailGorg | bodySize 0.7x donor | owner sheet ruling (`f4027c934` "30% smaller") |
| RSW_WarWyrm, RSW_Shaak, RSW_Zeer | bodySize 1.5x donor | owner sheet ruling (`a89376420` "50% bigger", same pass) |
| RSW_Blurrg | adds CaravanRidingSpeedFactor 1.5, MeatAmount 350 | deliberate mount sizing (its header comment) |
| RSW_Yobshrimp | different creature (BeetleLike body, sea swarm) | our SeaBeasts redesign, not a port |
| RSW_Jimvu | lifeExpectancy 30 vs donor 22 | set at its port (`bab45edca`); unexplained; reported, not changed |
| RSW_Scurrier | texPath `swanimals/Scurrier/Scurrier_m` has no PNG in our tree | binds only through the donor; fix row: extract the male art (same picture the game shows today) |

## Wave commits

| wave | sha | what |
|---|---|---|
| W0 | 5d97437d51ff | twin diff + this tracker |
| W1 | deab5ccedac4 | 82 donor roster rows in 10 `RUT_*` BiomeDefs repointed to the RSW_ twin under `MayRequire="mandrake.rsw.swbestiary"`; 4 left (Mynock x2 declined, Snoruuk, Wyyyschokk not yet ported) |
| W2a | 584de64af490 | the 5 roster-named species: Tauntaun, Tibidee, Vapaad ported; Snoruuk ART_BLOCKED; Wyyyschokk is RM_Ollathrix |
| W2b | 695812d5ec72 | 13 plain species ported, 13 canon entries written (one per species, all sourced from Wookieepedia; Bursa Legends-only) |
| W2c | dd2dea5ffead | 7 plain-with-deps species ported; 6 canon entries written (Ithorian reek from a Reek/Legends section) |
| W3a+W3b | ec18766ffd09 | rancor family (Rancor, JungleRancor, ChrysalideRancor; one shared body) and Kaadu + PaintedSpat (one shared body) |
| W3c | cb1d215241e1 | the 11 custom-body species with no items/abilities (one body each) |
| W3d | 39478dcd403f | 9 custom-body species with items/abilities (Akk to Mastmot) |
| W3e | e6d89d7d2eb0 | the last 9 custom-body species with items/abilities (Rikknit to Warbird) |
| W4a | 9072cc4cdaa0 | twins off the donor's defs: 254 refs repointed, 10 support defs ported, checker extended |
| W4b | 570bbe038eb0 | Snoruuk ported with the owner-picked render (card 2026-10-14); both TheRot rows repointed |

W1 check: `validate_patch.py --live --defs` 10 files 0 errors 0 warnings, but it does NOT check BiomeDef roster names
(probe: a bogus `RSW_NotABeastZZ` row passed), so `donor_pack_port.py check` does: 188 RSW_ roster rows resolve to an
RSW_ race with a PawnKindDef, 0 unresolved (probe: the bogus row is caught, exit 1).

## W4a: the twins off the donor's defs (2026-10-14)

`donor_pack_port.py check` now also fails on (1) any name in our Defs/Patches that only the donor's own Defs define
(not vanilla/DLC, not ours) and that no `MayRequire`/`FindMod` guards on the donor, and (2) any `sw*` texPath of ours
that only the donor's bundle serves. Prose fields (`label`, `description`...) and two C# `string` fields
(`anchorThingDef`, ExplosiveGrowth `plant`) are not references. Probe: a temp def naming `SWAnimalNamerMale` and a bare
`KellDragon` is caught (exit 1); a guarded `Grazer` and a `<label>Reek</label>` are not.

The earlier W0b list over-counted: the bare species names (Borcatu, Dragonsnake, Grank, Jamel, Kwi, Pufferpig,
Vornskyr) were `<label>` text, not references. Done in W4a: 254 references rewritten to the existing RSW_ copy
(`repoint-refs`: the namers x214, `SW_Spur`/`SW_Spit`/`SW_AcidSpew`, `Cameloid_Meat`, `AteCrustapodRoe`, crossbreed
partners Grazer/KellDragon/Reek/IthorianReek); 10 donor defs ported as RSW_ into `RSW_DonorPack_W4a.xml`
(`port --defs`: SW_ForcePush ability + trainable + projectile, AteToughMeat/AteChakroot/AteBloddle/AteAcklayClaw,
RawTookeTrapRoot, SkalderTusk, WarWyrmSkull) with their 5 PNGs, plus 4 raw-food PNGs the DesertPort plants named
(Bloddle, Chakroot, HubbaGourd, Nysyllin), all extracted donor art through the art ledger; 2 wildPlants rows naming
donor plants with no RSW_ copy guarded with `MayRequire` (RUT_AridShrubland Nysyllin, RUT_Webwork TookeTrap), as
RUT_Greentide already was. Result: 0 unguarded donor-only references.

Left, both owner art: `swanimals/Scurrier/Scurrier_m` (commission ruled 2026-10-14) and `swplants/Nysillin`
(RSW_Plant_Nysyllin_Wild; the ledger refuses the donor picture: sent back for redo on leaningscrub_sheet_2026-10-05).
Guarded references that simply go quiet donor-off (not errors): faction carriers Bantha/Dewback, the
`sw_DeadSarlaccCave` landmark, 10 guarded donor-plant wildPlants rows, the ExplosiveGrowth donor-plant rows.

## Part B: which art to commission (2026-10-14)

Census of the adult texPaths of all 159 species (Mynock declined): 79 OURS, 18 OWNER_KEPT, 11 EXISTING_RENDER,
40 KEEP_DONOR_ART_FOR_NOW, 10 COMMISSIONED, 1 COMMISSIONED_BY_SECOND_WORKER (Scurrier male). "Handled" was read from
the art ledger (live file sha vs donor variants; owner rulings by sha) and `artpipe_state.py find` over every candidate
(bound jobs and name-matched renders), never from names. Every already-owned twin still drawing donor art either
carries an owner keep or already has regenerated renders (canonregen_/regen_/enact_ jobs), so none was re-queued.
Graded by contact sheet against each entry's `## Must show`: a tint-masked greyscale sprite (CutoutComplex) was
judged in its def tint, not as the raw PNG (corrects the W2-W3 notes on ChrysalideRancor and Squall).

**Submitted:** 11 rows, 33 jobs (east master, north/south derived) into the running artpipe daemon with
`fill_queue.py --input design/RimMandrake/donor_pack_art_commission_2026-10-14.json`: canon slug and the entry's
images as anatomy guidance, `target_def`/`target_texpath` bound, `install_to` the port's own texPath, canvas by
drawSize (256/512/1024), priority 30 (big, visible species) or 40. Under the ~40 cap, so nothing is queued behind it.
First pass: 25 jobs failed in ~2 s (codex worker: "The 'gpt-5.5' model is not supported when using Codex with a ChatGPT
account"); the daemon was moved to gpt-5.6-sol and restarted by the coordinator, the 25 were requeued under their own
ids (failed/ -> pending/, manifests parked in _requeued_manifests/, as requeue_flakes.py does), and renders are landing
in done/ (boarwolf east checked by eye: hump, tusks, fangs, claws, grey-blue: matches Must show).

**Owed after the renders land:** look at them (canon_check gate, then a review sheet for the owner, since these
replace stand-ins he has not ruled on), then `artpipe_state.py collect --from-jobs` installs through the art ledger.
Grazer: its own entry now exists (`canon_references/grazerdomestic/`, 2026-10-14); the wild entry stays RSW_FeralGrazer's.
OWNER_QUESTION: none new (Snoruuk and Scurrier were ruled by card 2026-10-14).

**Collected (2026-10-14, FOUNDRY):** 30 renders in done/ for 9 species, all canon PASS; graded by eye at display size:
7 PASS, 2 MARGINAL (Kaadu, Stintaril), Aiwha FAIL/ART_BLOCKED (2 rounds, see its row). Requeued under new ids only
(`donor_pack_art_requeue_2026-10-14_{kaadu,aiwha}.json`); 3 generations this session (kaadu 1, aiwha east 2). Review sheet
`Transient/biome_ffar/donor_pack_port_sheet_2026-10-14.html` (art_sheet.py --subjects, gate PASS, served by serve_gated.py); agent prefill =
the render on every row, a suggestion only; skipping keeps the donor art. Sizes are FALLBACK 1 cell: the new RSW_
defs are not in the live dump until the next capture. **Install waits for his answers** (`art.py enact` on the
decisions file, then `artpipe_state.py collect --from-jobs`).

**Checker leftovers resolved:** `RSW_Bullet_AnimalToxbomb` `Things/Projectile/Acid` is NOT a defect: Biotech and
Anomaly ship that texPath (Data/*/Defs/AbilityDefs/Abilities.xml, Graphic_Random over Acid_A..J); the check reports it
only when run without `--vanilla-tex <names>`. `swplants/Nysillin`: a regenerated version already exists:
`ls3_nysyllin_a_v1` and `ls3_nysyllin_b_v1` (canon PASS, 2026-10-08, filed from his note "Ok, now make a realistic
version based on this, two variants"), shown as columns F/G on `leaningscrub_sheet_2026-10-05`; awaiting his pick
there, not a new commission.

**Second sheet (2026-10-14, FOUNDRY, after the owner's enact b104142ef):** the enact's redraw jobs were graded. Failed in
the artpipe on the canon check (not transient): boarwolf_j east (fangs), reek_j east (cheek horns), kwazelmaw swimming
north/south (head shape, markings); all had been filed at 256 px with the donor cartoon as their only reference. Refiled
once under new ids with the real canon images plus the installed adult as a style anchor, at the adult's canvas
(`donor_pack_art_requeue_2026-10-14_enact_{boarwolf,reek,kwazelmaw}.json`; boarwolf first, then the rest): 9 jobs, 10
generations (one internal canon retry), all canon PASS, none failed twice. Grades by eye at display size: PASS 5
(Boarwolf j, Narglatch m, Jungle Rancor brown, Nysillin ls3 a, Nysillin ls3 b), MARGINAL 3 (Reek j, Kwazel Maw
swimming, Kaadu m), FAIL 1 (Kaadu m swimming: striding, not swimming; not refiled, his call). Sheet
`Transient/biome_ffar/donor_pack_redraws_sheet_2026-10-14.html` (art_sheet.py --subjects --jobs --recommend, gate PASS,
served by serve_gated.py), agent prefill = the recommended render, skipping keeps the current picture. The Nysillin row
carries `ls3_nysyllin_a_v1`/`_b_v1` (b recommended). Builder changes: a subjects sheet no longer collapses a row he ruled
elsewhere when it names a render filed after that ruling (gate req 7 agrees); a render whose job names a `slot` is
never joined to another graphic by creature name; `--recommend FAMILY=WHY` sets the agent prefill.
**Owed:** his answers on that sheet, then `art.py enact` on its decisions file.

## How a port is made (W2 on)

`donor_pack_port.py port --batch B --species A,B --extract <bundle dump> --active <active list> --vanilla <names>`:
race ThingDef + PawnKindDef to `SWBestiary/Defs/ThingDefs_Races/RSW_<Sp>.xml`; every donor-only def they reach to
`SWBestiary/Defs/DonorPackPort/RSW_DonorPack_<B>.xml` as RSW_<name> (once; existing RSW_ copies are reused);
**our own patches that target the donor defName are applied first** (owner art folds and canon-art patches,
BeastNorm, tolerances, evictions, resizes), so the port is the creature the game shows today and owner-handled art is
moved over, not regenerated. A species whose art the ledger refuses (owner purge or send-back) or the bundle lacks is
ART_BLOCKED and left out whole. Art goes through `artwrite.TextureWriter` (the art ledger).
Owed when the donor is retired (W4): the patch ops that still name a ported donor defName go dead (their effect is
baked into the port); generators that emit them (BeastNorm manifest, MegafaunaYield, AnimalTolerances, evictions)
should learn the RSW_ names before they are next regenerated.

New ports differ from the raw donor only where our own patches already changed the donor in game (W0 diff on the
ports: comfy-temperature pins from `AnimalTolerances_Ashkarr.xml` on 9 of 23; BeastNorm tool numbers are not in
the diff). No new port names a donor-only def (`donor_refs` empty for all of them).

## Owed, not done here (W4 and anything live)

- **W4, the donor-off load** (L2 on a quicktest map): remove `mlie.starwarsanimalcollection` from a minimal test list and
  load with every biome still generating. Not run: no game, no bridge, no ModsConfig change in this pass.
- **Roster rows still on the donor:** Mynock x2 (declined, stays). Snoruuk rows repointed in W4b.
- **Other donor references outside rosters** (not roster rows, so not repointed): faction `carriers` (Bantha x2,
  Dewback) in JawaHuttCartel / JawaWildsteamClan, `specificMeatDef` in SeaBeasts_Scalefish, `RUT_CauldronPrizedMeats` /
  `Cauldron_ToxicPrizedMeat`, the `sw_DeadSarlaccCave` landmark mutator, 12 `wildPlants` rows (9 donor plants), and
  patches that only ever targeted the donor (ArtFold, BeastNorm, MegafaunaYield, AnimalTolerances, evictions,
  ShokkweaveButcherYield, TrophyCraft fang drop, AnimalBiomeDuplicates) which go dead with it.
- **Deploy:** only dry runs were made (`deploy_custom_mods.py --mod SWBestiary|UtinniPatches`); the `--apply` is owed
  with the next load round.
- **Flight** for canon fliers ported here (Tibidee, Aiwha, Drexl, Thranta; Brezak glides): MaxFlightTime + whole-body
  flip-book art, under the standing flyer rule; never live-tested without the owner.
- **Placement:** the 54 newly ported species with no roster row are unrostered; where they live is each biome
  sitting's call (evictions and keep/cut stay with the sittings).
- **Art:** the 33 commissioned renders (Part B) are owed collection and review; the other ports keep extracted donor art
  as a stand-in (owner 2026-10-14).
