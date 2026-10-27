"""validation.py -- modcheck suite for RimStarWars Cuisine
(mandrake.rsw.cuisine).

Grounded in the mod's actual Source and Defs, read whole before writing
this: `CuisineDefOf.cs` (the one `[DefOf]`, `RSW_Skewer`),
`IngredientValueGetter_ExcludeSkewer.cs` (why every skewer-consuming
recipe needs a non-nutrition value getter -- read its own header comment:
without it, `WorkGiver_DoBill`'s ingredient-picking loop divides by zero
and no bill naming `RSW_Skewer` can ever be satisfied), `NameGenComp.cs`
(the "Roasted <first ingredient>" `TransformLabel` override, ported from
badoaks.meatonastick per STICK_FOOD_INGEST_1), `ThingDefs_Cuisine.xml`
(`RSW_Skewer` plus the ONE `RSW_RoastOnAStick` meal def, owner card
2026-10-26 "One roast-on-a-stick item"),
`RecipeDefs_Cuisine.xml` (3 RecipeDefs: 1 skewer-crafting recipe and the 2
skewer-consuming `RSW_CookRoastOnAStick`/`...4` using
`IngredientValueGetter_ExcludeSkewer`), and
`About.xml` (no ModSettings anywhere in this mod's tree -- pure content,
`suite.toggles = []`).

Every cooked-meal recipe consumes `RSW_Skewer` as a real ingredient line and
MUST use `RimMandrake.StarWars.Cuisine.IngredientValueGetter_ExcludeSkewer` or
the skewer requirement becomes unsatisfiable (see that C# file's header).
`recipes_readback` checks both shapes (skewer-crafting, skewer-consuming).

The cooked empty skewer (`RSW_CookedSkewer`), its two `RSW_CookEmptySkewer*`
recipes and its `RSW_AteEmptySkewer` taste thought were removed from the
game (owner, picks_icons_sheet_2026-10-19: "Drop from game."); this suite
no longer checks them.

WHAT IS NOT ATTEMPTED, and why -- the "Roasted <ingredient>" rename
itself: `NameGenComp.TransformLabel` only fires its interesting branch
when `CompIngredients.ingredients` is non-empty, which only happens when
the item was actually produced by a COOKING JOB that recorded real
ingredients -- a bare `jawa/spawn_batch` spawn (this suite family's usual
spawn primitive) never populates that list, so it can only ever exercise
the FALLBACK branch (`ingredients.NullOrEmpty()` -> unchanged label).
Driving a real bill through a Campfire needs `jawa/bill_add_legacy` +
`jawa/configure_bill` + `jawa/ordered_job`, the exact combination
`Droidworks/validation.py`'s own docstring names and explicitly declines
to attempt ("not attempted here") for its own, structurally simpler
memory-wipe recipe -- no suite in this family has ever exercised this
combination live, and grepping the whole `skills/rimbridge/` tree finds
neither tool documented. Guessing the call shape for a first attempt here
would be exactly the kind of invented-pass this task's rigor bar forbids.
`namegen_fallback_on_bare_spawn` below proves the FALLBACK branch only,
honestly labeled as such.

Still not proven / likely first-live-run corrections: none recorded.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MIASMA_BED_XML = os.path.join(HERE, "..", "..", "RimMandrake", "Miasma", "Defs", "ThingDefs_Buildings", "RM_DecayCell.xml")
ROTTING_BED_PATCH = os.path.join(HERE, "Patches", "RSW_RottingBed_MarshFungus.xml")


def static_checks():
    """MIASMA_ROTTING_BED_CUISINE_1, offline: the cross-tier patch applies to the real Miasma bed def exactly once
    (lxml stands in for the engine's xpath: the outer Conditional matches, comps is created if absent, and the
    spawner lands naming RSW_MarshFungus), it is not guarded by a top-level MayRequire, and the item is PlantFoodRaw
    through RSW_CultureStarters. Sanity probe: the bed def must be found first, or nothing is measured."""
    from lxml import etree
    bad = []
    bed = etree.parse(MIASMA_BED_XML)
    beds = bed.xpath('/Defs/ThingDef[defName="RM_RottingBed"]')
    if len(beds) != 1:
        return ["sanity: RM_RottingBed found %d times in %s (expected 1)" % (len(beds), MIASMA_BED_XML)]
    patch = etree.parse(ROTTING_BED_PATCH)
    top = patch.xpath("/Patch/Operation")
    if len(top) != 1 or top[0].get("Class") != "PatchOperationConditional" or top[0].get("MayRequire"):
        bad.append("rotting bed patch must be one top-level PatchOperationConditional with no MayRequire")
    if not beds[0].xpath("comps"):
        etree.SubElement(beds[0], "comps")
    spawner = patch.xpath('//li[@Class="CompProperties_Spawner"]')
    if len(spawner) != 1 or spawner[0].findtext("thingToSpawn") != "RSW_MarshFungus":
        bad.append("rotting bed patch must add exactly one CompProperties_Spawner of RSW_MarshFungus")
    if len(bed.xpath('/Defs/ThingDef[defName="RM_RottingBed"]/comps')) != 1:
        bad.append("RM_RottingBed/comps does not resolve to one node after the conditional")
    src = open(os.path.join(HERE, "..", "..", "RimMandrake", "Miasma", "Source", "RM_RottingBed.cs"), encoding="utf-8").read()
    if "base.TickRare();" not in src:
        bad.append("RM_Building_RottingBed.TickRare must call base or CompSpawner.CompTickRare never runs")
    fungus = etree.parse(os.path.join(HERE, "Defs", "RSW_MarshFungus.xml"))
    if fungus.xpath('//ThingCategoryDef[defName="RSW_CultureStarters"]/parent/text()') != ["PlantFoodRaw"]:
        bad.append("RSW_CultureStarters must be a child of PlantFoodRaw (the stick recipes filter on PlantFoodRaw)")
    cats = fungus.xpath('//ThingDef[defName="RSW_MarshFungus"]/thingCategories/li/text()')
    if cats != ["RSW_CultureStarters"]:
        bad.append("RSW_MarshFungus thingCategories = %r" % cats)
    return bad


from modcheck import Suite, ExpectationFailed, shipped_defs  # noqa: E402

suite = Suite("Cuisine")
suite.toggles = []   # no Settings.cs / ModSettings anywhere in this mod's tree

MEAL_THINGDEFS = ["RSW_RoastOnAStick"]
NAME_GEN_COMP = "RimMandrake.StarWars.Cuisine.CompProperties_NameGen"
EXCLUDE_SKEWER_GETTER = "RimMandrake.StarWars.Cuisine.IngredientValueGetter_ExcludeSkewer"


def _get_defs(t, defs, fields):
    return t.bridge_call("jawa/get_defs", defs=defs, fields=fields)


def _row_for(r, def_key):
    for d in (r or {}).get("defs", (r or {}).get("results", [])) or []:
        if d.get("defName") == def_key.split("/", 1)[-1]:
            return d
    return None


@suite.chain("no_config_or_load_errors")
def no_config_or_load_errors(t):
    """Walk step 1: no Config error naming this mod's packageId, and no
    XML error naming any of the three Defs files."""
    with t.component("no_config_or_xml_error", beyond_toggle=True):
        for tag in ("Config error in mandrake.rsw.cuisine",
                    "ThingDefs_Cuisine.xml", "RecipeDefs_Cuisine.xml"):
            r = t.bridge_call("jawa/drain_log", limit=400, contains=tag)
            if t._guard() and not (r or {}).get("success"):
                # an unreadable log is not a clean log
                raise ExpectationFailed("UNMEASURED: jawa/drain_log did not answer: %r" % (r,))
            msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
            bad = [m for m in msgs if "error" in m.lower()]
            t._record("drain_log(%r) error lines -> %r" % (tag, bad), not bad)
            if bad:
                raise ExpectationFailed(
                    "found an error-looking log line mentioning %r: %r" % (tag, bad))


@suite.chain("thingdefs_readback")
def thingdefs_readback(t):
    """RSW_Skewer's own stats and each meal ThingDef's CompProperties_NameGen
    wiring."""
    t.clear_area(size=10)
    with t.component("skewer_stats", beyond_toggle=True):
        r = _get_defs(t, "ThingDef/RSW_Skewer", "statBases,tradeability")
        row = _row_for(r, "ThingDef/RSW_Skewer")
        got = str((row or {}).get("fields", {}).get("statBases", ""))
        ok = "0.12" in got
        t._record("RSW_Skewer.statBases -> %r" % got, ok)
        if not ok:
            raise ExpectationFailed(
                "RSW_Skewer.statBases = %r, expected to contain MarketValue "
                "0.12" % got)

    for def_name in MEAL_THINGDEFS:
        with t.component("namegen_comp_%s" % def_name, beyond_toggle=True):
            r = _get_defs(t, "ThingDef/%s" % def_name, "comps,statBases")
            row = _row_for(r, "ThingDef/%s" % def_name)
            fields = (row or {}).get("fields") or {}
            got_comps = str(fields.get("comps", ""))
            ok = "NameGen" in got_comps
            t._record("%s.comps -> %r" % (def_name, got_comps), ok)
            if not ok:
                raise ExpectationFailed(
                    "%s.comps = %r, expected to contain CompProperties_"
                    "NameGen" % (def_name, got_comps))


@suite.chain("recipes_readback")
def recipes_readback(t):
    """One representative recipe per shape (module docstring): skewer-crafting and skewer-consuming (ExcludeSkewer
    getter) -- not all 15, per this family's own sampling precedent."""
    with t.component("craft_skewers_recipe", beyond_toggle=True):
        r = _get_defs(t, "RecipeDef/RSW_CraftSkewers", "recipeUsers,products")
        row = _row_for(r, "RecipeDef/RSW_CraftSkewers")
        fields = (row or {}).get("fields") or {}
        got_users = str(fields.get("recipeUsers", ""))
        got_products = str(fields.get("products", ""))
        ok = "CraftingSpot" in got_users and "10" in got_products
        t._record("RSW_CraftSkewers -> users=%r products=%r"
                  % (got_users, got_products), ok)
        if not ok:
            raise ExpectationFailed(
                "RSW_CraftSkewers did not match expected recipeUsers="
                "CraftingSpot, products RSW_Skewer=10: %r/%r"
                % (got_users, got_products))

    with t.component("skewer_consuming_recipe_uses_exclude_getter", beyond_toggle=True):
        r = _get_defs(t, "RecipeDef/RSW_CookRoastOnAStick",
                     "ingredientValueGetterClass,products")
        row = _row_for(r, "RecipeDef/RSW_CookRoastOnAStick")
        fields = (row or {}).get("fields") or {}
        got_getter = str(fields.get("ingredientValueGetterClass", ""))
        got_products = str(fields.get("products", ""))
        ok = EXCLUDE_SKEWER_GETTER in got_getter and "RSW_RoastOnAStick" in got_products
        t._record("RSW_CookRoastOnAStick -> getter=%r products=%r"
                  % (got_getter, got_products), ok)
        if not ok:
            raise ExpectationFailed(
                "RSW_CookRoastOnAStick.ingredientValueGetterClass = %r, "
                "expected to contain %r" % (got_getter, EXCLUDE_SKEWER_GETTER))


