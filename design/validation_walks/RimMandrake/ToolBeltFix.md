# ToolBeltFix — validation walk
subject: src/RimMandrake/ToolBeltFix  (packageId mandrake.rm.toolbeltfix)
deps: VanillaExpanded.VAEAccessories (hard modDependency, "Vanilla Apparel Expanded — Accessories" — this mod must load AFTER it; loose-PNG override, order-dependent)
list: full   # third-party donor mod is not in the minimal list
status-hint: one loose PNG replacing a donor-mod worn-apparel texture that ships present-but-fully-transparent (256x256, alpha max 0), so a colonist wearing the tool belt and facing west renders invisible.

## must be true
- Ships exactly one file, `ToolBeltFix/Textures/Things/Apparel/ToolBelt/ToolBelt_west.png` (256x256, 10,502 bytes per About.xml) — the donor's own `ThingDef VAEA_Apparel_ToolBelt` (`VanillaExpanded.VAEAccessories`'s `1.6/Defs/ThingDefs_Misc/Apparel_Utility.xml:531,557,577`) has both `texPath` and `wornGraphicPath` at `Things/Apparel/ToolBelt/ToolBelt`, so `_west` at that stem is what this mod overrides.
- The replacement is the donor's own `_east` file flipped horizontally — verified against the donor by matching alpha histograms bucket-for-bucket (0 fully transparent, 54,300 below alpha 128, 10,980 at alpha ≥250 over the 65,536-pixel canvas), NOT a freshly drawn or cleaned-up image (About.xml "HOW OURS WAS BUILT AND VERIFIED").
- The generator, `ToolBeltFix/Source/mirror_toolbelt_west.py`, refuses to run if the donor's `_east` is itself under 1% covered — a guard against silently mirroring a blank into a permanent one.
- No log line can prove the fix landed — a present-but-transparent PNG is a fully successful load by every engine measure; "Failed to find any textures at" never fires (About.xml: "No log line is possible").
- Because this mod loads AFTER the donor and both ship loose PNGs, ContentFinder's last-mod-wins resolution must pick this mod's `_west` over the donor's blank one.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.toolbeltfix" and no XML error naming this mod (ships no XML/Defs at all, only a loose PNG)   # load-time
2. [D] confirm via file inspection (no def of its own — pure loose-texture override) that `ToolBeltFix/Textures/Things/Apparel/ToolBelt/ToolBelt_west.png` exists, is a valid PNG, and its alpha channel is NOT uniformly zero — the exact defect being fixed
3. [D] confirm this mod's file loads AFTER `VanillaExpanded.VAEAccessories` in the resolved mod order (`ModsConfig.xml` / live `jawa/mod_inventory` load-order listing) — order is the entire mechanism; a misordered list makes this mod a silent no-op
4. [B] `jawa/spawn_pawn`, then `jawa/inventory_transfer {mode: "add", ...}` a `VAEA_Apparel_ToolBelt` item onto the pawn (or `rimworld/right_click_cell` → wear order), rotate the pawn to face west, then use `jawa/inspect_string` on the pawn to confirm the apparel is worn — this proves the def resolves and equips, though whether the WEST-FACING TEXTURE actually renders is a visual property no bridge tool can assert (see [S] line)
X. [S] (human pass) with the tool belt worn and the pawn facing west, confirm the belt is visible rather than invisible — deferred to MOD_HUMAN_EXPLORATION_PASS_1
