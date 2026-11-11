"""One-time repair editing receipt; assertions prevent silently missing a caller."""
from pathlib import Path

root = Path(__file__).resolve().parents[3]
base = root / 'src/RimMandrake/FlowWorks/Source'

def replace(path, old, new, count=1):
    p = base / path
    s = p.read_text()
    assert s.count(old) == count, (path, old, s.count(old))
    p.write_text(s.replace(old, new))

def scope(path, signature, actor):
    p = base / path
    s = p.read_text()
    assert s.count(signature) == 1, (path, signature)
    at = s.index('{', s.index(signature)) + 1
    s = s[:at] + '\n\t\t\tusing var theftActor = RimMandrake.FlowWorks.Machinery.RM_LiquidTheft.As(' + actor + ');' + s[at:]
    p.write_text(s)

scope('LiquidTypes/Building_LiquidPump.cs', 'private string TryDraw()', 'this')
scope('LiquidTypes/Building_LiquidPump.cs', 'private string TryPour()', 'this')
for path in ('Machinery/CompLiquidConverter.cs', 'Machinery/CompLiquidPipeAdapter.cs', 'Machinery/Kits/RM_LiquidReaction.cs'):
    scope(path, 'public override void CompTickRare()', 'parent')
scope('Thirst/Building_RM_PipeFaucet.cs', 'public static bool TryPour(Thing faucet, LiquidDef liquid, int units)', 'faucet')
scope('Sprinklers/RM_Sprinkle.cs', 'public static Result Pulse(ThingWithComps head, List<IntVec3> cells, bool enabled, bool switchOn)', 'head')
scope('RM_IceMelter.cs', 'public static void Postfix(Bill_Production __instance)', '__instance.billStack?.billGiver as Thing')
scope('Machinery/Kits/RM_LiquidBath.cs', 'public static void Postfix(Bill_Production __instance)', '__instance.billStack?.billGiver as Thing')
for path in ('LiquidTypes/JobDriver_FillBottleFromTank.cs', 'LiquidTypes/JobDriver_EmptyBottleIntoTank.cs'):
    replace(path, 'finish.initAction = delegate\n            {', 'finish.initAction = delegate\n            {\n                using var theftActor = Machinery.RM_LiquidTheft.As(pawn);')
replace('Thirst/RM_ThirstJobs.cs', 'Building_LiquidTank tank = Tank;\n\t\t\t\tLiquidDef liquid', 'using var theftActor = Machinery.RM_LiquidTheft.As(pawn);\n\t\t\t\tBuilding_LiquidTank tank = Tank;\n\t\t\t\tLiquidDef liquid')
# The actor of a settle is the actual Empty source or Fill destination, not
# whichever unrelated mover caused this component to be enumerated first.
replace('Machinery/RM_LiquidNet.cs', 'Building_LiquidTank src = tanks[si], dst = tanks[di];', 'Building_LiquidTank src = tanks[si], dst = tanks[di];\n\t\t\t\t\t\tusing var theftActor = RM_LiquidTheft.As(src.EffectiveMode == RM_TankMode.Empty ? src : dst);')
replace('Machinery/RM_LiquidNet.cs', 'foreach (Building_LiquidTank tank in dumps.OrderBy(t => t.thingIDNumber))\n\t\t\t{', 'foreach (Building_LiquidTank tank in dumps.OrderBy(t => t.thingIDNumber))\n\t\t\t{\n\t\t\t\tusing var theftActor = RM_LiquidTheft.As(tank);')

replace('LiquidTypes/Building_LiquidTank.cs', '        public int theftSeenUnits = -1;\n        public LiquidDef theftSeenLiquid;', '''        // Signed player mutations since the last theft pass, keyed by liquid so an
        // equal-volume identity swap remains visible. Symmetric put-backs cancel.
        public System.Collections.Generic.Dictionary<LiquidDef, int> theftPlayerChanges = new System.Collections.Generic.Dictionary<LiquidDef, int>();
        public RimWorld.Faction theftPendingVictim;''')
replace('LiquidTypes/Building_LiquidTank.cs', '            storedLiquid = liquid;\n            storedUnits += units;', '            Machinery.RM_LiquidTheft.Record(this, liquid, units);\n            storedLiquid = liquid;\n            storedUnits += units;')
replace('LiquidTypes/Building_LiquidTank.cs', '            storedUnits -= units;', '            Machinery.RM_LiquidTheft.Record(this, storedLiquid, -units);\n            storedUnits -= units;')
replace('LiquidTypes/Building_LiquidTank.cs', '            Scribe_Values.Look(ref theftTicks, "rmTheftTicks", 0);', '''            Scribe_Values.Look(ref theftTicks, "rmTheftTicks", 0);
            Scribe_References.Look(ref theftPendingVictim, "rmTheftPendingVictim");
            Scribe_Collections.Look(ref theftPlayerChanges, "rmTheftPlayerChanges", LookMode.Def, LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && theftPlayerChanges == null)
            {
                theftPlayerChanges = new System.Collections.Generic.Dictionary<LiquidDef, int>();
            }''')

