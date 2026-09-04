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
    public class WorldObject_Inhabited : MapParent, IThingHolder, IThingHolderTickable
    {
        /// <summary>What the place is.</summary>
        public InhabitedPlaceDef placeDef;

        /// <summary>Who lives in it. Falls back to the place's default cast.</summary>
        public InhabitedCastDef castDef;

        /// <summary>The people. Real pawns, held off-map, frozen.</summary>
        public ThingOwner<Pawn> roster;

        /// <summary>
        /// Trade goods AND the larder, off-map. Real Things: GenStep_InhabitedStock
        /// puts them on the ground at every visit and Patch_MapRemoval takes back
        /// what is left, so this holder is the place's remaining goods rather than
        /// a running total of them. See InhabitedPlaceDef.larder.
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

        /// <summary>
        /// The thingIDNumber of every stack the place's stock landed as for the
        /// visit in progress. Same idea as <see cref="onTheGround"/> and the same
        /// reason: the holder is emptied onto the map, so while a map exists this
        /// is the only record of which stacks came out of it.
        ///
        /// ⚠️ A FLOOR, NOT A CENSUS -- see InhabitedStock.DumpOnto. A split or
        /// merged stack gets an ID that was never written here, which is why
        /// <see cref="StockArea"/> exists alongside it.
        /// </summary>
        public List<int> stockOnTheGround = new List<int>();

        /// <summary>Where the goods were put down this visit. Invalid until a map
        /// has generated. Scribed so the recall can still find the area after a
        /// save/load taken mid-visit.</summary>
        public IntVec3 stockSpot = IntVec3.Invalid;

        /// <summary>Half-width of the stock area around <see cref="stockSpot"/>.
        /// ThingPlaceMode.Near walks outward from the anchor, so the area has to
        /// be wider than the drop itself or the tail of a large larder lands
        /// outside its own granary.</summary>
        public int stockRadius = 8;

        /// <summary>Total stackCount that reached the ground this visit. The
        /// denominator for "most of the granary is gone".</summary>
        public int stockSpawnedCount;

        /// <summary>
        /// A cause named by <see cref="InhabitedFate"/> has fired. Detected live
        /// by MapComponent_InhabitedWatch during the visit; ACTED ON at teardown
        /// by InhabitedFateWorker.Apply -- see that method for why the two are
        /// separated rather than the cast walking off the map in front of the
        /// player.
        /// </summary>
        public bool threatened;

        /// <summary>The translation key of the cause that fired. Kept so a later
        /// letter or inspect line can say WHICH, and so a save carries the reason
        /// rather than just the fact.</summary>
        public string threatReason;

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

        /// <summary>Where the place's goods lie on a generated map, as an area
        /// rather than a point. Empty until a map has generated.</summary>
        public CellRect StockArea =>
            stockSpot.IsValid ? CellRect.CenteredOn(stockSpot, stockRadius) : CellRect.Empty;

        /// <summary>
        /// `new`, not an override -- MapParent.GetDirectlyHeldThings() is not
        /// virtual (it always returns null; MapParent itself holds nothing
        /// directly, only a Map). Re-declaring IThingHolder on this class (see
        /// the class line) rebinds the interface's dispatch to THIS method for
        /// every WorldObject_Inhabited instance regardless of the static
        /// reference type doing the calling -- interface dispatch resolves off
        /// the runtime type's own map, not the declaring type's non-virtual
        /// body.
        /// </summary>
        public new ThingOwner GetDirectlyHeldThings()
        {
            return roster;
        }

        /// <summary>
        /// Override, not new -- MapParent.GetChildHolders IS virtual. base()
        /// first: MapParent's own body appends the generated Map as a child
        /// holder when HasMap, which is the whole point of the rebase (a
        /// visited place's pawns-on-the-map are reachable through this object
        /// now, not just through whatever else used to own the tile).
        /// </summary>
        public override void GetChildHolders(List<IThingHolder> outChildren)
        {
            base.GetChildHolders(outChildren);
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
            Scribe_Collections.Look(ref stockOnTheGround, "stockOnTheGround", LookMode.Value);
            Scribe_Values.Look(ref stockSpot, "stockSpot", IntVec3.Invalid);
            Scribe_Values.Look(ref stockRadius, "stockRadius", 8);
            Scribe_Values.Look(ref stockSpawnedCount, "stockSpawnedCount", 0);
            Scribe_Values.Look(ref threatened, "threatened", defaultValue: false);
            Scribe_Values.Look(ref threatReason, "threatReason");
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
                if (stockOnTheGround == null)
                {
                    stockOnTheGround = new List<int>();
                }
                // A zero or negative radius makes StockArea a single cell or an
                // empty one -- narrower than the drop it has to cover, so the
                // recall would leave goods behind rather than fail loudly.
                if (stockRadius <= 0)
                {
                    stockRadius = 8;
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
            // ⛔ NOTHING TO INSTANTIATE IS NOT THE SAME AS HAVING INSTANTIATED
            // NOTHING, and latching the flag over the difference made a place
            // permanently sterile. placeDef is assigned in exactly one place --
            // GenStep_ComposeSettlementDistrict -- so a place reaches this with a
            // null archetype whenever that step did not run or did not bind: the
            // whole wilderness RM_InhabitedPlace tile-mutator route, which has no
            // compose step at all, and any settlement whose manifest name failed
            // to match on the FIRST visit. The flag then said "done" over an
            // unfilled larder and an unrolled cast, and because it is only ever
            // read as `if (!castInstantiated)`, no later visit -- and no later
            // authoring of the manifest or the archetype -- could reach this
            // method again. Returning without latching costs three field reads a
            // visit and leaves the place recoverable.
            if (placeDef == null && Cast == null)
            {
                return;
            }

            castInstantiated = true;

            // Fixed 2026-09-03 (INHABITED_STOCK_ONTO_MAP_AND_FATE_1): the stock
            // fill used to sit at the BOTTOM of this method, below the early
            // return for "no cast". A place with a larder and no InhabitedCastDef
            // -- which is every place in this build set, since no cast defs are
            // authored yet -- therefore got no goods either, and the larder table
            // could not be exercised at all. Nothing about a granary depends on
            // somebody living in it.
            FillStock();

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
        }

        /// <summary>
        /// Stock the holder from the archetype's tables. Runs once, inside
        /// InstantiateCast, before the cast is rolled.
        ///
        /// ⚖️ THE TRADE TABLE IS GATED ON A DEALER AND THE LARDER IS NOT, which
        /// is InhabitedPlaceDef.stock's own documented meaning ("trade goods held
        /// for a cast that contains a dealer") finally enforced. Sustenance is
        /// what a place HAS; merchandise is what a dealer BROUGHT, and a place
        /// with nobody to sell it has no reason to be sitting on it -- least of
        /// all now that the goods land on the ground where the player can take
        /// them.
        /// </summary>
        private void FillStock()
        {
            if (placeDef == null || stock == null)
            {
                return;
            }
            stock.Fill(placeDef.larder);
            if (HasTrader)
            {
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
                    if (!roster.Remove(p))
                    {
                        continue;
                    }
                    if (!pool.Absorb(p, Faction, DisplacedReason.Fled, LabelCap)
                        && !roster.TryAdd(p, canMergeWithExistingStacks: false))
                    {
                        // Absorb refuses a destroyed pawn and a pool that will
                        // not take them, and this loop had already taken them off
                        // the roster -- so they were held by nothing, which no
                        // Scribe path reaches and no save can carry.
                        // InhabitedFateWorker.Apply guards its identical loop this
                        // way; this copy and the debug one did not.
                        Log.Error("[RimMandrake.Inhabited] " + p.LabelShort + " left " + LabelCap
                                  + " and has nowhere to be; they are lost.");
                    }
                }
            }
            base.Destroy();
        }
    }
}
