"""validation.py -- first north-star script for RimUtinni: KyberTradePlot (mandrake.rut.kybertradeplot).

KYBER_TRADE_PLOT_FIRST_SCRIPT_1 (KYBER_TRADE_PLOT_1). Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run KyberTradePlot

INTENDED FUNCTION (About.xml): every kyber/mindstone sale in a trade window raises Imperial attention on the Colony
Visibility meter, Hutt interest, and Cartel goodwill when the Cartel buys; after the second sale the Homestead visit
(three moisture farmers, one unarmed, a choice letter asking how the kyber was obtained) comes once; a straight answer,
or the Cartel fixer when the visit went nowhere, brings the one donation quest (no reward, no Heat, no Rebellion).
WHAT IT PROVES (live, through existing bridge tools; no proof hooks were added):
  * the GiveQuest incident and the visit incident answer a dry run
  * every Mod Settings bool flips and reads back through jawa/mod_settings_field (class and field names resolve)
  * every attribute-declared Harmony patch (the TradeDeal.TryExecute kyber-sale hook) lists this mod's Harmony id as an
    owner (jawa/harmony_patches)
  * every shipped def is loaded and its scalar fields read back equal to the XML (modcheck.shipped_defs)
OFFLINE (python3 src/RimMandrake/Utils/selftest_kyber_trade_plot.py): the sale count over real Tradeable/TradeDeal
objects, the patch's target and injected parameters, the donation's delivery never being a trade deal (IL of
TradeRequestComp.Fulfill), the heat landing on a real GameComponent_ColonyVisibility, and the plot's state machine tick
by tick: the visit once, the donation once through either door.
NOT PROVEN HERE OR OFFLINE (first pokes for the next live pass):
  * a real trade window sale: the first-sale letter, Visibility up, Cartel goodwill up
  * the visit spawning its three pawns and the choice letter's answers
  * the donation quest generating at a lane settlement and its delivery paying the letter of thanks
STATIC (offline): `python3 validation.py` runs modcheck.mod_static over the mod -- every Defs/Patches XML parses, no
inert top-level `<Operation MayRequire>`, every Source/*.cs is in the csproj, a ModSettings class exists and every
Scribed setting has a control.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
from modcheck import mod_static  # noqa: E402


def static_checks():
    return mod_static.static_findings(HERE)


def _build_suite():
    from modcheck import Suite, ExpectationFailed, shipped_defs  # noqa: F401
    suite = Suite("KyberTradePlot")
    suite.toggles = sorted(mod_static.bool_settings(HERE))

    mod_static.add_settings_chain(suite, __file__)
    mod_static.add_harmony_chain(suite, __file__)
    mod_static.add_incident_chain(suite, __file__)
    shipped_defs.add_chain(suite, __file__, sanity=('RUT_KyberHomesteadVisit', 'RUT_KyberDonationSmuggle'), min_count=6)
    return suite


try:
    suite = _build_suite()
except ImportError:
    suite = None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL (%d)" % len(problems)))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
