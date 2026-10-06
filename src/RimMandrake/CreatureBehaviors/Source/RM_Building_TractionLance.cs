using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // WEBWORK_TRACTION_LANCE_BUILD_1 step 2: the traction lance. The capstan is the fixed powered turret; the lance
    // is the CREWED one (vanilla CompMannable + JobDriver_ManTurret, which runs on any Building: its only
    // Building_TurretGun casts are `as`-guarded load/refuel helpers — RimSage-read 2026-10-06). It fires a tether
    // and reels one visible pawn toward it with THE shared pull, RM_CompTetherPull; nothing here moves a pawn.
    //
    // Step 3, lasso relative: the building is stuffed by fabric and the stuff IS the tether. Per-stuff factors
    // come from RM_TetherStuffExtension on the def (cloth weak and snappy, devilstrand middling, thrixweave best),
    // times that fabric's Mod Settings multiplier. The tether's rigging is a CompRefuelable fuelled with fabric:
    // reeling wears it (scaled by the target's body size), a snap consumes all of it, and re-rigging is an
    // ordinary refuel job (a small fabric cost).
    //
    // Power draw scales with the target's body size while reeling.
    public class RM_TetherStuffFactor
    {
        public ThingDef stuff;
        public float range = 1f;
        public float strength = 1f;   // multiplies mass and body-size caps
        public float reel = 1f;
        public float snap = 1f;       // multiplies snap chance (higher = snappier)
    }

    public class RM_TetherStuffExtension : DefModExtension
    {
        public List<RM_TetherStuffFactor> factors = new List<RM_TetherStuffFactor>();
        // Tether rigging worn per reeled cell, per unit of target body size. PROVISIONAL.
        public float wearPerCellPerBodySize = 0.25f;
        // Extra power per unit of target body size while reeling, as a fraction of base draw. PROVISIONAL.
        public float powerPerBodySize = 1f;
        // Base mass / body-size caps before the stuff's strength. PROVISIONAL.
        public float maxMass = 120f;
        public float maxBodySize = 2f;
        // Damage the snap does to the lance. PROVISIONAL.
        public float snapDamage = 10f;

        public RM_TetherStuffFactor FactorFor(ThingDef stuff)
        {
            if (stuff == null || factors == null)
            {
                return null;
            }
            for (int i = 0; i < factors.Count; i++)
            {
                if (factors[i].stuff == stuff)
                {
                    return factors[i];
                }
            }
            return null;
        }
    }

    public class RM_Building_TractionLance : Building, IRM_TetherPullHost
    {
        private static Graphic topGraphic;

        public RM_CompTetherPull Pull => GetComp<RM_CompTetherPull>();
        public CompMannable Mannable => GetComp<CompMannable>();
        public CompPowerTrader Power => GetComp<CompPowerTrader>();
        public CompRefuelable Rigging => GetComp<CompRefuelable>();
        public RM_TetherStuffExtension Ext => def.GetModExtension<RM_TetherStuffExtension>() ?? new RM_TetherStuffExtension();

        /// <summary>Proof hook: a debug [Tool] sets this to stand in for a crew without spawning one.</summary>
        public bool debugForceManned;

        public bool Manned => debugForceManned || (Mannable != null && Mannable.MannedNow);
        public bool Rigged => Rigging == null || Rigging.HasFuel;

        public bool TetherCanWork => RM_CreatureBehaviorsSettings.lanceEnabled && Spawned && Manned
            && (Power == null || Power.PowerOn) && Rigged;

        public static float SettingsMultiplierFor(ThingDef stuff)
        {
            if (stuff == null)
            {
                return 1f;
            }
            switch (stuff.defName)
            {
                case "Cloth": return RM_CreatureBehaviorsSettings.lanceClothMultiplier;
                case "DevilstrandCloth": return RM_CreatureBehaviorsSettings.lanceDevilstrandMultiplier;
                case "Hyperweave": return RM_CreatureBehaviorsSettings.lanceThrixweaveMultiplier; // thrixweave (RM_Thrixweave_Rename.xml)
                default: return 1f;
            }
        }

        public RM_TetherTuning TetherTuning
        {
            get
            {
                RM_TetherStuffExtension ext = Ext;
                RM_TetherStuffFactor f = ext.FactorFor(Stuff) ?? new RM_TetherStuffFactor();
                float m = Mathf.Max(0.01f, SettingsMultiplierFor(Stuff));
                return new RM_TetherTuning
                {
                    range = RM_CreatureBehaviorsSettings.lanceRange * f.range * m,
                    reelSpeed = RM_CreatureBehaviorsSettings.lanceReelSpeed * f.reel,
                    cooldownSeconds = RM_CreatureBehaviorsSettings.lanceCooldownSeconds,
                    friendlyPull = RM_CreatureBehaviorsSettings.lanceFriendlyPull,
                    snapChance = Mathf.Clamp01(RM_CreatureBehaviorsSettings.lanceSnapChance * f.snap / m),
                    maxMass = ext.maxMass * f.strength * m,
                    maxBodySize = ext.maxBodySize * f.strength * m,
                    snapDamage = ext.snapDamage,
                };
            }
        }

        public Material TetherLineMaterial
        {
            get
            {
                Color c = Stuff != null ? Stuff.stuffProps.color : new Color(0.9f, 0.88f, 0.8f);
                return SolidColorMaterials.SimpleSolidColorMaterial(c);
            }
        }

        public void Notify_TetherReelStep(Pawn target)
        {
            float size = target != null ? target.BodySize : 1f;
            if (Rigging != null)
            {
                Rigging.ConsumeFuel(Ext.wearPerCellPerBodySize * size);
                if (!Rigging.HasFuel && Pull != null && Pull.Target != null)
                {
                    Pull.Snap("the tether wore through", "wear");
                    return;
                }
            }
            if (Power != null)
            {
                Power.PowerOutput = -Power.Props.PowerConsumption * (1f + Ext.powerPerBodySize * size);
            }
        }

        public void Notify_TetherSnapped(Pawn target, string reasonCode)
        {
            // A snapped tether is consumed: the lance must be re-rigged (refuelled with fabric) before it fires again.
            if (Rigging != null && Rigging.Fuel > 0f)
            {
                Rigging.ConsumeFuel(Rigging.Fuel);
            }
            ResetPower();
        }

        public void Notify_TetherReleased(Pawn target)
        {
            ResetPower();
        }

        private void ResetPower()
        {
            // Unconditional: a brownout mid-reel would otherwise leave the boosted draw on the trader, which
            // PowerNet then demands before restarting it (PowerNet.cs: !PowerOn && ... EnergyOutputPerTick).
            if (Power != null)
            {
                Power.PowerOutput = -Power.Props.PowerConsumption;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref debugForceManned, "debugForceManned");
        }

        protected override void DrawAt(Vector3 drawLoc, bool flip = false)
        {
            base.DrawAt(drawLoc, flip);
            if (topGraphic == null)
            {
                // PLACEHOLDER top: vanilla mini-turret top until RM_TractionLance_Top is installed through the art ledger
                // (a render sits in the artpipe _artsrc). Then point this at the installed texPath.
                topGraphic = GraphicDatabase.Get<Graphic_Single>("Things/Building/Security/TurretMini_Top", ShaderDatabase.Cutout, Vector2.one, Color.white);
            }
            Vector3 top = drawLoc;
            top.y = AltitudeLayer.BuildingOnTop.AltitudeFor();
            float angle = Pull != null ? Pull.TopAngle : 0f;
            Matrix4x4 mtx = Matrix4x4.TRS(top, Quaternion.AngleAxis(angle, Vector3.up), Vector3.one);
            Graphics.DrawMesh(MeshPool.plane10, mtx, topGraphic.MatSingle, 0);
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string mine = !RM_CreatureBehaviorsSettings.lanceEnabled ? "Switched off in Mod Settings."
                : !Manned ? "Needs a crew to fire."
                : !Rigged ? "Tether snapped: re-rig it with fabric."
                : null;
            if (mine == null)
            {
                return s;
            }
            return s.NullOrEmpty() ? mine : s + "\n" + mine;
        }
    }

    /// <summary>
    /// Dev proofs (WEBWORK_TRACTION_LANCE_BUILD_1 criteria), called through jawa/static_call. Deterministic state
    /// reads: position delta, tether outcome code, snap chance and range per fabric.
    /// </summary>
    public static class RM_TractionLanceProof
    {
        /// <summary>
        /// stuff: Cloth | DevilstrandCloth | Hyperweave. mode: raider | unmanned | wall | heavy | downed.
        /// Spawns a player lance of that stuff (power forced on; crew stood in by debugForceManned except "unmanned")
        /// and a target 9 cells east in the open, ropes it and reels until it arrives or the line goes.
        /// "wall" puts a steel wall between them; "heavy" uses a thrumbo; "downed" a downed player colonist.
        /// </summary>
        public static string ProofPull(string stuff, string mode)
        {
            Map map = Find.CurrentMap;
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_TractionLance");
            ThingDef stuffDef = DefDatabase<ThingDef>.GetNamedSilentFail(stuff);
            if (map == null || def == null || stuffDef == null)
            {
                return "UNMEASURED no map, no RM_TractionLance def, or no stuff " + stuff;
            }
            IntVec3 origin = IntVec3.Invalid;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(map.Center, 40f, true))
            {
                CellRect r = new CellRect(c.x - 1, c.z - 2, 13, 5);
                bool clear = r.InBounds(map);
                if (clear)
                {
                    foreach (IntVec3 x in r)
                    {
                        if (!x.Standable(map) || x.GetFirstBuilding(map) != null || x.GetFirstPawn(map) != null || x.Fogged(map))
                        {
                            clear = false;
                            break;
                        }
                    }
                }
                if (clear)
                {
                    origin = c;
                    break;
                }
            }
            if (!origin.IsValid)
            {
                return "UNMEASURED no clear 13x5 strip";
            }
            var lance = (RM_Building_TractionLance)GenSpawn.Spawn(ThingMaker.MakeThing(def, stuffDef), origin, map);
            lance.SetFaction(Faction.OfPlayer);
            if (lance.Power != null)
            {
                lance.Power.PowerOn = true;
            }
            lance.debugForceManned = mode != "unmanned";
            RM_CompTetherPull pull = lance.Pull;
            RM_TetherTuning tune = lance.TetherTuning;
            Pawn p;
            if (mode == "heavy")
            {
                p = PawnGenerator.GeneratePawn(PawnKindDefOf.Thrumbo, null);
            }
            else if (mode == "downed")
            {
                p = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
            }
            else
            {
                Faction enemy = Find.FactionManager.RandomEnemyFaction(allowNonHumanlike: false);
                p = PawnGenerator.GeneratePawn(PawnKindDefOf.Villager, enemy);
            }
            IntVec3 at = origin + new IntVec3(9, 0, 0);
            GenSpawn.Spawn(p, at, map);
            Thing wall = null;
            if (mode == "wall")
            {
                wall = GenSpawn.Spawn(ThingMaker.MakeThing(ThingDefOf.Wall, ThingDefOf.Steel), origin + new IntVec3(5, 0, 0), map);
            }
            if (mode == "downed")
            {
                HealthUtility.DamageUntilDowned(p, allowBleedingWounds: false);
            }
            IntVec3 start = p.Position;
            bool roped = false;
            int steps = 0;
            if (lance.TetherCanWork)
            {
                roped = pull.TryRope(p);
                while (pull.Target != null && steps < 60)
                {
                    pull.DebugReelNow();
                    steps++;
                }
            }
            IntVec3 end = p.Spawned ? p.Position : IntVec3.Invalid;
            string outcome = string.Format(
                "LANCE stuff={0} mode={1} canWork={2} roped={3} startDist={4:0.0} endDist={5:0.0} cellsMoved={6} steps={7} outcome={8} snaps={9} range={10:0.0} snapChance={11:0.000} maxMass={12:0.0} rigging={13:0.00}",
                stuff, mode, lance.TetherCanWork || roped, roped, start.DistanceTo(lance.Position),
                end.IsValid ? end.DistanceTo(lance.Position) : -1f, end.IsValid ? (int)start.DistanceTo(end) : -1,
                steps, pull.LastOutcome.NullOrEmpty() ? "none" : pull.LastOutcome, pull.Snaps,
                tune.range, tune.snapChance, tune.maxMass, lance.Rigging != null ? lance.Rigging.Fuel : -1f);
            if (p.Spawned)
            {
                p.Destroy();
            }
            wall?.Destroy();
            lance.Destroy();
            return outcome;
        }

        /// <summary>Range and snap chance per fabric, no map needed: the stuff criterion's deterministic read.</summary>
        public static string ProofStuffTable()
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_TractionLance");
            RM_TetherStuffExtension ext = def?.GetModExtension<RM_TetherStuffExtension>();
            if (ext == null)
            {
                return "UNMEASURED no RM_TractionLance or no RM_TetherStuffExtension";
            }
            var parts = new List<string>();
            foreach (RM_TetherStuffFactor f in ext.factors)
            {
                float m = Mathf.Max(0.01f, RM_Building_TractionLance.SettingsMultiplierFor(f.stuff));
                parts.Add(string.Format("{0}: range={1:0.0} snap={2:0.000} maxMass={3:0.0}", f.stuff?.defName ?? "null",
                    RM_CreatureBehaviorsSettings.lanceRange * f.range * m,
                    Mathf.Clamp01(RM_CreatureBehaviorsSettings.lanceSnapChance * f.snap / m), ext.maxMass * f.strength * m));
            }
            return "STUFF " + string.Join(" | ", parts);
        }
    }
}
