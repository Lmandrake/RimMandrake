# custom_patches/ — self-authored compat patches (last resort)

Local RimWorld mod holding **only** patches we author for the gravship campaign.
Load it **last** in the mod order (RimSort) so it sees the final state of every
def it touches.

## Standing preference: avoid patches when possible

Patches are a debugging tax — a mistyped xpath fails **silently**, load order
can move the target out from under you, and VEF/VFE updates rename defs between
versions. So the rule for this folder is:

1. **Prefer an existing maintained mod** that does the same thing. Only author a
   patch when no clean mod exists (or the mod is stale on the current game
   version).
2. **Wrap every patch in `PatchOperationConditional`** whose test also checks the
   target isn't already in the desired state. That turns "target moved / already
   handled" from a red error into a silent no-op.
3. **Never guess a defName or field.** Every target here was read from the
   actual mod source before writing the patch.
4. **Test in a dev-mode throwaway world** and read `Player.log` before trusting
   a patch in the campaign save.

## Contents

### Jawa_Patches/ — the local mod
`packageId: mandrake.jawa.patches`. Currently holds **no patches** (the
`Patches/` dir is empty). Kept as ready infrastructure for future patches.

**Retired patch (deleted 2026-08-03):** `Patches/Slingshot_Buildable.xml` made
VFE-Ancients' `VFEA_AncientSupplySlingshot` buildable. Deleted because the entire
**Ancients** line was dropped from the campaign — VFE-Ancients is deprecated
(1.5-capped) and its 1.6 successor VQE-Ancients removed the Supply Slingshot. See
required_mods.md "ANCIENTS — DROPPED ENTIRELY". Do not resurrect it.

**Next intended patch (not yet authored):** the **universal-buyer TraderKindDef
buy-filter** patch — widen each `TraderKindDef`'s buy-side filter so any trader
buys basically anything (the "Star Wars merchant obsession" ask). Author it here,
wrapped in `PatchOperationConditional`, defNames confirmed from installed source.

## Install / test

Symlink or copy `Jawa_Patches/` into RimWorld's `Mods/` folder (or point
RimSort at it as a local mod), enable it, place it **last**. When a patch is
present, test it in a dev-mode throwaway world and read `Player.log` for patch
errors before trusting it in the campaign save.
