using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    //   <ThingDef ParentName="AnimalThingBase">
    //     <defName>RUT_WardenMother</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.CompProperties_TerritorialAnchor">
    //         <dutyDef>RM_AnchorGuard</dutyDef>
    //         <anchorRadius>12</anchorRadius>
    //       </li>
    //     </comps>
    //   </ThingDef>
    public class CompProperties_TerritorialAnchor : CompProperties
    {
        // A DutyDef the pawn's own ThinkTreeDef actually reads (must gate
        // its JobGivers on mindState.duty existing) — the same PawnDuty
        // seam vanilla's hive defenders use. XML-configurable rather than
        // hardcoded so any future anchored creature reuses this comp.
        public DutyDef dutyDef;

        public float anchorRadius = 12f;

        public CompProperties_TerritorialAnchor()
        {
            compClass = typeof(RM_CompTerritorialAnchor);
        }
    }

    // MIASMA_MECHANICS_1 M6 spike (miasma_kit_spec.md). "Stationary +
    // lethal in reach" for the warden mothers.
    //
    // Seam confirmed against the live 1.6 decompile — closing the spec's
    // named ❓ ("cleanest seam: a ThinkTree subtree vs a wander-radius
    // override"). It is neither exactly: vanilla's own hive defenders use
    // Verse.AI.PawnDuty (focus + radius fields, Verse.AI/PawnDuty.cs) read
    // by two JobGiver overrides:
    //   RimWorld/JobGiver_HiveDefense.cs   : JobGiver_AIFightEnemies
    //     GetFlagPosition => pawn.mindState.duty.focus.Thing (the Hive)
    //     GetFlagRadius   => pawn.mindState.duty.radius
    //   RimWorld/JobGiver_WanderHive.cs    : JobGiver_Wander
    //     GetWanderRoot   => same Hive, wanderRadius 7.5
    // GetFlagPosition/GetFlagRadius are `protected virtual` on the abstract
    // base RimWorld/JobGiver_AIFightEnemy.cs:42,47 — a real, overridable
    // seam, not a guess. This comp reproduces the same PawnDuty wiring
    // generically (the anchor is whatever Thing SetAnchor() is given —
    // RUT_CrecheMarker in the full build — rather than a Hive), and
    // RM_JobGiver_AnchorDefense / RM_JobGiver_AnchorWander below crib the
    // two vanilla JobGivers' overrides exactly.
    //
    // SPIKE SCOPE: this proves the comp + JobGiver seam compiles and
    // matches the confirmed vanilla pattern. NOT done here, owed to M6's
    // full build: the RM_GenStep_PlacedSetPieces scatterer, the
    // RUT_CrecheMarker building, and wiring a ThinkTreeDef for
    // RUT_WardenMother that actually calls these two JobGivers (a
    // PawnKindDef/ThinkTreeDef content decision, not an engine-fact
    // question this spike needs to resolve). Absent an explicit
    // SetAnchor() call from that GenStep, PostSpawnSetup anchors on the
    // pawn's own spawn cell as a safe, real, compiling default.
    public class RM_CompTerritorialAnchor : ThingComp
    {
        private LocalTargetInfo anchor = LocalTargetInfo.Invalid;
        private bool anchorSet;

        public CompProperties_TerritorialAnchor Props => (CompProperties_TerritorialAnchor)props;

        public void SetAnchor(LocalTargetInfo focus)
        {
            anchor = focus;
            anchorSet = true;
            ApplyDuty();
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);

            if (!anchorSet)
            {
                Pawn pawn = parent as Pawn;
                if (pawn != null)
                {
                    anchor = new LocalTargetInfo(pawn.Position);
                    anchorSet = true;
                }
            }

            ApplyDuty();
        }

        private void ApplyDuty()
        {
            Pawn pawn = parent as Pawn;
            CompProperties_TerritorialAnchor props = Props;
            if (pawn == null || !anchorSet || props == null)
            {
                return;
            }

            if (props.dutyDef == null)
            {
                Log.WarningOnce(
                    "[RM EnvironmentalHazards] CompProperties_TerritorialAnchor on " + parent.def.defName
                    + " has no dutyDef; the anchor cannot be assigned.",
                    parent.def.shortHash ^ 0x5A19);
                return;
            }

            pawn.mindState.duty = new PawnDuty(props.dutyDef, anchor, props.anchorRadius);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_TargetInfo.Look(ref anchor, "anchor", LocalTargetInfo.Invalid);
            Scribe_Values.Look(ref anchorSet, "anchorSet", false);
        }

        // MIASMA_MECHANICS_1 M6 build, §8 "everything living remembers it":
        // "killing a warden ... flips the site's marker to despoiled."
        // Notify_Killed is the real, dedicated vanilla seam for exactly
        // this (Verse/ThingComp.cs — distinct from PostDestroy, which also
        // fires on ordinary despawn/vanish; this one fires only when
        // Pawn.Kill() actually kills the parent). Deliberately generic:
        // this class never references RUT_CrecheMarker or any Miasma type
        // by name — it only notifies whatever comps the anchor Thing
        // itself carries that opt in via IRM_AnchorDeathListener, so
        // Sump's own future anchored set-piece (S3, same shared
        // RM_GenStep_PlacedSetPieces prerequisite) gets the identical
        // "tell my anchor point I died" behavior for free if it anchors to
        // a Thing rather than a bare cell.
        public override void Notify_Killed(Map prevMap, DamageInfo? dinfo = null)
        {
            base.Notify_Killed(prevMap, dinfo);

            if (!anchor.HasThing || !(anchor.Thing is ThingWithComps anchorThing))
            {
                return; // anchored to a bare cell (no markerDef configured) — nothing to notify
            }

            List<ThingComp> comps = anchorThing.AllComps;
            for (int i = 0; i < comps.Count; i++)
            {
                (comps[i] as IRM_AnchorDeathListener)?.Notify_AnchorPawnKilled(parent as Pawn);
            }
        }
    }

    // The generic death-notification contract RM_CompTerritorialAnchor
    // calls on whatever Thing it is anchored to (see Notify_Killed above).
    // Kept independent of any specific marker class so this file — the
    // shared anchor mechanism — never needs to know RUT_CrecheMarker (or
    // any future Sump equivalent) exists.
    public interface IRM_AnchorDeathListener
    {
        void Notify_AnchorPawnKilled(Pawn anchoredPawn);
    }

    // Crib: RimWorld/JobGiver_HiveDefense.cs, generalized off Hive onto
    // whatever Thing the pawn's own PawnDuty.focus names.
    public class RM_JobGiver_AnchorDefense : JobGiver_AIFightEnemies
    {
        protected override IntVec3 GetFlagPosition(Pawn pawn)
        {
            if (pawn.mindState.duty != null && pawn.mindState.duty.focus.IsValid)
            {
                return pawn.mindState.duty.focus.Cell;
            }
            return pawn.Position;
        }

        protected override float GetFlagRadius(Pawn pawn)
        {
            if (pawn.mindState.duty != null && pawn.mindState.duty.radius > 0f)
            {
                return pawn.mindState.duty.radius;
            }
            return base.GetFlagRadius(pawn);
        }
    }

    // Crib: RimWorld/JobGiver_WanderHive.cs, same generalization.
    public class RM_JobGiver_AnchorWander : JobGiver_Wander
    {
        public RM_JobGiver_AnchorWander()
        {
            wanderRadius = 7.5f;
            ticksBetweenWandersRange = new IntRange(125, 200);
        }

        protected override IntVec3 GetWanderRoot(Pawn pawn)
        {
            if (pawn.mindState.duty != null && pawn.mindState.duty.focus.IsValid)
            {
                return pawn.mindState.duty.focus.Cell;
            }
            return pawn.Position;
        }
    }
}
