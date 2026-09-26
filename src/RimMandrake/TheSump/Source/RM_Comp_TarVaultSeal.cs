using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.TheSump
{
    // SUMP_TAR_VAULT_1 — "the tar larder, and extraction as the solvent's
    // economy". Owner ruling verbatim (typed, question card): "it requires
    // solvents to extract things or else they are rendered useless. So
    // extraction is a solvent based economic need."
    //
    // Distinct from RM_Comp_TarCoatingSource/RM_TarCoatingUtility
    // (mandrake.rm.environmentalhazards, SUMP_TAR_NASTINESS_1) — that pair
    // splashes tar FILTH onto terrain (a source coating the ground around
    // it). This is the opposite direction: a storage building that seals
    // items ALREADY stored in it against rot, and gates getting them back
    // out behind consuming a solvent. No shared code between the two; they
    // solve unrelated problems that happen to share the word "tar".
    //
    // Lives in the SUMP-OWN assembly (RimMandrake.TheSump), not the shared
    // EnvironmentalHazards one, because EnvironmentalHazards is contended by
    // a sibling FOUNDRY pass today — this mechanism is Sump-specific (a
    // single building type) and does not need to be shared with Greentide/
    // Miasma/etc. the way the tar-coating and tarred-hediff mechanisms do.
    //
    // Mechanism, per the item's own spec line "rot-stop is a container comp
    // (vanilla-adjacent)": CompRottable.disabled is a real public field
    // (RimWorld/CompRottable.cs, read via RimSage this pass) that makes
    // CompRottable.Active false, which is CompRottable's OWN top-of-method
    // guard in TickInterval — so setting it true is not a workaround, it is
    // the vanilla "this thing does not rot right now" switch (the same one
    // CompHatcher's disableIfHatcher path already uses). No RotProgress
    // bookkeeping is needed at all — vanilla's own tick simply does nothing
    // while disabled is true, and resumes exactly where it left off the
    // instant it is false again.
    //
    // "Sealing is cheap" (spec) needs no seal action of its own: ordinary
    // vanilla hauling AI carries a matching item into this building's
    // storage cells (Building_Storage/StorageShelfBase, unmodified) the
    // moment its filter allows it, exactly like a shelf. This comp's own
    // job starts the instant that item is physically present in
    // slotGroup.HeldThings — no bill, no work order.
    public class CompProperties_TarVaultSeal : CompProperties
    {
        // How often the vault re-scans its own storage cells for newly
        // arrived / departed items. Short enough that a freshly-hauled-in
        // item is sealed well within one vanilla CompRottable tick
        // (TickerType.Rare = every 250 ticks) so it never accrues a
        // measurable sliver of rot before the seal takes hold.
        public int scanIntervalTicks = 60;

        public CompProperties_TarVaultSeal()
        {
            compClass = typeof(RM_Comp_TarVaultSeal);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (parentDef.thingClass == null || !typeof(Building_Storage).IsAssignableFrom(parentDef.thingClass))
            {
                yield return "CompProperties_TarVaultSeal is on " + parentDef.defName
                           + ", whose thingClass is not Building_Storage (or a subclass) — this comp reads "
                           + "slotGroup.HeldThings and would do nothing.";
            }
        }
    }

    public class RM_Comp_TarVaultSeal : ThingComp
    {
        public CompProperties_TarVaultSeal Props => (CompProperties_TarVaultSeal)props;

        // Persisted so a save/reload can tell "already sealed, do not
        // re-forbid every scan" apart from "just arrived", and so an item
        // that leaves without going through ExtractOne (destroyed some
        // other way, or the vault itself is deconstructed) still gets its
        // rot resumed rather than staying frozen forever as an orphaned
        // reference.
        private List<Thing> sealedThings = new List<Thing>();

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Collections.Look(ref sealedThings, "sealedThings", LookMode.Reference);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && sealedThings == null)
            {
                sealedThings = new List<Thing>();
            }
        }

        public override void CompTick()
        {
            base.CompTick();

            if (!RM_TheSumpSettings.tarVaultEnabled)
            {
                return;
            }

            if (Props.scanIntervalTicks <= 0 || Find.TickManager.TicksGame % Props.scanIntervalTicks != 0)
            {
                return;
            }

            Scan();
        }

        private void Scan()
        {
            if (!parent.Spawned || !(parent is Building_Storage storage))
            {
                return;
            }

            List<Thing> present = storage.slotGroup.HeldThings.ToList();

            // Freshly arrived: seal it (freeze rot, forbid ordinary hauling
            // so a passing colonist cannot simply re-haul it out and defeat
            // the whole solvent gate).
            for (int i = 0; i < present.Count; i++)
            {
                Thing t = present[i];
                if (sealedThings.Contains(t))
                {
                    continue;
                }

                sealedThings.Add(t);
                Seal(t);
            }

            // No longer present (extracted through ExtractOne, hauled out
            // some other way, or destroyed): stop tracking it. ExtractOne
            // itself already unseals the CLEAN path before the item leaves
            // slotGroup.HeldThings; this is the safety net for every other
            // way a sealed thing can stop being here (deconstruction,
            // debug spawn removal, a mod interaction this pass did not
            // anticipate) — a Thing this comp cannot re-find is either
            // destroyed already (Unseal no-ops safely on a dead Thing,
            // Destroyed guarded below) or no longer this building's
            // concern either way.
            for (int i = sealedThings.Count - 1; i >= 0; i--)
            {
                Thing t = sealedThings[i];
                if (t != null && !t.Destroyed && present.Contains(t))
                {
                    continue;
                }

                sealedThings.RemoveAt(i);
                if (t != null && !t.Destroyed)
                {
                    Unseal(t);
                }
            }
        }

        private static void Seal(Thing t)
        {
            if (!(t is ThingWithComps twc))
            {
                return;
            }

            CompRottable rot = twc.TryGetComp<CompRottable>();
            if (rot != null)
            {
                rot.disabled = true;
            }

            // Not every haulable ThingDef ships CompForbiddable (confirmed
            // via RimSage this pass that the vanilla helper itself no-ops
            // safely without it) — where it is missing, the item is still
            // rot-frozen but can be hand-hauled away early. Flagged, not
            // fixed: a real risk-of-abuse only for whatever small slice of
            // haulable ThingDefs skip that comp, and no such gap is known
            // in the three categories this vault targets (food, corpses,
            // leather all carry it in the live def dump).
            CompForbiddable forbid = twc.TryGetComp<CompForbiddable>();
            if (forbid != null)
            {
                forbid.Forbidden = true;
            }
        }

        private static void Unseal(Thing t)
        {
            if (!(t is ThingWithComps twc))
            {
                return;
            }

            CompRottable rot = twc.TryGetComp<CompRottable>();
            if (rot != null)
            {
                rot.disabled = false;
            }

            CompForbiddable forbid = twc.TryGetComp<CompForbiddable>();
            if (forbid != null)
            {
                forbid.Forbidden = false;
            }
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra())
            {
                yield return g;
            }

            if (parent.Faction != Faction.OfPlayer)
            {
                yield break;
            }

            yield return new Command_Action
            {
                defaultLabel = "Extract from tar vault",
                defaultDesc = "Pull a sealed item back out. With a tar solvent in "
                             + "stock (weak or strong — one unit is consumed), it "
                             + "comes out exactly as it went in. With none on hand, "
                             + "the tar keeps it: the item comes out ruined and "
                             + "worthless.",
                icon = TexCommand.RearmTrap,
                action = OpenExtractMenu,
            };
        }

        private void OpenExtractMenu()
        {
            if (!(parent is Building_Storage storage) || !parent.Spawned)
            {
                return;
            }

            List<Thing> sealedPresent = storage.slotGroup.HeldThings
                .Where(t => sealedThings.Contains(t))
                .ToList();

            if (sealedPresent.Count == 0)
            {
                Messages.Message("Nothing sealed in this vault.", parent, MessageTypeDefOf.RejectInput, historical: false);
                return;
            }

            List<FloatMenuOption> options = new List<FloatMenuOption>();
            foreach (Thing t in sealedPresent)
            {
                Thing target = t;
                options.Add(new FloatMenuOption(
                    "Extract " + target.LabelCap,
                    () => ExtractOne(target)));
            }

            Find.WindowStack.Add(new FloatMenu(options));
        }

        // Public: consumes 1 solvent (weak or strong, either accepted —
        // same "either cures it" posture RUT_Tarred_Surgery.xml already
        // uses for the pawn-hediff cure) if the map has any, and unseals
        // the target unchanged. With none in stock, the target is
        // destroyed and replaced with RUT_TarRuinedGoods at the same
        // stack count in the same spot — "the tarred variant comes out"
        // (item spec's own words), a single uniform ruined stand-in rather
        // than per-category spoilage, since food/corpse/hide each ruin
        // differently and the spec gives no per-type numbers to build
        // against.
        public void ExtractOne(Thing target)
        {
            if (target == null || target.Destroyed || !sealedThings.Contains(target))
            {
                return;
            }

            Map map = parent.Map;
            IntVec3 pos = target.Position;

            Thing solvent = FindAnySolvent(map);
            sealedThings.Remove(target);

            if (solvent != null)
            {
                solvent.SplitOff(1).Destroy();
                Unseal(target);
                Messages.Message(
                    target.LabelCap + " comes out of the tar vault clean.",
                    new TargetInfo(pos, map), MessageTypeDefOf.PositiveEvent, historical: false);
                return;
            }

            int count = target.stackCount;
            Unseal(target);
            target.Destroy();

            ThingDef ruinedDef = RuinedGoodsDef;
            if (ruinedDef != null && map != null)
            {
                Thing ruined = ThingMaker.MakeThing(ruinedDef);
                ruined.stackCount = Mathf.Max(1, count);
                GenPlace.TryPlaceThing(ruined, pos, map, ThingPlaceMode.Near);
            }

            Messages.Message(
                "No tar solvent on hand — the vault's contents come out ruined.",
                new TargetInfo(pos, map), MessageTypeDefOf.NegativeEvent, historical: false);
        }

        // Administrative consumption, same posture RUT_Tarred_Surgery.xml's
        // recipe ingredient search already uses (a bill's ingredients are
        // consumed once hauled to the bench, not walked-for mid-job): the
        // nearest available solvent stack anywhere on the map is spent, not
        // one specifically pre-hauled to this building. Building a real
        // two-stage haul-then-extract job (carry solvent to the vault
        // first) is real future work, flagged rather than guessed at this
        // pass — this pass's own verify only promises "solvent consumption
        // scales per item", which this delivers.
        private static Thing FindAnySolvent(Map map)
        {
            if (map == null)
            {
                return null;
            }

            ThingDef weak = WeakSolventDef;
            ThingDef strong = StrongSolventDef;
            if (weak == null && strong == null)
            {
                return null;
            }

            foreach (Thing t in map.listerThings.AllThings)
            {
                if (t.stackCount <= 0)
                {
                    continue;
                }

                if (t.def == weak || t.def == strong)
                {
                    return t;
                }
            }

            return null;
        }

        // Deliberately NOT a [DefOf] class. RUT_WeakTarSolvent/
        // RUT_StrongTarSolvent/RUT_TarRuinedGoods are RUT-tier (this
        // campaign's own UtinniPatches, SUMP_TAR_NASTINESS_1's own build) —
        // this comp's own assembly is RM-tier (mandrake.rm.thesump, no
        // Utinni dependency in About.xml, same "no hard campaign
        // dependency" posture every RM_ mod in this repo keeps). A
        // [DefOf]'s static ctor logs a startup error for every defName it
        // cannot resolve; GetNamedSilentFail degrades silently instead —
        // with UtinniPatches absent, solvent is simply never found (every
        // extraction ruins, no crash, no log spam). Re-tiering these three
        // defs into an RM_-tier def so a standalone RM_TheSump install has
        // a real solvent of its own is SUMP_UTINNI_LAYER_1's retier, not
        // this pass's — flagged in this item's own build note.
        private static ThingDef weakSolventDef;
        private static ThingDef strongSolventDef;
        private static ThingDef ruinedGoodsDef;
        private static bool resolvedDefs;

        private static ThingDef WeakSolventDef { get { ResolveDefsOnce(); return weakSolventDef; } }
        private static ThingDef StrongSolventDef { get { ResolveDefsOnce(); return strongSolventDef; } }
        private static ThingDef RuinedGoodsDef { get { ResolveDefsOnce(); return ruinedGoodsDef; } }

        private static void ResolveDefsOnce()
        {
            if (resolvedDefs)
            {
                return;
            }

            weakSolventDef = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_WeakTarSolvent");
            strongSolventDef = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_StrongTarSolvent");
            ruinedGoodsDef = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_TarRuinedGoods");
            resolvedDefs = true;
        }
    }
}
