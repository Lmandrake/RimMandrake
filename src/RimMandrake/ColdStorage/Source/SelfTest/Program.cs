// COLD_STORAGE_ENGINE_BUILD_CLIMATE_COMP: offline selftest of the cold storage engine.
//
// Compiles the REAL Kernel/ColdStorageKernel.cs (every rule the comps and Harmony patches apply) and checks it against
// the game's own Verse.GenTemperature.RotRateAtTemperature from the shipped Assembly-CSharp.dll. Proves:
//   1. rot per tick for each unit type (chill at three temperatures, stasis holding and down, sealed);
//   2. the temperature an item held by a unit reads (chill: the unit's; stasis and off: the room's);
//   3. every engine switch off gives vanilla: rot at room temperature, no power drawn, no aging;
// plus the unit's temperature step (cooling, drift, insulation, passive drop, no heating), power draw, aging and
// seal failure. What it cannot prove: that the Harmony patches land and the comps call these in a running game; that
// is COLD_STORAGE_PROOF_VERIFY_ROT_RATES_LIVE.
using System;
using Verse;

namespace RimMandrake.ColdStorage.SelfTest
{
    internal static class Program
    {
        private static int pass;
        private static int fail;

        private static void Check(string name, bool ok, string detail = "")
        {
            if (ok)
            {
                pass++;
            }
            else
            {
                fail++;
                Console.WriteLine("FAIL " + name + (detail.Length > 0 ? ": " + detail : ""));
            }
        }

        private static void Near(string name, float got, float want, float tol = 1e-4f)
        {
            Check(name, Math.Abs(got - want) <= tol, "got " + got + ", want " + want);
        }

        private static readonly Func<float, float> Vanilla = GenTemperature.RotRateAtTemperature;

        private static int Main()
        {
            RotPerUnitType();
            TemperatureReading();
            SettingsOffIsVanilla();
            StasisOffFallsBackToChill();
            UnitTemperatureStep();
            Power();
            AgingAndFailure();
            OneDayEndToEnd();
            FixedRotFactors();
            Console.WriteLine("coldstorage selftest: " + pass + " passed, " + fail + " failed");
            return fail == 0 ? 0 : 1;
        }

        // 1. rot per tick for each unit type, at a hot room (30 C)
        private static void RotPerUnitType()
        {
            const float room = 30f;
            EffectiveMode chill = ColdStorageKernel.Resolve(StorageMode.Chill, true, true);
            EffectiveMode stasis = ColdStorageKernel.Resolve(StorageMode.Stasis, true, true);
            Check("resolve chill", chill == EffectiveMode.Chill);
            Check("resolve stasis", stasis == EffectiveMode.Stasis);

            Near("chill unit at -10 C: frozen, no rot", ColdStorageKernel.RotPerTick(chill, true, false, -10f, room, Vanilla), 0f);
            Near("chill unit at 5 C: half rate", ColdStorageKernel.RotPerTick(chill, true, false, 5f, room, Vanilla), 0.5f);
            Near("chill unit at 20 C: full rate", ColdStorageKernel.RotPerTick(chill, true, false, 20f, room, Vanilla), 1f);
            Near("chill unit unpowered still reads its own (drifting) temperature",
                ColdStorageKernel.RotPerTick(chill, false, false, 2f, room, Vanilla), 0.2f);
            Near("stasis holding: no rot in a hot room", ColdStorageKernel.RotPerTick(stasis, true, false, room, room, Vanilla), 0f);
            Near("stasis down: room rate", ColdStorageKernel.RotPerTick(stasis, false, false, room, room, Vanilla), 1f);
            Near("sealed on the floor: no rot", ColdStorageKernel.RotPerTick(EffectiveMode.None, false, true, room, room, Vanilla), 0f);
            Near("sealed in a chill unit: no rot", ColdStorageKernel.RotPerTick(chill, true, true, 20f, room, Vanilla), 0f);
            Near("unsealed (opened) on the floor: room rate", ColdStorageKernel.RotPerTick(EffectiveMode.None, false, false, room, room, Vanilla), 1f);
            Check("seal suspends rot only while sealed", ColdStorageKernel.SealSuspendsRot(true) && !ColdStorageKernel.SealSuspendsRot(false));
            Check("stasis holds only when active", ColdStorageKernel.StasisHolds(EffectiveMode.Stasis, true)
                && !ColdStorageKernel.StasisHolds(EffectiveMode.Stasis, false)
                && !ColdStorageKernel.StasisHolds(EffectiveMode.Chill, true));
        }

