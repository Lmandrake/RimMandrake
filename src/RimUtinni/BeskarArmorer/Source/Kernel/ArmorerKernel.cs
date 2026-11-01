// BESKAR_ARMORER_QUEST_1: the pure rules of the quest, no Verse, so the selftest runs them with no game.
// Spec: design/RimMandrake/beskar_armorer_quest_design_2026-10-09.md sections 2.2, 3.1, 5.
using System;
using System.Collections.Generic;

namespace RimMandrake.Utinni.BeskarArmorer
{
    public static class ArmorerKernel
    {
        /// <summary>Beskar mass of one thing: stack of a beskar material, else its cost-list beskar plus its stuff count when made of
        /// beskar. Hit points never enter (spec 2.2: full mass regardless).</summary>
        public static int BeskarMass(bool thingIsBeskarMaterial, int stackCount, IEnumerable<KeyValuePair<bool, int>> costIsBeskarCount,
            bool stuffIsBeskar, int costStuffCount)
        {
            if (thingIsBeskarMaterial) return Math.Max(0, stackCount);
            int n = 0;
            if (costIsBeskarCount != null)
                foreach (KeyValuePair<bool, int> c in costIsBeskarCount)
                    if (c.Key) n += Math.Max(0, c.Value);
            if (stuffIsBeskar) n += Math.Max(0, costStuffCount);
            return n;
        }

        /// <summary>Ingots owed for melting beskarMass with 1-in-tributeOneIn kept. The fraction she has not yet paid stays in
        /// remainder, so five single raw units melted one at a time still give exactly four ingots.</summary>
        public static int MeltIngots(int beskarMass, int tributeOneIn, ref int remainder)
        {
            if (beskarMass <= 0) return 0;
            int d = Math.Max(2, tributeOneIn);
            int total = beskarMass * (d - 1) + Math.Max(0, remainder);
            remainder = total % d;
            return total / d;
        }

        /// <summary>Steel from smelting beskarCount: ceiling of count times ratio. Zero beskar gives nothing, so no slag either.</summary>
        public static int SmeltSteel(int beskarCount, float steelRatio)
        {
            if (beskarCount <= 0) return 0;
            // a Mod Settings float: 1f/3f is 0.33333334, so 300 x it is 100.000003; the slack is scaled to the count
            return (int)Math.Ceiling(beskarCount * (double)steelRatio - 1e-5 * beskarCount);
        }

        public static int SmeltSlag(int beskarCount) { return beskarCount > 0 ? 1 : 0; }

        /// <summary>The bill gate (spec 5.2 patch 1): beskar is consumed only at her forge. A smelt or destroy bill makes nothing out
        /// of the beskar, so it is not a reforge and stays open (L6 needs the smelter to take beskar gear).</summary>
        public static bool BillMayConsume(bool modEnabled, bool carriesBeskar, bool atForge, bool smeltsOrDestroys)
        {
            if (!modEnabled || !carriesBeskar) return true;
            return atForge || smeltsOrDestroys;
        }

        public static bool MayWorkForge(bool modEnabled, bool atForge, bool isArmorer)
        {
            return !modEnabled || !atForge || isArmorer;
        }

        /// <summary>Route 1 trigger, spec 3.1.</summary>
        public static bool RouteOneFires(bool routeEnabled, bool isBlackstarMandalorian, bool alive, bool wasPlayerPrisoner,
            bool revealed, bool lost, bool routeQuestRunning)
        {
            return routeEnabled && isBlackstarMandalorian && alive && wasPlayerPrisoner && !revealed && !lost && !routeQuestRunning;
        }

        /// <summary>Route 2 offer gate, spec 4.2.</summary>
        public static bool RouteTwoOffers(bool routeEnabled, float daysPassed, float earliestDay, bool revealed, bool lost, bool routeQuestRunning)
        {
            return routeEnabled && daysPassed >= earliestDay && !revealed && !lost && !routeQuestRunning;
        }
    }
}
