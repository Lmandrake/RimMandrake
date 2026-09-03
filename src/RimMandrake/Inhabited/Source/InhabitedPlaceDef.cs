using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// What could end a cast. The default is nothing: they live here.
    /// Flight is CAUSED, never scheduled -- every value below names a cause,
    /// not a timer.
    ///
    /// 🔴 DECLARED, NOT WIRED. `InhabitedPlaceDef.fate` is the only field of this
    /// type and no code in this mod reads it, so every value below is at present a
    /// statement of intent that changes nothing in play. Making a cause fire is
    /// INHABITED_STOCK_ONTO_MAP_AND_FATE_1.
    /// </summary>
    public enum InhabitedFate
    {
        /// <summary>Nothing ends them. The default and the great majority.</summary>
        Resident,
        /// <summary>They break and go if the player menaces them. Costs goodwill,
        /// and hostility ends only at goodwill 0, so a fright is not a thing a
        /// gift repairs.</summary>
        FleeIfThreatened,
        /// <summary>A gravship coming out of the sky is enough. The ship is a
        /// presence in the world, not transport.</summary>
        FleeOnArrival,
        /// <summary>A genuine caravan passing through. The rare case.</summary>
        Transient
    }

    /// <summary>What the world map reports about a place.</summary>
    public enum InhabitedState
    {
        Inhabited,
        Abandoned,
        Looted,
        Squatted
    }

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
        /// 🔴 WHAT THIS TABLE DOES TODAY, AND IT IS LESS THAN THAT PARAGRAPH USED
        /// TO CLAIM. `WorldObject_Inhabited.InstantiateCast` pours this table into
        /// the place's `InhabitedStock`, which is scribed with the world object and
        /// nothing else. NOTHING spawns those things onto a generated map and
        /// nothing collects them back at teardown, so the larder is BOOKKEEPING,
        /// not scenery: it cannot be seen, stolen or burned, and the `fate` field
        /// above is read by no code in this mod at all. "Burn the granary and they
        /// leave, with no new code" describes the intended design, not the build --
        /// spawning stock and firing FATE off it is
        /// INHABITED_STOCK_ONTO_MAP_AND_FATE_1.
        /// </summary>
        public List<ThingDefCountClass> larder = new List<ThingDefCountClass>();

        /// <summary>Trade goods held for a cast that contains a dealer.</summary>
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
