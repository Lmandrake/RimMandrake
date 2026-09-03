using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// A place on the planet that somebody lives in, and the people themselves.
    ///
    /// The roster is a ThingOwner&lt;Pawn&gt; holding ACTUAL Pawn objects, never
    /// records. Names, skills, relationships, scars and memories therefore survive
    /// map destruction with no serialisation of ours, and "sell a pawn and they
    /// stay there, remembering that you sold them" falls out of the container
    /// choice rather than needing a feature.
    ///
    /// THE WORLD REMEMBERS BY CONSTRUCTION. Nobody writes "12 souls, 3 dead"
    /// anywhere. The roster simply IS the survivors, and the dead are not recorded
    /// at all -- no memorial, no ledger, no counter. The absence is the memory.
    ///
    /// TWO PLACES THIS DIVERGES FROM Caravan, WHICH IT IS OTHERWISE MODELLED ON,
    /// AND BOTH DIVERGENCES ARE LOAD-BEARING:
    ///
    /// 1. LookMode.Deep, not Caravan's LookMode.Reference. Caravan can use
    ///    Reference because its pawns are registered with WorldPawns, which
    ///    deep-saves them -- and WorldPawnGC then protects them by an explicit
    ///    `p.IsCaravanMember()` test inside GetCriticalPawnReason. A custom holder
    ///    matches none of that method's tests, so every resident would return null
    ///    and the collector would discard the whole cast between visits.
    ///    Deep-saving here means they are not world pawns at all and the collector
    ///    never sees them.
    ///
    /// 2. ShouldTickContents is false. WorldObject.DoTick walks its child holders
    ///    and calls ThingOwner.DoTick on each, skipping only owners that are a Map
    ///    or a Caravan -- a hardcoded type test we cannot join. Left alone an
    ///    off-map roster would tick: needs would fall and a cast would starve in a
    ///    box while the player was elsewhere. IThingHolderTickable is the
    ///    supported opt-out, and it is what makes "frozen until visited" true
    ///    rather than merely intended.
    /// </summary>
    public class WorldObject_Inhabited : WorldObject, IThingHolder, IThingHolderTickable
    {
        /// <summary>What the place is.</summary>
        public InhabitedPlaceDef placeDef;

        /// <summary>Who lives in it. Falls back to the place's default cast.</summary>
        public InhabitedCastDef castDef;

        /// <summary>The people. Real pawns, held off-map, frozen.</summary>
        public ThingOwner<Pawn> roster;

        /// <summary>
        /// Trade goods AND the larder. ⚠️ Held and scribed only -- nothing spawns
        /// it onto a map, so it is not yet visible, stealable or destroyable. See
        /// InhabitedPlaceDef.larder and INHABITED_STOCK_ONTO_MAP_AND_FATE_1.
        /// </summary>
        public InhabitedStock stock;

        /// <summary>What the world map reports.</summary>
        public InhabitedState state = InhabitedState.Inhabited;

        /// <summary>
        /// True once the cast has been rolled. A second visit must not re-roll a
        /// place merely because everyone in it is dead -- an emptied place is
        /// abandoned, not restocked.
        /// </summary>
        public bool castInstantiated;

        /// <summary>
        /// The thingIDNumber of everyone this place has put on the ground for the
        /// visit in progress, written by GenStep_InhabitedCast and cleared by the
        /// recall.
        ///
        /// ⭐ WHY THIS EXISTS AT ALL. Spawning the cast EMPTIES the roster -- a
        /// pawn cannot be in a ThingOwner and on a map at the same time -- so
        /// while a map exists there is no other record of who belongs here. The
        /// recall used to key on "still under a LordJob_Inhabited lord", and
        /// LordJob.ShouldRemovePawn returns true by default, so the engine drops
        /// any resident who is merely DOWNED out of the lord. Every one of them
        /// then fell through to MapDeiniter.PassPawnsToWorld, became an ordinary
        /// world pawn, and was collected by WorldPawnGC -- off the roster with no
        /// log line and indistinguishable from the recorded-dead case, which is
        /// the one thing "the roster IS the survivors" cannot survive.
        /// </summary>
        public List<int> onTheGround = new List<int>();

        private string nameInt;

        public WorldObject_Inhabited()
        {
            roster = new ThingOwner<Pawn>(this, oneStackOnly: false, LookMode.Deep);
            stock = new InhabitedStock(this);
        }

        public string Name
        {
            get => nameInt;
            set => nameInt = value;
        }

        public override string Label => nameInt ?? base.Label;

        /// <summary>Frozen until visited. See the class comment, divergence 2.</summary>
        public bool ShouldTickContents => false;

        /// <summary>How many are alive in the roster right now.</summary>
        public int SoulCount => roster?.InnerListForReading.Count(p => p != null && !p.Dead) ?? 0;

        /// <summary>Who lives here, resolved. The world object wins over the place.</summary>
        public InhabitedCastDef Cast => castDef ?? placeDef?.defaultCast;

        /// <summary>True if anyone in the cast deals.</summary>
        public bool HasTrader => Cast?.roles != null && Cast.roles.Any(r => r != null && r.trades);

        public ThingOwner GetDirectlyHeldThings()
        {
            return roster;
        }

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
            if (stock != null)
            {
                outChildren.Add(stock);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Defs.Look(ref placeDef, "placeDef");
            Scribe_Defs.Look(ref castDef, "castDef");
            Scribe_Deep.Look(ref roster, "roster", this);
            Scribe_Deep.Look(ref stock, "stock", this);
            Scribe_Values.Look(ref state, "state", InhabitedState.Inhabited);
            Scribe_Values.Look(ref castInstantiated, "castInstantiated", defaultValue: false);
            Scribe_Collections.Look(ref onTheGround, "onTheGround", LookMode.Value);
            Scribe_Values.Look(ref nameInt, "name");
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (roster == null)
                {
                    roster = new ThingOwner<Pawn>(this, oneStackOnly: false, LookMode.Deep);
                }
                if (stock == null)
                {
                    stock = new InhabitedStock(this);
                }
                if (onTheGround == null)
                {
                    onTheGround = new List<int>();
                }
            }
        }

        // ------------------------------------------------------------------
        // Instantiation. Runs ONCE, at the first map generation on this tile.
        // ------------------------------------------------------------------

        /// <summary>
        /// Roll the cast, drawing from the displaced pool BEFORE generating
        /// anybody new. That single ordering rule is the whole recurring-character
        /// effect: the six people at a trade post may be the refinery crew the
        /// player burned out two months ago, and RimWorld's own opinion system
        /// already knows what happened between them.
        ///
        /// This is not a background process. It runs at cast INSTANTIATION -- when
        /// a map generates -- which is why it does not violate "frozen until
        /// visited".
        /// </summary>
        public void InstantiateCast()
        {
            castInstantiated = true;

            InhabitedCastDef cast = Cast;
            if (cast == null || cast.roles.NullOrEmpty())
            {
                return;
            }

            List<PawnKindDef> wanted = new List<PawnKindDef>();
            for (int i = 0; i < cast.roles.Count; i++)
            {
                InhabitedRole role = cast.roles[i];
                if (role?.kind == null)
                {
                    continue;
                }
                int n = role.count.RandomInRange;
                for (int j = 0; j < n; j++)
                {
                    wanted.Add(role.kind);
                }
            }
            if (wanted.Count == 0)
            {
                return;
            }

            // Trim from the BACK, so leaders and traders -- written first -- keep
            // their places when a roll overshoots the archetype's size.
            int size = cast.castSize.RandomInRange;
            if (size > 0 && wanted.Count > size)
            {
                wanted.RemoveRange(size, wanted.Count - size);
            }

            int fromPool = 0;
            DisplacedPool pool = DisplacedPool.Current;
            if (pool != null && Faction != null)
            {
                // Fixed 2026-09-02 (opus code review): DrawInto transfers straight
                // into the roster, so there is no instant in which a drawn person
                // is out of the pool and not yet anywhere else. The old shape
                // returned a list and orphaned anyone the roster then refused --
                // not in the pool, not in a roster, not spawned, not a world pawn,
                // and therefore never saved.
                fromPool = pool.DrawInto(Faction, wanted.Count, roster);
            }

            // Authored people go to the freshly generated pawns only. Anyone drawn
            // from the pool is already somebody, and overwriting them would undo
            // the one thing the pool exists for.
            int nextCharacter = 0;

            // Fixed 2026-09-02 (opus code review): the pool fills the TAIL of
            // `wanted`, not its head. The trim above cuts from the back precisely
            // because leaders and traders are written FIRST, so the front of the
            // list is the part that must still be generated -- drawing into the
            // head silently cost a place receiving displaced people its authored
            // leader and trader pawnkinds, and misaligned every authored character
            // against the role it was written for.
            for (int i = 0; i < wanted.Count - fromPool; i++)
            {
                // Fixed 2026-09-02 (opus code review): must thread the upcoming
                // character's gender into generation itself (fixedGender), not
                // assign pawn.gender afterward in ApplyTo -- PawnGenerator picks
                // body type, head, hair/beard and name from gender AT GENERATION
                // TIME. A post-hoc reassignment changes only the label/pronouns
                // and leaves a rolled-for-the-other-gender body/head/hair, which
                // is what CharacterApplier.Spawn's own fixedGender arg already
                // avoids for its callers -- this was the one path that didn't.
                CharacterDef upcoming = (cast.characters != null && nextCharacter < cast.characters.Count)
                    ? cast.characters[nextCharacter]
                    : null;

                Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(
                    wanted[i],
                    Faction,
                    PawnGenerationContext.NonPlayer,
                    Tile,
                    forceGenerateNewPawn: true,
                    allowDead: false,
                    allowDowned: false,
                    canGeneratePawnRelations: true,
                    mustBeCapableOfViolence: false,
                    colonistRelationChanceFactor: 1f,
                    forceAddFreeWarmLayerIfNeeded: false,
                    allowGay: true,
                    allowPregnant: false,
                    allowFood: true,
                    allowAddictions: true,
                    inhabitant: true,
                    fixedGender: upcoming?.gender));
                if (p == null)
                {
                    continue;
                }
                if (upcoming != null)
                {
                    CharacterApplier.ApplyTo(p, upcoming);
                    nextCharacter++;
                }
                if (!roster.TryAdd(p, canMergeWithExistingStacks: false))
                {
                    p.Destroy();
                }
            }

            if (placeDef != null && stock != null)
            {
                stock.Fill(placeDef.larder);
                stock.Fill(placeDef.stock);
            }
        }

        // ------------------------------------------------------------------
        // The world map is the census.
        // ------------------------------------------------------------------

        public override string GetInspectString()
        {
            StringBuilder sb = new StringBuilder();
            string baseStr = base.GetInspectString();
            if (!baseStr.NullOrEmpty())
            {
                sb.AppendLine(baseStr);
            }

            List<string> parts = new List<string>();
            switch (state)
            {
                case InhabitedState.Abandoned:
                    parts.Add("InhabitedFled".Translate(SoulCount));
                    parts.Add("InhabitedStockSpoiling".Translate());
                    break;
                case InhabitedState.Looted:
                    parts.Add("InhabitedLooted".Translate());
                    break;
                case InhabitedState.Squatted:
                    parts.Add("InhabitedSquatted".Translate());
                    parts.Add("InhabitedSouls".Translate(SoulCount));
                    break;
                default:
                    parts.Add("InhabitedSouls".Translate(SoulCount));
                    if (!placeDef?.stockLabel.NullOrEmpty() ?? false)
                    {
                        parts.Add(placeDef.stockLabel);
                    }
                    if (HasTrader)
                    {
                        parts.Add("InhabitedWillTrade".Translate());
                    }
                    break;
            }
            sb.Append(string.Join(" . ", parts.ToArray()));
            return sb.ToString().TrimEndNewlines();
        }

        public override void Destroy()
        {
            // A place going away does not kill the people in it. Anyone still on
            // the roster becomes placeless and can turn up somewhere else.
            //
            // Fixed 2026-09-02 (opus code review): the guard used to also require
            // Faction != null, gating the ENTIRE rescue on it despite
            // DisplacedPool.Absorb already handling a null faction correctly. A
            // factionless place (reachable from the shipped debug action, which
            // can roll RandomNonHostileFaction(...) == null) lost every living
            // resident with no log line, directly contradicting this method's own
            // comment.
            DisplacedPool pool = DisplacedPool.Current;
            if (pool != null && roster != null && roster.Count > 0)
            {
                List<Pawn> left = roster.InnerListForReading.ToList();
                for (int i = 0; i < left.Count; i++)
                {
                    Pawn p = left[i];
                    if (p == null || p.Dead)
                    {
                        continue;
                    }
                    if (roster.Remove(p))
                    {
                        pool.Absorb(p, Faction, DisplacedReason.Fled, LabelCap);
                    }
                }
            }
            base.Destroy();
        }
    }
}