        // 2. the temperature a held item reads
        private static void TemperatureReading()
        {
            Check("chill: item reads the unit", ColdStorageKernel.TryHeldTemperature(EffectiveMode.Chill, -7f, out float t) && t == -7f);
            Check("stasis: item keeps the room (comes out unfrozen)", !ColdStorageKernel.TryHeldTemperature(EffectiveMode.Stasis, -7f, out _));
            Check("off: item keeps the room", !ColdStorageKernel.TryHeldTemperature(EffectiveMode.None, -7f, out _));
            // The vanilla rate the item then gets is the game's own, at the read temperature, at every degree.
            for (float u = -30f; u <= 40f; u += 0.5f)
            {
                float got = ColdStorageKernel.RotPerTick(EffectiveMode.Chill, true, false, u, 25f, Vanilla);
                if (got != GenTemperature.RotRateAtTemperature(u))
                {
                    Check("chill rate equals vanilla at unit temp " + u, false, "got " + got);
                    return;
                }
            }
            Check("chill rate equals vanilla at the unit temperature, -30..40 C", true);
        }

        // 3. every switch off: vanilla
        private static void SettingsOffIsVanilla()
        {
            foreach (StorageMode mode in new[] { StorageMode.Chill, StorageMode.Stasis, StorageMode.Sealed })
            {
                EffectiveMode e = ColdStorageKernel.Resolve(mode, false, false);
                Check("all off: " + mode + " unit is a plain shelf", e == EffectiveMode.None);
                bool same = true;
                for (float room = -30f; room <= 40f; room += 0.5f)
                {
                    // the unit's last temperature (-20) must not leak through once switched off
                    if (ColdStorageKernel.RotPerTick(e, true, false, -20f, room, Vanilla) != GenTemperature.RotRateAtTemperature(room))
                    {
                        same = false;
                    }
                }
                Check("all off: " + mode + " unit rots at vanilla room rate, -30..40 C", same);
                Near("all off: " + mode + " unit draws no power", ColdStorageKernel.PowerDraw(e, 200f, 1f, false, 0.3f), 0f);
            }
            Check("chill off, stasis on: chill unit is a shelf", ColdStorageKernel.Resolve(StorageMode.Chill, false, true) == EffectiveMode.None);
            Check("chill off, stasis on: stasis unit still holds", ColdStorageKernel.Resolve(StorageMode.Stasis, false, true) == EffectiveMode.Stasis);
            Check("aging off: sealed goods never age", ColdStorageKernel.AgingTicks(10f, 1f, false) == -1
                && !ColdStorageKernel.HasAged(0, int.MaxValue, ColdStorageKernel.AgingTicks(10f, 1f, false)));
            Near("failure multiplier 0: never ruins", ColdStorageKernel.SealFailureChance(0.5f, 0f), 0f);
        }

        // stasis switched off: the unit chills at -10 C (section 6)
        private static void StasisOffFallsBackToChill()
        {
            EffectiveMode e = ColdStorageKernel.Resolve(StorageMode.Stasis, true, false);
            Check("stasis off: stasis unit chills", e == EffectiveMode.Chill);
            Near("stasis off: fallback setpoint -10 C", ColdStorageKernel.EffectiveSetpoint(StorageMode.Stasis, e, 4f), -10f);
            Near("chill unit keeps its own setpoint", ColdStorageKernel.EffectiveSetpoint(StorageMode.Chill, EffectiveMode.Chill, 4f), 4f);
            float t = 25f;
            for (int i = 0; i < 10; i++)
            {
                t = ColdStorageKernel.StepUnitTemperature(t, -10f, 25f, true, false, 20f, 0.2f, 0f, 1f, 0.1f);
            }
            Near("stasis off: reaches -10 C within 2 h", ColdStorageKernel.StepUnitTemperature(t, -10f, 25f, true, false, 20f, 0.2f, 0f, 1f, 1f), -10f);
        }

