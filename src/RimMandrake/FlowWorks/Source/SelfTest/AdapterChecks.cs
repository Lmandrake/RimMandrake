// Liquid networks build step L10 (design/RimMandrake/liquid_network_semantics_design_2026-10-11.md rev 2 §3.10-3.11, §6 L10):
// adapter modes Send / Take / Shut on the PRODUCTION rules (RM_AdapterRules), the boundary's short accept on the transfer service,
// then the production adapter read from source. Gates: save-key mapping; a short accept puts the units back.
using System;
using System.IO;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class AdapterChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("Adapter_save_keys_map_to_modes", () =>
            {
                Assert(RM_AdapterRules.ModeOf(true, false) == RM_AdapterMode.Send && RM_AdapterRules.ModeOf(false, false) == RM_AdapterMode.Take
                       && RM_AdapterRules.ModeOf(true, true) == RM_AdapterMode.Shut && RM_AdapterRules.ModeOf(false, true) == RM_AdapterMode.Shut,
                    "RM_adapterFeedNet true -> Send, false -> Take; RM_adapterShut wins");
                Assert(!RM_AdapterRules.ShutOnSpawn(true, false) && RM_AdapterRules.ShutOnSpawn(true, true) && RM_AdapterRules.ShutOnSpawn(false, false),
                    "an older save (no RM_adapterShut, false) keeps running; a new build starts Shut");
                Assert(RM_AdapterRules.Next(RM_AdapterMode.Send) == RM_AdapterMode.Take && RM_AdapterRules.Next(RM_AdapterMode.Take) == RM_AdapterMode.Shut
                       && RM_AdapterRules.Next(RM_AdapterMode.Shut) == RM_AdapterMode.Send, "the button cycles Send, Take, Shut");
            });

            Case("Adapter_short_accept_puts_units_back", () =>
            {
                int tank = 50;
                float ve = 0f, carry = 0f;
                // the VE storage takes only 3.0 of the 8 units offered (per 1.0)
                RM_TransferLeg send = RM_TransferLeg.Boundary(k => true, k => { float d = Math.Min(k, 3.0f); ve += d; return RM_LiquidTransfer.SettleSend(d, 1f, k, ref carry); });
                int moved = RM_LiquidTransfer.Move(8, RM_TransferLeg.Store(k => tank >= k, k => { tank -= k; return true; }, k => { tank += k; return true; }), send, out RM_MoveOutcome o);
                Assert(moved == 3 && tank == 47 && ve == 3f && carry == 0f && o.Refused == RM_MoveRefusal.Partial, "3 cross, 5 go back into the tank (" + moved + ", " + tank + ")");
            });

            Case("Adapter_production_modes", () =>
            {
                string ad = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "CompLiquidPipeAdapter.cs"));
                RiverSwitchFlipChecks.Has(ad, @"Scribe_Values\.Look\(ref feedNet, ""RM_adapterFeedNet"", true\); Scribe_Values\.Look\(ref shut, ""RM_adapterShut"", false\);", "the two save keys");
                RiverSwitchFlipChecks.Has(ad, @"shut = RM_AdapterRules\.ShutOnSpawn\(respawningAfterLoad, shut\);", "a new build starts Shut");
                RiverSwitchFlipChecks.Has(ad, @"if \(shut\) \{ status = ""RMFlow_AdapterShut""\.Translate\(\); return; \}", "Shut moves nothing");
                RiverSwitchFlipChecks.Has(ad, @"private void FailClosed\(string why\) \{ Log\.ErrorOnce\([^;]*; status = ""RMFlow_AdapterBroken""\.Translate\(\); shut = true; \}", "a failure shuts the adapter, one red line");
                RiverSwitchFlipChecks.Has(ad, @"if \(!Bind\(\)\) \{ FailClosed\(", "a reflection failure fails closed");
            });
        }
    }
}