@suite.chain("skewer_spawns")
def skewer_spawns(t):
    """Walk step 5: the skewer resource actually spawns onto a real map."""
    t.clear_area(size=15)
    with t.component("skewer_stack_spawns", beyond_toggle=True):
        cells = t.spawn("RSW_Skewer", count=1, at="point")
        x, z = cells[0] if cells else t.anchor
        r = t.bridge_call("jawa/list_things", rect="%d,%d,3,3" % (x - 1, z - 1))
        rows = (r or {}).get("things") or []
        ok = any(row.get("def") == "RSW_Skewer" for row in rows)
        t._record("RSW_Skewer present at (%d,%d) -> %s" % (x, z, ok), ok)
        if not ok:
            raise ExpectationFailed(
                "no RSW_Skewer found at (%d,%d) after spawning: %r" % (x, z, rows))

        t.screenshot()


@suite.chain("namegen_fallback_on_bare_spawn")
def namegen_fallback_on_bare_spawn(t):
    """FALLBACK branch only -- see module docstring's "WHAT IS NOT
    ATTEMPTED" section for why the interesting "Roasted <ingredient>"
    rename needs a real cook job this suite does not attempt. A bare
    spawn has an empty CompIngredients.ingredients list, so
    NameGenComp.TransformLabel takes its `ingredients.NullOrEmpty()`
    early-return branch and the label should read unchanged."""
    t.clear_area(size=10)
    with t.component("unchanged_label_with_no_ingredients", beyond_toggle=True):
        cells = t.spawn("RSW_RoastOnAStick", count=1, at="point")
        x, z = cells[0] if cells else t.anchor
        r = t.bridge_call("jawa/list_things", rect="%d,%d,3,3" % (x - 1, z - 1))
        rows = (r or {}).get("things") or []
        row = next((row for row in rows if row.get("def") == "RSW_RoastOnAStick"), None)
        label = (row or {}).get("label", "")
        ok = "roasted" not in label.lower()
        t._record("bare-spawned RSW_RoastOnAStick label -> %r" % label, ok)
        if not ok:
            raise ExpectationFailed(
                "bare-spawned RSW_RoastOnAStick label = %r, expected the "
                "unchanged fallback label (not a 'Roasted ...' rename, "
                "which needs recorded ingredients this spawn never sets)"
                % label)