        private static void UnitTemperatureStep()
        {
            Near("cooling is linear, 20 C/h", ColdStorageKernel.StepUnitTemperature(20f, -10f, 20f, true, false, 20f, 0.2f, 0f, 1f, 1f), 0f);
            Near("cooling stops at the setpoint", ColdStorageKernel.StepUnitTemperature(0f, -10f, 20f, true, false, 20f, 0.2f, 0f, 1f, 1f), -10f);
            Near("zero hours: no change", ColdStorageKernel.StepUnitTemperature(5f, -10f, 20f, true, false, 20f, 0.2f, 0f, 1f, 0f), 5f);
            float drift1 = ColdStorageKernel.StepUnitTemperature(-10f, -10f, 20f, false, false, 20f, 0.2f, 0f, 1f, 1f);
            Near("unpowered drift: exp(-0.2) of the gap remains", drift1, 20f - 30f * (float)Math.Exp(-0.2), 1e-3f);
            float drift2 = ColdStorageKernel.StepUnitTemperature(-10f, -10f, 20f, false, false, 20f, 0.2f, 0f, 2f, 1f);
            Near("insulation 2: drifts half as fast", drift2, 20f - 30f * (float)Math.Exp(-0.1), 1e-3f);
            Check("insulation slows the drift", drift2 < drift1);
            Near("passive drop: no colder than room - 8", ColdStorageKernel.StepUnitTemperature(30f, -10f, 30f, true, false, 20f, 0.2f, 8f, 1f, 5f), 22f);
            Near("cannot heat: holds the setpoint in a colder room",
                ColdStorageKernel.StepUnitTemperature(-15f, -10f, 0f, true, false, 20f, 50f, 0f, 1f, 1f), -10f);
            float cold = ColdStorageKernel.StepUnitTemperature(-15f, -10f, -30f, true, false, 20f, 0.2f, 0f, 1f, 1f);
            Check("cannot heat: a colder room pulls it down", cold < -15f, "got " + cold);
            Near("can heat: rises to the setpoint", ColdStorageKernel.StepUnitTemperature(-15f, -10f, -30f, true, true, 20f, 0.2f, 0f, 1f, 1f), -10f);
        }

        private static void Power()
        {
            Near("chill cooling: full draw", ColdStorageKernel.PowerDraw(EffectiveMode.Chill, 200f, 1f, false, 0.3f), 200f);
            Near("chill at setpoint: idle draw", ColdStorageKernel.PowerDraw(EffectiveMode.Chill, 200f, 1f, true, 0.3f), 60f);
            Near("power multiplier 2", ColdStorageKernel.PowerDraw(EffectiveMode.Chill, 200f, 2f, false, 0.3f), 400f);
            Near("stasis: always full draw", ColdStorageKernel.PowerDraw(EffectiveMode.Stasis, 200f, 1f, true, 0.3f), 200f);
        }

        private static void AgingAndFailure()
        {
            Check("10 days aging = 600000 ticks", ColdStorageKernel.AgingTicks(10f, 1f, true) == 600000);
            Check("aging multiplier 0.5 halves it", ColdStorageKernel.AgingTicks(10f, 0.5f, true) == 300000);
            Check("no aging days: never", ColdStorageKernel.AgingTicks(0f, 1f, true) == -1);
            Check("not aged one tick early", !ColdStorageKernel.HasAged(1000, 1000 + 599999, 600000));
            Check("aged on time", ColdStorageKernel.HasAged(1000, 1000 + 600000, 600000));
            Check("unknown seal tick never ages", !ColdStorageKernel.HasAged(-1, 10000000, 600000));
            Near("failure chance scales", ColdStorageKernel.SealFailureChance(0.1f, 2f), 0.2f);
            Near("failure chance clamps to 1", ColdStorageKernel.SealFailureChance(0.6f, 3f), 1f);
            Check("merged seal tick is stack-weighted", ColdStorageKernel.MergedSealTick(100, 1, 200, 3) == 175);
        }