p = base / 'Machinery/RM_LiquidTheft.cs'
s = p.read_text()
a = s.index('\t/// <summary>')
b = s.index('\tpublic static class RM_LiquidTheft', a)
s = s[:a] + '''\t/// <summary>
\t/// L9: successful player-caused tank mutations, netted per liquid per pump cycle.
\t/// Machine/pawn/job entry scopes supply the actor; tank mutation methods record the
\t/// signed change, so transfer put-backs cancel, including partial split rollback.
\t/// Reachability and total stock changes are not actor evidence: owner activity may
\t/// reach player equipment or exactly replenish a real withdrawal. Witness/caught
\t/// state and the power-theft goodwill rule remain unchanged. Pending changes are
\t/// saved with each tank; unscoped setup/debug writes are not player transfers.
\t/// </summary>
''' + s[b:]
a = s.index('\t\tpublic static void TheftTick')
s = s[:a] + '''        [System.ThreadStatic] private static Thing actor;

        /// <summary>Lexical main-thread actor boundary, including credits/hose fills.
        /// Always restore the previous actor, even on early returns and exceptions.
        /// Owner/unowned nested entries mask an outer player's scope.</summary>
        public struct ActorScope : System.IDisposable
        {
            private readonly Thing previous;
            public ActorScope(Thing current)
            {
                previous = actor;
                actor = current;
            }
            public void Dispose() { actor = previous; }
        }

        public static ActorScope As(Thing current)
        {
            return new ActorScope(current);
        }

        /// <summary>Called only after a tank mutation passed validation, before an
        /// emptying removal clears its liquid identity. Undo uses the same actor.
        /// No component/global tank set is credited; only this tank changed.</summary>
        public static void Record(Building_LiquidTank tank, LiquidDef liquid, int delta)
        {
            if (!RM_MachinerySettings.liquidTheftEnabled)
            {
                tank.theftPlayerChanges.Clear();
                tank.theftPendingVictim = null;
                return;
            }
            if (actor?.Faction != Faction.OfPlayer || actor.Map != tank.Map || !RM_LiquidNet.IsForeign(tank)) return;
            if (tank.theftPendingVictim != tank.Faction)
            {
                tank.theftPlayerChanges.Clear();
                tank.theftPendingVictim = tank.Faction;
            }
            RM_LiquidTheftMath.RecordChange(tank.theftPlayerChanges, liquid, delta);
        }

''' + s[a:]
s = s.replace('if (map == null || !RM_MachinerySettings.liquidTheftEnabled)', 'if (map == null)')
a = s.index('\t\t\t\tif (!(th is Building_LiquidTank t)')
b = s.index('\t\t\t\tif (t.theftCaughtBy != victim)', a)
s = s[:a] + '''                if (!(th is Building_LiquidTank t)) continue;
                Faction victim = t.Faction;
                bool touched = t.theftPendingVictim == victim && RM_LiquidTheftMath.HasChanges(t.theftPlayerChanges);
                // Consume on every pass, even disabled, claimed, defeated or unwitnessed.
                // Thus a witness arriving later cannot catch a past, unseen move.
                t.theftPlayerChanges.Clear();
                t.theftPendingVictim = null;
                if (!RM_MachinerySettings.liquidTheftEnabled || !RM_LiquidNet.IsForeign(t)
                    || !touched || victim == null || victim.defeated)
                {
                    continue;
                }
''' + s[b:]
s = s.replace('/// components, a player reel\'s hose on one, or a player machine touching it)? Only such a tank can be stolen from.', '/// components, a player reel\'s hose on one, or a player machine touching it)? Opportunity diagnostic only; never attribution.')
p.write_text(s)

replace('Machinery/RM_LiquidNetKernel.cs', '        /// <summary>Was liquid taken from or put into the tank since the last look', '''        /// <summary>Signed player-only changes: a refused/restored transfer cancels,
        /// while changing identity at equal volume leaves two nonzero entries.</summary>
        public static void RecordChange<T>(Dictionary<T, int> changes, T liquid, int delta) where T : class
        {
            if (liquid == null || delta == 0) return;
            int net = (changes.TryGetValue(liquid, out int old) ? old : 0) + delta;
            if (net == 0) changes.Remove(liquid);
            else changes[liquid] = net;
        }

        public static bool HasChanges<T>(Dictionary<T, int> changes)
        {
            if (changes == null) return false;
            foreach (int delta in changes.Values) if (delta != 0) return true;
            return false;
        }

        /// <summary>Was liquid taken from or put into the tank since the last look''')