@suite.chain("rotting_bed_grows_marsh_fungus")
def rotting_bed_grows_marsh_fungus(t):
    """MIASMA_ROTTING_BED_CUISINE_1: with the Miasma loaded, RM_RottingBed carries the cuisine's spawner of
    RSW_MarshFungus; with it absent the bed is simply not there (UNMEASURED here, never a pass)."""
    with t.component("offline_patch_shape", beyond_toggle=True):
        bad = static_checks()
        t._record("static_checks -> %r" % bad, not bad)
        if bad:
            raise ExpectationFailed("; ".join(bad))
    with t.component("bed_spawner_live", beyond_toggle=True):
        r = _get_defs(t, "ThingDef/RM_RottingBed", "comps")
        row = _row_for(r, "ThingDef/RM_RottingBed")
        if row is None:
            # last row of the chain: upstream_failed makes the component UNMEASURED, never a pass
            t.upstream_reason = "UNMEASURED: RM_RottingBed absent from this load (Miasma not loaded) or get_defs unreadable: %r" % (r,)
            t.upstream_failed = True
            return
        got = str((row.get("fields") or {}).get("comps", ""))
        ok = "RSW_MarshFungus" in got
        t._record("RM_RottingBed.comps -> %r" % got, ok)
        if not ok:
            raise ExpectationFailed("RM_RottingBed.comps lacks the RSW_MarshFungus spawner: %r" % got)