        // one in-game day at 25 C, stepped in rare ticks (250) as the game does: rot ticks accrued per unit type
        private static void OneDayEndToEnd()
        {
            const float room = 25f;
            float vanilla = 0f;
            float chill = 0f;
            float stasis = 0f;
            float sealedRot = 0f;
            float unit = room;
            for (int tick = 0; tick < 60000; tick += 250)
            {
                unit = ColdStorageKernel.StepUnitTemperature(unit, -10f, room, true, false, 20f, 0.2f, 0f, 1f, 250f / ColdStorageKernel.TicksPerHour);
                vanilla += ColdStorageKernel.RotPerTick(EffectiveMode.None, true, false, unit, room, Vanilla) * 250f;
                chill += ColdStorageKernel.RotPerTick(EffectiveMode.Chill, true, false, unit, room, Vanilla) * 250f;
                stasis += ColdStorageKernel.RotPerTick(EffectiveMode.Stasis, true, false, room, room, Vanilla) * 250f;
                sealedRot += ColdStorageKernel.RotPerTick(EffectiveMode.None, false, true, room, room, Vanilla) * 250f;
            }
            Near("one day on the floor: 60000 rot ticks", vanilla, 60000f, 0.5f);
            Check("one day in a chill unit: only the cool-down hour rots", chill > 0f && chill < 4000f, "got " + chill);
            Near("one day in stasis: none", stasis, 0f);
            Near("one day sealed: none", sealedRot, 0f);
            Console.WriteLine("one day at 25 C, rot ticks: floor " + vanilla + ", chill unit " + chill + ", stasis " + stasis + ", sealed " + sealedRot);
        }

        // 9. fixed rot multipliers: a slow-stasis unit, preserved goods (sand-dried, pickled), the seal overriding both
        private static void FixedRotFactors()
        {
            const float room = 30f;
            EffectiveMode stasis = EffectiveMode.Stasis;
            Near("true stasis (factor 0): no rot", ColdStorageKernel.RotFactor(stasis, true, false, 0f, 1f), 0f);
            Near("slow stasis x0.1 holding", ColdStorageKernel.RotFactor(stasis, true, false, 0.1f, 1f), 0.1f);
            Near("slow stasis x0.1 unpowered: full", ColdStorageKernel.RotFactor(stasis, false, false, 0.1f, 1f), 1f);
            Near("sand-dried x0.1 on the floor", ColdStorageKernel.RotPerTick(EffectiveMode.None, false, false, room, room, Vanilla, 0f, 0.1f), 0.1f);
            Near("pickled x0.05 on the floor", ColdStorageKernel.RotPerTick(EffectiveMode.None, false, false, room, room, Vanilla, 0f, 0.05f), 0.05f);
            Near("pickled x0.05 in a chill unit at 5 C", ColdStorageKernel.RotPerTick(EffectiveMode.Chill, true, false, 5f, room, Vanilla, 0f, 0.05f), 0.025f);
            Near("pickled in slow stasis: factors multiply", ColdStorageKernel.RotFactor(stasis, true, false, 0.1f, 0.05f), 0.005f);
            Near("sealed overrides an item factor", ColdStorageKernel.RotFactor(EffectiveMode.None, false, true, 0f, 0.1f), 0f);
            Near("negative item factor clamps to 0", ColdStorageKernel.RotFactor(EffectiveMode.None, false, false, 0f, -1f), 0f);
            Near("chill does not use the unit factor", ColdStorageKernel.RotFactor(EffectiveMode.Chill, true, false, 0f, 1f), 1f);
            Check("ticks: factor 1 unchanged", ColdStorageKernel.TicksUntilRotWithFactor(60000, 1f) == 60000);
            Check("ticks: factor 0.1 x10", ColdStorageKernel.TicksUntilRotWithFactor(60000, 0.1f) == 600000);
            Check("ticks: factor 0 never", ColdStorageKernel.TicksUntilRotWithFactor(60000, 0f) == ColdStorageKernel.NeverRotTicks);
            Check("ticks: already never stays never", ColdStorageKernel.TicksUntilRotWithFactor(ColdStorageKernel.NeverRotTicks, 0.5f) == ColdStorageKernel.NeverRotTicks);
            Check("ticks: tiny factor caps at never", ColdStorageKernel.TicksUntilRotWithFactor(60000000, 0.01f) == ColdStorageKernel.NeverRotTicks);
            Check("ticks: already rotten (0) stays 0", ColdStorageKernel.TicksUntilRotWithFactor(0, 0.1f) == 0);
        }
    }
}
