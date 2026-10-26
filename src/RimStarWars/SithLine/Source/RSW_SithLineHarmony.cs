using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.StarWars.SithLine
{
    /// <summary>
    /// SANGUOPHAGE_KEPT_UNREACHABLE_1 — every hook the Sith line attaches, in one file. Design §2 (never recruitable),
    /// S6b (absorb backstop), §1.5 (Anzati DefOf alias), §4 (inquisitors). Prefixes and postfixes on public methods
    /// only; each does nothing unless its own setting is on. Decisions come from RSW_SithLineKernel.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class RSW_SithLineStartup
    {
        static RSW_SithLineStartup()
        {
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rsw.sithline"), typeof(RSW_SithLineStartup).Assembly, "RimMandrake.SithLine");
            ApplyLairTuning();
            if (RSW_SithLineSettings.sithBuildingsUnbuildable)
            {
                // S8: the casket inherits minifiedDef from vanilla FurnitureBase, which no XML patch on the casket's own
                // node can remove, so the reinstall route is closed here (the five bound devices lose theirs in XML).
                foreach (string n in RSW_SithLineDefs.SithBuildings)
                {
                    ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(n);
                    if (d != null)
                    {
                        d.minifiedDef = null;
                    }
                }
            }
        }

        /// <summary>The rumour's weight and refire days are QuestScriptDef fields; the settings write them at startup
        /// and whenever the settings window closes. Off writes weight 0 (the node's TestRun also refuses).</summary>
        public static void ApplyLairTuning()
        {
            QuestScriptDef q = DefDatabase<QuestScriptDef>.GetNamedSilentFail("RSW_SithLairRumour");
            if (q == null)
            {
                return;
            }
            q.rootSelectionWeight = RSW_SithLineSettings.lairRumours ? System.Math.Max(0f, RSW_SithLineSettings.lairRumourWeight) : 0f;
            q.minRefireDays = System.Math.Max(0f, RSW_SithLineSettings.lairRefireDays);
        }
    }

    public static class RSW_SithLineDefs
    {
        public static readonly string[] SithBuildings =
            { "DeathrestCasket", "Hemopump", "HemogenAmplifier", "GlucosoidPump", "PsychofluidPump", "DeathrestAccelerator" };

        private static bool resolved;
        private static GeneDef anzatiHemogenic, anzatiBloodfeeder;
        private static PawnKindDef inquisitor;

        private static void Resolve()
        {
            if (resolved)
            {
                return;
            }
            resolved = true;
            anzatiHemogenic = DefDatabase<GeneDef>.GetNamedSilentFail("RSW_AnzatiHemogenic");
            anzatiBloodfeeder = DefDatabase<GeneDef>.GetNamedSilentFail("RSW_AnzatiBloodfeeder");
            inquisitor = DefDatabase<PawnKindDef>.GetNamedSilentFail("RSW_SithInquisitor");
        }

        /// <summary>The Anzati copy that answers for a vanilla gene the engine names by DefOf, or null.</summary>
        public static GeneDef AliasFor(GeneDef vanilla)
        {
            if (vanilla == null)
            {
                return null;
            }
            Resolve();
            if (vanilla == GeneDefOf.Hemogenic)
            {
                return anzatiHemogenic;
            }
            if (vanilla == GeneDefOf.Bloodfeeder)
            {
                return anzatiBloodfeeder;
            }
            return null;
        }

        public static PawnKindDef Inquisitor { get { Resolve(); return inquisitor; } }

        /// <summary>A Sith adept is the vanilla Sanguophage xenotype, relabelled (design §0: the def cannot be deleted).</summary>
        public static bool IsSith(Pawn p)
        {
            return p != null && p.genes != null && p.genes.Xenotype == XenotypeDefOf.Sanguophage;
        }
    }

    // §2 layer 2: unwaveringly loyal, permanently (brainwipe, quest joins and every Recruitable setter are defeated).
    [HarmonyPatch(typeof(Pawn_GuestTracker), nameof(Pawn_GuestTracker.Recruitable), MethodType.Getter)]
    public static class Patch_GuestTracker_Recruitable
    {
        public static void Postfix(Pawn ___pawn, ref bool __result)
        {
            if (__result)
            {
                __result = RSW_SithLineKernel.Recruitable(true, RSW_SithLineSettings.neverRecruitable, RSW_SithLineDefs.IsSith(___pawn));
            }
        }
    }

    // §2 layer 3: enslaving makes a prisoner the colony's slave without consulting Recruitable or calling SetFaction.
    // SITHLINE_FIX_ENSLAVE_GUARD_WRONG_METHOD: the warden's enslave attempt calls TryEnslavePrisoner directly
    // (InteractionWorker_EnslaveAttempt.cs:55); EnslavePrisoner is a wrapper only the debug tool uses, and it calls
    // TryEnslavePrisoner too (GenGuest.cs:122-127), so this one patch covers both. False = "not enslaved": no letter.
    [HarmonyPatch(typeof(GenGuest), nameof(GenGuest.TryEnslavePrisoner))]
    public static class Patch_GenGuest_TryEnslavePrisoner
    {
        public static bool Prefix(Pawn prisoner, ref bool __result)
        {
            if (RSW_SithLineKernel.RefuseJoin(RSW_SithLineSettings.neverRecruitable, RSW_SithLineDefs.IsSith(prisoner), true))
            {
                Messages.Message("RSW_SithRefusesToJoin".Translate(prisoner.LabelShort), prisoner, MessageTypeDefOf.RejectInput, false);
                __result = false;
                return false;
            }
            return true;
        }
    }

    // §2 layer 4a: the recruit itself.
    [HarmonyPatch(typeof(RecruitUtility), nameof(RecruitUtility.Recruit))]
    public static class Patch_RecruitUtility_Recruit
    {
        public static bool Prefix(Pawn pawn, Faction faction)
        {
            if (RSW_SithLineKernel.RefuseJoin(RSW_SithLineSettings.neverRecruitable, RSW_SithLineDefs.IsSith(pawn), faction != null && faction.IsPlayer))
            {
                Messages.Message("RSW_SithRefusesToJoin".Translate(pawn.LabelShort), pawn, MessageTypeDefOf.RejectInput, false);
                return false;
            }
            return true;
        }
    }

    // §2 layer 4b: the backstop every join route ends in, including quest joins and mods we have not read.
    [HarmonyPatch(typeof(Pawn), nameof(Pawn.SetFaction))]
    public static class Patch_Pawn_SetFaction
    {
        public static bool Prefix(Pawn __instance, Faction newFaction)
        {
            if (RSW_SithLineKernel.RefuseJoin(RSW_SithLineSettings.neverRecruitable, RSW_SithLineDefs.IsSith(__instance),
                    newFaction != null && newFaction.IsPlayer && __instance.Faction != newFaction))
            {
                Log.Warning("[SithLine] refused to move Sith adept " + __instance.LabelShort + " into the player faction (never recruitable).");
                return false;
            }
            return true;
        }
    }

    // S6b: the absorb-xenogerm backstop for an older or dev-spawned Sith that still carries the implanter gene.
    [HarmonyPatch(typeof(GeneUtility), nameof(GeneUtility.CanAbsorbXenogerm))]
    public static class Patch_GeneUtility_CanAbsorbXenogerm
    {
        public static void Postfix(Pawn pawn, ref bool __result)
        {
            if (__result && RSW_SithLineSettings.blockXenogermAbsorb && RSW_SithLineDefs.IsSith(pawn))
            {
                __result = false;
            }
        }
    }

    // §1.5: the engine reads GeneDefOf.Hemogenic / GeneDefOf.Bloodfeeder by DefOf; an Anzati carries our copies, so the
    // copy answers for the original. No gene is aliased for a pawn that carries the original itself.
    [HarmonyPatch(typeof(Pawn_GeneTracker), nameof(Pawn_GeneTracker.HasActiveGene))]
    public static class Patch_GeneTracker_HasActiveGene
    {
        public static void Postfix(Pawn_GeneTracker __instance, GeneDef geneDef, ref bool __result)
        {
            if (__result)
            {
                return;
            }
            GeneDef alias = RSW_SithLineDefs.AliasFor(geneDef);
            if (alias != null && alias != geneDef)
            {
                __result = __instance.HasActiveGene(alias);
            }
        }
    }

    [HarmonyPatch(typeof(Pawn_GeneTracker), nameof(Pawn_GeneTracker.GetGene))]
    public static class Patch_GeneTracker_GetGene
    {
        public static void Postfix(Pawn_GeneTracker __instance, GeneDef geneDef, ref Gene __result)
        {
            if (__result != null)
            {
                return;
            }
            GeneDef alias = RSW_SithLineDefs.AliasFor(geneDef);
            if (alias != null && alias != geneDef)
            {
                __result = __instance.GetGene(alias);
            }
        }
    }

    // ANZATI_XENOGERM_WIRE_BLOODFEEDER_PRECEPT: the two xenogerm gates compare the germ's genes against
    // GeneDefOf.Bloodfeeder by reference (Xenogerm.cs:162, CompAbilityEffect_ReimplantXenogerm.cs:176, rw16 decomp), not
    // through HasActiveGene, so the alias above never reaches them. These postfixes add the Anzati copy to each check;
    // the decision is RSW_SithLineKernel.BloodfeederCopyBlocks.
    [HarmonyPatch(typeof(Xenogerm), nameof(Xenogerm.PawnIdeoDisallowsImplanting))]
    public static class Patch_Xenogerm_PawnIdeoDisallowsImplanting
    {
        public static void Postfix(Xenogerm __instance, Pawn selPawn, ref bool __result)
        {
            if (__result)
            {
                return;
            }
            GeneDef copy = RSW_SithLineDefs.AliasFor(GeneDefOf.Bloodfeeder);
            bool carries = copy != null && __instance.GeneSet != null && __instance.GeneSet.GenesListForReading.Contains(copy);
            bool gate = ModsConfig.BiotechActive && ModsConfig.IdeologyActive;
            __result = RSW_SithLineKernel.BloodfeederCopyBlocks(false, gate, carries,
                !(gate && carries) || IdeoUtility.DoerWillingToDo(HistoryEventDefOf.PropagateBloodfeederGene, selPawn));
        }
    }

    [HarmonyPatch(typeof(CompAbilityEffect_ReimplantXenogerm), nameof(CompAbilityEffect_ReimplantXenogerm.PawnIdeoCanAcceptReimplant))]
    public static class Patch_ReimplantXenogerm_PawnIdeoCanAcceptReimplant
    {
        public static void Postfix(Pawn implanter, Pawn implantee, ref bool __result)
        {
            if (!__result)
            {
                return;
            }
            GeneDef copy = RSW_SithLineDefs.AliasFor(GeneDefOf.Bloodfeeder);
            bool carries = copy != null && implanter?.genes != null && implanter.genes.Xenogenes.Any(g => g.def == copy);
            bool gate = ModsConfig.IdeologyActive;
            __result = !RSW_SithLineKernel.BloodfeederCopyBlocks(false, gate, carries,
                !(gate && carries) || IdeoUtility.DoerWillingToDo(HistoryEventDefOf.PropagateBloodfeederGene, implantee));
        }
    }

    // §4: at most one inquisitor in a Galactic Empire raid or settlement-defender group, never a trader. A postfix on
    // pawn-group generation because the campaign's GalacticEmpire.xml REPLACES the Empire Combat option lists, which
    // would erase an option added by this mod.
    [HarmonyPatch(typeof(PawnGroupMakerUtility), nameof(PawnGroupMakerUtility.GeneratePawns))]
    public static class Patch_PawnGroupMakerUtility_GeneratePawns
    {
        public static void Postfix(PawnGroupMakerParms parms, ref IEnumerable<Pawn> __result)
        {
            if (parms == null || parms.faction == null || parms.groupKind == null)
            {
                return;
            }
            RSW_SithLineKernel.GroupKind kind =
                parms.groupKind == PawnGroupKindDefOf.Combat ? RSW_SithLineKernel.GroupKind.Combat
              : parms.groupKind == PawnGroupKindDefOf.Settlement ? RSW_SithLineKernel.GroupKind.Settlement
              : parms.groupKind == PawnGroupKindDefOf.Trader ? RSW_SithLineKernel.GroupKind.Trader
              : RSW_SithLineKernel.GroupKind.Other;
            if (kind != RSW_SithLineKernel.GroupKind.Combat && kind != RSW_SithLineKernel.GroupKind.Settlement)
            {
                return;
            }
            bool add = RSW_SithLineKernel.AddInquisitor(kind, parms.faction.def == FactionDefOf.Empire, parms.points, Rand.Value,
                RSW_SithLineSettings.inquisitorRaids, RSW_SithLineSettings.inquisitorRaidChance, RSW_SithLineSettings.inquisitorRaidMinPoints,
                RSW_SithLineSettings.inquisitorDefenders, RSW_SithLineSettings.inquisitorDefenderChance,
                parms.faction.HostileTo(Faction.OfPlayer));
            if (add && RSW_SithLineDefs.Inquisitor != null)
            {
                __result = WithInquisitor(__result, parms);
            }
        }

        private static IEnumerable<Pawn> WithInquisitor(IEnumerable<Pawn> pawns, PawnGroupMakerParms parms)
        {
            bool any = false;
            foreach (Pawn p in pawns)
            {
                any = true;
                yield return p;
            }
            if (!any)
            {
                yield break; // a group that generated nobody stays empty: one lone inquisitor is not a raid
            }
            Pawn inq = null;
            try
            {
                inq = PawnGenerator.GeneratePawn(new PawnGenerationRequest(RSW_SithLineDefs.Inquisitor, parms.faction,
                    PawnGenerationContext.NonPlayer, parms.tile.Valid ? parms.tile : (PlanetTile?)null, mustBeCapableOfViolence: true, inhabitant: parms.inhabitants));
            }
            catch (System.Exception e)
            {
                Log.Warning("[SithLine] inquisitor generation failed; the group goes without one: " + e.Message);
            }
            if (inq != null)
            {
                yield return inq;
            }
        }
    }
}
