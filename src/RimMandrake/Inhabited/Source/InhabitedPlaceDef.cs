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
    /// WIRED. InhabitedFateWorker.DetectCause turns each value below into a real
    /// test on a live map, MapComponent_InhabitedWatch runs it during the visit,
    /// and InhabitedFateWorker.Apply acts on it at teardown -- the cast goes to
    /// the DisplacedPool and the place reads Abandoned or Looted from then on.
    ///
    /// ⏱️ CAUSE AND CONSEQUENCE ARE SEPARATED BY THE VISIT. Nobody walks off the
    /// map in front of the player; the place is empty the next time they come.
    /// InhabitedFateWorker's class comment has the engine reason (Pawn.ExitMap
    /// hands a non-player pawn to WorldPawns, and WorldPawnGC then eats the
    /// roster) and names what a visible walk-off would take.
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

    /// <summary>
    /// What the world map reports about a place. Drawn by
    /// WorldObject_Inhabited.GetInspectString.
    ///
    /// Written in three places: GenStep_InhabitedCast and Patch_MapRemoval both
    /// set Abandoned when nobody is left, and InhabitedFateWorker.Apply picks
    /// Abandoned or Looted by whether the larder survived.
    ///
    /// ⚠️ Squatted is DECLARED, NOT WRITTEN. Nothing sets it, because nothing in
    /// this mod yet moves a second party into an emptied place -- it is the state
    /// a later "somebody else has taken it over" feature will write, and inventing
    /// a trigger for it here would have been a guess.
    /// </summary>
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