@suite.chain("cooking_disabled_pawn_roasts_cleanly")
def cooking_disabled_pawn_roasts_cleanly(t):
    """ROAST_STICK_FIX_DISABLED_COOK_STAT_ERRORS (ported from the r12 live script roast.py): a colonist whose Cooking is
    disabled (MidworldSailor91) roasts one RSW_RoastOnAStick at a campfire. The roast must appear, and no fresh
    "disabled stat" error may name CookSpeed or FoodPoisonChance (vanilla's dev-mode ErrorOnce; fixed by the recipe XML
    and the FoodPoisonDisabledCookGuard prefix). A fresh pawn each run, so ErrorOnce cannot hide a repeat."""
    t.clear_area(size=15)
    x, z = t.anchor
    with t.component("roast_made_by_cooking_disabled_pawn", beyond_toggle=True):
        t.bridge_call("jawa/build_batch", ops="Campfire:%d,%d" % (x, z), faction="player", wipeExisting=False)
        fires = [r for r in ((t.bridge_call("jawa/list_things", defName="Campfire") or {}).get("things") or [])
                 if r.get("x") == x and r.get("z") == z]
        if not fires:
            raise ExpectationFailed("UNMEASURED: no Campfire at (%d,%d) after build_batch (SITE)" % (x, z))
        fid = fires[0]["id"]
        t.bridge_call("jawa/thing_refuel", thingId=fid, amount=50)
        t.bridge_call("jawa/spawn_batch", ops="RSW_Skewer:%d,%d,4;Meat_Cow:%d,%d,30" % (x - 2, z, x - 2, z + 1))
        pid = t.spawn_pawn("Colonist", beyond=[(x, z - 1)])
        if not pid:
            raise ExpectationFailed("UNMEASURED: spawn_pawn Colonist returned no id (SITE)")
        bs = t.bridge_call("jawa/set_pawn_backstory", pawn=pid, adulthood="MidworldSailor91")
        t._record("set_pawn_backstory %s MidworldSailor91 (Cooking disabled) -> %r" % (pid, bs), bool(bs))

        def roasts():
            rows = (t.bridge_call("jawa/list_things", defName="RSW_RoastOnAStick") or {}).get("things") or []
            return sum(int(r.get("stackCount") or 1) for r in rows if abs(r["x"] - x) < 10 and abs(r["z"] - z) < 10)
        n0 = roasts()
        t.bridge_call("jawa/bill_add", giverId=fid, recipe="RSW_CookRoastOnAStick", repeatMode="repeatcount",
                      repeatCount=1, storeMode="dropfloor")
        r = t.bridge_call("jawa/do_bill_now", pawnId=pid, billGiverId=fid, workGiverDef="RSW_DoBillsRoastCampfire")
        t._record("do_bill_now -> accepted=%r job=%r" % ((r or {}).get("accepted"), (r or {}).get("afterJobDef")),
                  bool((r or {}).get("accepted")))
        if not (r or {}).get("accepted"):
            raise ExpectationFailed("the Cooking-disabled pawn was refused the roast bill: %r" % (r,))
        n = n0
        for _ in range(20):
            t.wait_ticks(300)
            n = roasts()
            if n > n0:
                break
        t._record("RSW_RoastOnAStick near the fire %d -> %d" % (n0, n), n > n0)
        if n <= n0:
            raise ExpectationFailed("no RSW_RoastOnAStick appeared after 6000 ticks (%d -> %d)" % (n0, n))
    with t.component("no_disabled_stat_error", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=400, contains="disabled stat")
        if not (r or {}).get("success") or t._log_base is False:
            raise ExpectationFailed("UNMEASURED: jawa/drain_log or the chain-start log mark was unreadable: %r" % (r,))
        base = t._log_base or {}
        fresh = [m.get("text", "") for m in ((r or {}).get("messages") or [])
                 if m.get("text", "") not in base]
        bad = [m for m in fresh if "CookSpeed" in m or "FoodPoisonChance" in m]
        t._record("fresh 'disabled stat' lines naming CookSpeed/FoodPoisonChance -> %r" % bad, not bad)
        if bad:
            raise ExpectationFailed("disabled-stat error(s) while a Cooking-disabled pawn roasted: %r" % bad)


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)


# NORTHSTAR_PARTIAL_GAPS_FILL_1 (audit row: "salt-cured ration line ... 0 salt references; 8 meal defs / 14 recipes
# only sampled"): every def in Defs/ (rations, cure recipes, the salt-cured thought, culture starters, all meals and
# recipes) must be loaded live, labels and recipe work amounts equal to the XML. The cook-a-bill end to end stays
# uncovered (it needs a stocked kitchen fixture).
shipped_defs.add_chain(suite, __file__,
                       fields_by_type={"RecipeDef": ("label", "workAmount"),
                                       "ThingDef": ("label", "stackLimit")},
                       sanity=("RSW_SaltCuredRation_White", "RSW_CureWithAmberSalt", "RSW_AteCrystalSaltCured"),
                       min_count=30)
