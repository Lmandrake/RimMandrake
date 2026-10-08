using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // GREYSEA_BRINE_POOL_DEFENCE_1 — the thing a crystallised pawn becomes.
    //
    // 🔴 THE RULING THIS IMPLEMENTS, and it is a ruling, not a reading.
    // Owner, 2026-09-26, verbatim (content doc §6):
    //     "Brine pools and the creatures near them have a unique defence:
    //      they squirt out a protein shower causing ultra-rapid
    //      crystallisation around the player, freezing them in place and
    //      possibly smothering them — just like being frozen in ice already
    //      exists in the game." · "Touching a brine pool directly does the
    //      same thing." · "Loot within the pools is ultra-protected until
    //      the player figures out how to get at it."
    //
    // RULED at the bench the same day (Q1, answer (b), sheet §4d):
    //     "a crystallised pawn is ENCASED AS AN OBJECT that must be mined
    //      out — NOT a hediff."
    // One mechanism for the living and the dead, matching the sheet's
    // statuary and Odyssey's own SolidIce_Loot shape. A downed pawn can be
    // rescued; an encased one must be dug, which is what "ultra-protected"
    // asks for.
    //
    // ⛔ Do NOT "simplify" this into a movement-blocking hediff. That is
    // option (a), it was put to the owner, and he chose (b).
    //
    // ════════════════════════════════════════════════════════════════════
    // WHY IT SUBCLASSES Mineable AND NOT Building_Casket
    // ════════════════════════════════════════════════════════════════════
    // Building_Casket would hand us IThingHolder, Scribe and eject-on-destroy
    // for free — but a casket is not MINED. "Must be mined out" is the ruling
    // and Designator_Mine gates on def.mineable, which only a Mineable
    // satisfies; without it a rescue is "attack the block until it breaks",
    // which is a different verb with different pawn AI behind it. So this
    // takes Mineable as its base and re-implements the ~20 lines of
    // IThingHolder the casket would have given, which is the cheaper trade.
    //
    // MEASURED against Mineable itself: it overrides Destroy(DestroyMode) and
    // spawns its yield only on KillFinalize, and DestroyMined(pawn) routes
    // through that same Destroy. So overriding Destroy here and ejecting
    // BEFORE calling base covers every route out — mined, shot, exploded,
    // or the map being cleaned up.
    //
    // ════════════════════════════════════════════════════════════════════
    // SMOTHERING IS A TIMER ON THE JACKET, NOT A SECOND HEDIFF ON THE PAWN
    // ════════════════════════════════════════════════════════════════════
    // Sheet §4d: "Smothering is a timer on the jacket, not a second hediff."
    // So the jacket ticks RM_Smothered onto whatever it holds and nothing
    // else does; free the pawn and the hediff stops advancing and heals off.
    // A pawn left in long enough dies inside, and its corpse stays inside —
    // which IS the statuary, and is the Grey's own law that what the minerals
    // take, they keep.
    //
    // ⚠️ Deliberately NOT lethal in minutes. The rescue window is wide on
    // purpose (see the def's smotherSeverityPerRareTick): the pool is meant
    // to cost a rescue operation, not delete a colonist while the player is
    // looking at another map.
    // ════════════════════════════════════════════════════════════════════
    public class RM_Building_BrineEncasement : Mineable, IThingHolder
    {
        private ThingOwner innerContainer;
        private int heldTicks;

        // Severity added to RM_Smothered per rare tick (250 ticks) for a held
        // living pawn. At 0.004 a pawn reaches lethal severity 1.0 in ~250
        // rare ticks = 62,500 ticks = just over one in-game day. [INVENTED]
        // and owed a live look; the intent is "a rescue you have time to
        // mount, and a body you find tomorrow if you do not".
        private const float SmotherSeverityPerRareTick = 0.004f;

        public RM_Building_BrineEncasement()
        {
            innerContainer = new ThingOwner<Thing>(this, oneStackOnly: false);
        }

        public ThingOwner GetDirectlyHeldThings()
        {
            return innerContainer;
        }

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        public bool HasAnyContents => innerContainer != null && innerContainer.Count > 0;

        public Thing ContainedThing => (innerContainer != null && innerContainer.Count > 0) ? innerContainer[0] : null;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Deep.Look(ref innerContainer, "innerContainer", this);
            Scribe_Values.Look(ref heldTicks, "heldTicks", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && innerContainer == null)
            {
                innerContainer = new ThingOwner<Thing>(this, oneStackOnly: false);
            }
        }

        /// <summary>Take a spawned pawn out of the world and into this jacket.
        /// Returns false and leaves the pawn alone if anything goes wrong —
        /// losing a pawn into nowhere is the one outcome worth guarding
        /// against here (the Titanoslime's engulf has the same guard, and for
        /// the same reason).</summary>
        public bool TryEncase(Pawn p)
        {
            if (p == null || !p.Spawned || HasAnyContents)
            {
                return false;
            }
            Map map = p.Map;
            IntVec3 pos = p.Position;
            p.DeSpawn();
            if (!innerContainer.TryAdd(p))
            {
                if (map != null)
                {
                    GenSpawn.Spawn(p, pos, map);
                }
                return false;
            }
            heldTicks = 0;
            return true;
        }

        public override void TickRare()
        {
            base.TickRare();
            if (!HasAnyContents)
            {
                return;
            }
            heldTicks += 250;

            if (!(ContainedThing is Pawn p) || p.Dead)
            {
                return;
            }
            HediffDef smothered = DefDatabase<HediffDef>.GetNamedSilentFail("RM_Smothered");
            if (smothered == null)
            {
                return;
            }
            Hediff h = p.health.hediffSet.GetFirstHediffOfDef(smothered);
            if (h == null)
            {
                h = HediffMaker.MakeHediff(smothered, p);
                h.Severity = SmotherSeverityPerRareTick;
                p.health.AddHediff(h);
            }
            else
            {
                h.Severity += SmotherSeverityPerRareTick;
            }
        }

        // Every route out of the world goes through here, including
        // Mineable.DestroyMined. Eject first, then let Mineable do its yield.
        public override void Destroy(DestroyMode mode)
        {
            Map map = base.Map;
            IntVec3 pos = base.Position;
            bool ejectAlive = mode == DestroyMode.KillFinalize || mode == DestroyMode.Deconstruct;

            // Eject while still spawned (the Building_Casket order), so the holder is never
            // destroyed with a live pawn still inside it.
            if (ejectAlive && map != null && innerContainer != null && innerContainer.Count > 0)
            {
                innerContainer.TryDropAll(pos, map, ThingPlaceMode.Near);
            }

            base.Destroy(mode);

            if (innerContainer == null || innerContainer.Count == 0)
            {
                return;
            }
            if (ejectAlive && map != null)
            {
                // Retry now that the jacket's own cell is free; never silently destroy a pawn here.
                innerContainer.TryDropAll(pos, map, ThingPlaceMode.Near);
                if (innerContainer.Count > 0)
                {
                    Log.Error("[DivingInteraction] Brine jacket at " + pos + " could not eject "
                        + innerContainer.Count + " thing(s) on destruction.");
                }
                return;
            }
            innerContainer.ClearAndDestroyContents();
        }

        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo g in base.GetGizmos())
            {
                yield return g;
            }
            Gizmo sel = Building.SelectContainedItemGizmo(this, ContainedThing);
            if (sel != null)
            {
                yield return sel;
            }
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            if (!HasAnyContents)
            {
                return s;
            }
            if (!s.NullOrEmpty())
            {
                s += "\n";
            }
            s += "Encased: " + ContainedThing.LabelShortCap;
            if (ContainedThing is Pawn p && !p.Dead)
            {
                s += " (held " + (heldTicks / 2500) + "h — mine it out)";
            }
            return s;
        }
    }
}
