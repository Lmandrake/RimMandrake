# SauridFrillFix — validation walk
subject: src/RimMandrake/SauridFrillFix  (packageId mandrake.rm.sauridfrillfix)
deps: vanillaracesexpanded.saurid (hard modDependency, "Vanilla Races Expanded - Saurid" — this mod must load AFTER it; loose-PNG override, order-dependent)
list: full   # third-party donor mod is not in the minimal list; no minimal+ variant exists for it
status-hint: one loose PNG replacing a donor-mod texture whose real filename carries a stray trailing hyphen ("CenterFrill8_north-.png"), so the game never finds it and Graphic_Multi silently falls back to the south sprite for that direction.

## must be true
- Ships exactly one file, `SauridFrillFix/Textures/Pawn/CenterFrill/CenterFrill8_north.png` (correctly named, no hyphen) — confirmed present on disk, no Defs, no Source, no XML patch of any kind (About.xml: "No defs are patched, no code runs").
- The donor's own `HairDef VRESaurids_Littlefoot` (`vanillaracesexpanded.saurid`'s `1.6/Defs/HairDefs/HairDefs_Saurid.xml:68`) asks for `texPath Pawn/CenterFrill/CenterFrill8` — this mod supplies only the missing `_north` facing at that path; `_east`/`_south` remain the donor's own, untouched files.
- Because this mod loads AFTER the donor (About.xml `loadAfter: vanillaracesexpanded.saurid`) and both ship loose PNGs (no AssetBundle), ContentFinder's last-mod-wins resolution must pick THIS mod's `_north` file over the donor's missing/absent one for the fix to take effect.
- No log line can prove the fix landed — "Failed to find any textures at" only fires when EVERY direction of a `Graphic_Multi` is absent, and one present direction (even the donor's own correctly-named `_east`/`_south`) suppresses it regardless of `_north`'s state (About.xml: "The defect cannot appear in the log").

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.sauridfrillfix" and no XML error naming this mod (trivial — it ships no XML/Defs at all, only a loose PNG)   # load-time
2. [L] Player.log after load does NOT contain "Failed to find any textures at" naming `Pawn/CenterFrill/CenterFrill8` — a NEGATIVE check only, per must-be-true's log-blindness note: absence of this line does not by itself prove the north facing resolved, only that no direction is fully missing
3. [D] confirm via file inspection (not a def field — this is a loose-texture override with no def of its own) that `SauridFrillFix/Textures/Pawn/CenterFrill/CenterFrill8_north.png` exists, is a valid PNG, and its alpha channel is NOT uniformly zero (the exact defect this mod exists to fix, per its own README-style About.xml description of the donor's typo) — mirrors the alpha-decode method the mod's own justification is built on, not a log read
4. [D] confirm this mod's file loads AFTER `vanillaracesexpanded.saurid` in the resolved mod order (read `ModsConfig.xml` / RimSort's resolved order, or the live `jawa/mod_inventory` load-order listing) — order is the entire mechanism here; a misordered list makes this mod a silent no-op
X. [S] (human pass) spawn or select a saurid pawn with the "littlefoot" center frill and rotate it to face north — confirm the crest is visible from behind rather than showing the front-facing fallback; deferred to MOD_HUMAN_EXPLORATION_PASS_1
