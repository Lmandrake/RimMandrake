using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.Sound;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M6 build (greentide_kit_spec.md M6, "Three-feller
    // tree fall"). "No falling-tree machinery exists" is CONFIRMED against the
    // real 1.6/Odyssey decompile by that item's own spike pass (2026-09-13,
    // zero hits for FallingTree|TreeFall) — this is built from scratch, not a
    // crib. "Build once, pay three times" per the spec's own framing: this is
    // the "once" — RM_CompCrackFall, the HediffComp_PeriodicAreaAttack hook,
    // and RM_JobGiver_GnawTreeBase all call FellTree rather than each
    // reimplementing a swath.
    //
    // Generic RM_-tier utility, not Greentide-hardcoded: works on ANY Plant,
    // tagged or not — an untagged Plant just gets the conservative Default
    // tuning below rather than a null-reference.
    public static class RM_TreeFallUtility
    {
        // Which feller triggered the fall — recorded on the utility itself
        // rather than each feller inventing its own enum, since all three
        // (and any future one) share the same three-value vocabulary the
        // kit spec names.
        public enum FallCause
        {
            Cracked,   // feller 1 — cracked from within
            Shattered, // feller 2 — shattered from the side
            Gnawed,    // feller 3 — gnawed from below
        }

        // Used for any Plant with no RM_FellableTreeExtension of its own —
        // damage-only fall, no wood drop (greenwoodDef stays null), short
        // swath. Keeps FellTree callable on an arbitrary vanilla Plant
        // without throwing.
        private static readonly RM_FellableTreeExtension Default = new RM_FellableTreeExtension
        {
            fellLength = 3,
            fallDamageRange = new FloatRange(20f, 40f),
        };

        // Static routine per the spec's own signature. dir: fall direction,
        // picked by the caller (away from the feller, or random — see each
        // feller's own comment for which it uses). cause: recorded only for
        // future hooks (e.g. a distinct fleck/sound per cause); FellTree
        // itself does not currently branch on it.
        public static void FellTree(Plant tree, Rot4 dir, FallCause cause)
        {
            if (tree == null || tree.Destroyed || !tree.Spawned)
            {
                return;
            }

            if (!RM_EnvironmentalHazardsSettings.treeFallEnabled)
            {
                return; // mod option: tree-fall mechanics disabled — single choke point for all three fellers
            }

            Map map = tree.Map;
            if (map == null)
            {
                return;
            }

            RM_FellableTreeExtension ext = tree.def.GetModExtension<RM_FellableTreeExtension>() ?? Default;
            IntVec3 origin = tree.Position;
            IntVec3 step = dir.FacingCell;
            if (step == IntVec3.Zero)
            {
                step = Rot4.Random.FacingCell;
            }

            // The tree itself is destroyed explicitly (below), not by the
            // swath's own damage pass — skip it when the swath's damage
            // loop reaches its own cell.
            bool hardwoodDropped = false;

            for (int i = 0; i < ext.fellLength; i++)
            {
                IntVec3 cell = origin + step * i;
                if (!cell.InBounds(map))
                {
                    break;
                }

                DamageCell(cell, map, tree, ext);

                if (i <= ext.heartRadius && ext.isGiantClass && ext.hardwoodDef != null && !hardwoodDropped)
                {
                    hardwoodDropped = true; // one hardwood drop per fall, at the first heart cell reached
                    DropAt(cell, map, ext.hardwoodDef, ext.hardwoodDropRange.RandomInRange);
                }

                if (ext.greenwoodDef != null && Rand.Chance(ext.greenwoodDropChancePerCell))
                {
                    DropAt(cell, map, ext.greenwoodDef, ext.greenwoodStackRange.RandomInRange);
                }

                FleckMaker.ThrowDustPuff(cell, map, ext.dustPuffScale);
            }

            (ext.crashSound ?? SoundDefOf.Roof_Collapse).PlayOneShot(SoundInfo.InMap(new TargetInfo(origin, map)));

            // Distant-crash ambience is free from this alone, per the spec —
            // a plain map-volume PlayOneShot needs no separate sustainer or
            // falloff work.
            tree.Destroy(DestroyMode.Vanish);
        }

        private static void DamageCell(IntVec3 cell, Map map, Plant tree, RM_FellableTreeExtension ext)
        {
            List<Thing> things = new List<Thing>(cell.GetThingList(map));
            float amount = ext.fallDamageRange.RandomInRange
                * System.Math.Max(0f, RM_EnvironmentalHazardsSettings.hazardDamageMultiplier);

            for (int i = 0; i < things.Count; i++)
            {
                Thing t = things[i];
                if (t == null || t.Destroyed || t == tree)
                {
                    continue;
                }

                if (amount > 0f)
                {
                    t.TakeDamage(new DamageInfo(DamageDefOf.Blunt, amount, 0f, -1f, null));
                }
            }
        }

        private static void DropAt(IntVec3 cell, Map map, ThingDef def, int count)
        {
            if (def == null || count <= 0)
            {
                return;
            }

            Thing drop = ThingMaker.MakeThing(def);
            drop.stackCount = count;
            GenPlace.TryPlaceThing(drop, cell, map, ThingPlaceMode.Near);
        }
    }
}
