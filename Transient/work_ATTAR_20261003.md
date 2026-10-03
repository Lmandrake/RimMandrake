# MIASMA_ATTAR_STILL_1 work 2026-10-03
- claimed+started. Searched src/ and artpipe: no attar def/art/CSV row (artpipe find attar = 0 hits). Art NOT queued: no turn-1 CSV row for it exists; placeholder = tinted delta-silt/salt icons reused.
## Plan / choices
- RM_Attar item (MarketValue 90) ; RM_AttarStill = powerless workbench (BenchBase), recipe RM_MakeAttar: 4 delta silt + 2 delta salt -> 1 attar (silt via filter, salt second ingredient). Hand-fed bill pattern, not the sun-still.
- Glaze: right-click an artwork (building with CompArt) with attar in reach -> job RM_GlazeArtwork. Glazed set stored in a Scribed GameComponent; Beauty raised by a StatPart on StatDef Beauty (XML patch), no Harmony.
- Balm: right-click a pawn with a scar (permanent Hediff_Injury) -> job RM_BalmScar; reduces ONE scar's severity until removed. Never touches non-permanent injuries, never heals anything else.
- Settings: attarEnabled (gates both the still bench bill and the float menu / stat part).
## Done
- Files (Miasma only): Source/RM_Attar.cs (+csproj Compile), Source/RM_MiasmaMod.cs (attarEnabled + applier hides recipe on RM_AttarStill), Defs/ThingDefs_Items/RM_Attar.xml (RM_Attar, RM_AttarStill), Defs/RecipeDefs/RM_MakeAttar.xml (4 silt + 2 salt -> 1), Defs/JobDefs/RM_Jobs_Attar.xml, Patches/RM_Attar_BeautyPart.xml (StatPart_Glazed +3 Beauty on glazed artworks), placeholder PNGs, validation.py (static + UNMEASURED live chain).
- Glaze registry is a GameComponent (Scribed ids); balm removes 3 severity from the first permanent scar only.
- Build OK (winbuild Miasma). Static PASS. validate_patch 0 errors (no --defs: parent/texPath cross-checks skipped).
- UNMEASURED: Beauty stat cache refresh after glaze (if Beauty is cached, effect shows after reload), live recipe/glaze/balm. Art placeholders; no artpipe job queued (no CSV row).
