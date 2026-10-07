using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// A PLACE archetype and its parameter table -- what the place IS, as opposed
    /// to who lives there.
    ///
    /// Section 1.1 of the design: most of the 36 named templates in
    /// LIVING_NPC_TEMPLATES.md are one machine with different numbers. The numbers
    /// live here; the machine lives in C#. Expect six to eight real archetypes.
    ///
    /// Type name is deliberately NOT the bare `PlaceDef` the queue item wrote --
    /// see InhabitedCastDef for why.
    /// </summary>
    public class InhabitedPlaceDef : Def
    {
        /// <summary>Who lives here by default. A world object may override it.</summary>
        public InhabitedCastDef defaultCast;

        /// <summary>What could end them. Default: nothing.</summary>
        public InhabitedFate fate = InhabitedFate.Resident;

        /// <summary>How far from the worksite a resident wanders by day.</summary>
        public float workRadius = 14f;

        /// <summary>How far from the barracks a resident strays at night.</summary>
        public float homeRadius = 10f;

        /// <summary>Hour the cast turns in. Local time at the place's own tile.</summary>
        public int sleepStartHour = 22;

        /// <summary>Hour the cast gets up.</summary>
        public int wakeHour = 6;

        /// <summary>
        /// SUSTENANCE IS PRESENT, NOT PRODUCED, and that is not an oversight.
        ///
        /// NPCs cannot farm -- three independent shipped walls, the worst being
        /// WorkGiver_GrowerHarvest.ShouldSkip, which opens
        /// `if (pawn.GetLord() != null) return true;`, so ANY lorded pawn skips
        /// harvest, even a colonist. Fighting that is not worth it.
        ///
        /// So a place has a mess and a paste vat, a farmstead a granary, a Tusken
        /// camp a herd.
        ///
        /// WHAT THIS TABLE DOES. `WorldObject_Inhabited.InstantiateCast` pours it
        /// into the place's `InhabitedStock` once, `GenStep_InhabitedStock` (order
        /// 910) drops the whole holder onto every generated map inside the
        /// composed district, and `Patch_MapRemoval` takes back whatever is still
        /// there when the player leaves. So the larder IS scenery: it can be seen,
        /// eaten, stolen and burned, and "burn the granary and they leave"
        /// is the `fate` field above reading the very same goods.
        ///
        /// ⚠️ THESE ARE COUNTS OF A STACK, NOT A DAILY RATION. Nothing replenishes
        /// them and nothing consumes them on a schedule -- what comes back off the
        /// map is what the place has next time. A place the player strips stays
        /// stripped.
        /// </summary>
        public List<ThingDefCountClass> larder = new List<ThingDefCountClass>();

        /// <summary>Trade goods held for a cast that contains a dealer. ⚖️ Gated
        /// on exactly that: WorldObject_Inhabited.FillStock skips this table when
        /// no role in the cast has `trades`, so a place with nobody to sell is not
        /// left sitting on merchandise the player can walk off with.</summary>
        public List<ThingDefCountClass> stock = new List<ThingDefCountClass>();

        /// <summary>Short phrase for the census line: "oil", "water", "salvage".</summary>
        public string stockLabel;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (sleepStartHour < 0 || sleepStartHour > 23)
            {
                yield return "sleepStartHour out of 0-23: " + sleepStartHour;
            }
            if (wakeHour < 0 || wakeHour > 23)
            {
                yield return "wakeHour out of 0-23: " + wakeHour;
            }
            if (workRadius <= 0f || homeRadius <= 0f)
            {
                yield return "a radius is zero or negative; residents would have nowhere to be";
            }
        }
    }
}
