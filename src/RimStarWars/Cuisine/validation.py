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
(`RSW_Skewer` plus the 8 `MealCookedIngredientless`-parented meal defs),
`RecipeDefs_Cuisine.xml` (14 RecipeDefs: 2 skewer-free meat recipes using
plain `IngredientValueGetter_Nutrition`, 1 skewer-crafting recipe, and 10
skewer-consuming recipes using `IngredientValueGetter_ExcludeSkewer`),
`ThoughtDefs_Cuisine.xml` (`RSW_AteEmptySkewer`, -6 mood for a day), and
`About.xml` (no ModSettings anywhere in this mod's tree -- pure content,
`suite.toggles = []`).

WHY TWO DIFFERENT `ingredientValueGetterClass` VALUES APPEAR ACROSS THE 14
RECIPES, and why this suite checks both: `RSW_CookMeatOnAStick`/
`RSW_CookMeatOnAStickBulk` need no skewer at all (the file's own comment:
"Base: meat only, no skewer resource required") and use plain
`IngredientValueGetter_Nutrition`; every OTHER cooked-meal recipe consumes
`RSW_Skewer` as a real ingredient line and MUST use
`RimMandrake.StarWars.Cuisine.IngredientValueGetter_ExcludeSkewer` or the
skewer requirement becomes unsatisfiable (module docstring's own C#
comment, verified against `WorkGiver_DoBill.
TryFindBestBillIngredientsInSet_AllowMix`'s division). `recipes_readback`
below checks a representative recipe from each of the three shapes
(meat-only, skewer-crafting, skewer-consuming), not all 14 -- enough to
catch a whole-file load break without being a rubber stamp, per this
suite family's own sampling precedent (PawnFlavor's backstory sample).

MOOD THOUGHT COVERAGE -- `jawa/pawn_thoughts` IS A REAL, CONFIRMED-LIVE
CHANNEL, contrary to what a shallow read of Ninefold/validation.py's own
docstring might suggest. Ninefold's "MOOD has NO read-back channel
anywhere" finding is specifically about a PERIODIC MOOD-SHIFT SCALAR
(`moodWalkMultiplier`'s tick-driven walk) -- a genuinely different
question from "does a discrete ThoughtDef appear in a pawn's active
thoughts", which `jawa/pawn_thoughts` answers directly and which
`Droidworks/validation.py` already drives live (`mood_penalty_nearby`,
checking for `RSW_DW_NearBoltedDroid` in the returned `thoughts[].def`
list). `eating_empty_skewer_applies_mood_thought` below uses the exact
same call shape to check for `RSW_AteEmptySkewer`.

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

Still not proven / likely first-live-run corrections:
  1. `eating_empty_skewer_applies_mood_thought`'s `wait_ticks` sizing for
     an `Ingest` job to complete and its thought to register has no
     precedent in this suite family (no other suite drives a plain
     `Ingest` job) -- sized generously (300 ticks) but untested at this
     specific mechanism.
  2. Lowering the eater's Food need first (`jawa/pawn_need` action="need")
     mirrors Droidworks' own precedent for making a needs-driven job
     realistic, not a confirmed requirement for a FORCED `Ingest` job to
     be accepted.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("Cuisine")
suite.toggles = []   # no Settings.cs / ModSettings anywhere in this mod's tree

MEAL_THINGDEFS = [
    "RSW_MeatOnAStick", "RSW_VegOnAStick", "RSW_FungusOnAStick",
    "RSW_LittleMeatOnAStick", "RSW_BlendOnAStick", "RSW_FruitOnAStick",
]
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
                    "ThingDefs_Cuisine.xml", "RecipeDefs_Cuisine.xml",
                    "ThoughtDefs_Cuisine.xml"):
            r = t.bridge_call("jawa/drain_log", limit=400, contains=tag)
            msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
            bad = [m for m in msgs if "error" in m.lower()]
            t._record("drain_log(%r) error lines -> %r" % (tag, bad), not bad)
            if bad:
                raise ExpectationFailed(
                    "found an error-looking log line mentioning %r: %r" % (tag, bad))


@suite.chain("thingdefs_readback")
def thingdefs_readback(t):
    """RSW_Skewer's own stats, each meal ThingDef's CompProperties_NameGen
    wiring, and RSW_CookedSkewer's tasteThought link to the mood thought
    this suite checks live in `eating_empty_skewer_applies_mood_thought`."""
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

    with t.component("cooked_skewer_taste_thought", beyond_toggle=True):
        r = _get_defs(t, "ThingDef/RSW_CookedSkewer", "ingestible")
        row = _row_for(r, "ThingDef/RSW_CookedSkewer")
        got = str((row or {}).get("fields", {}).get("ingestible", ""))
        ok = "RSW_AteEmptySkewer" in got
        t._record("RSW_CookedSkewer.ingestible -> %r" % got, ok)
        if not ok:
            raise ExpectationFailed(
                "RSW_CookedSkewer.ingestible = %r, expected to contain "
                "tasteThought RSW_AteEmptySkewer" % got)


@suite.chain("recipes_readback")
def recipes_readback(t):
    """One representative recipe per shape (module docstring): meat-only
    (no skewer), skewer-crafting, and skewer-consuming (ExcludeSkewer
    getter) -- not all 14, per this family's own sampling precedent."""
    with t.component("meat_only_recipe_no_skewer_getter", beyond_toggle=True):
        r = _get_defs(t, "RecipeDef/RSW_CookMeatOnAStick",
                     "recipeUsers,ingredientValueGetterClass,products")
        row = _row_for(r, "RecipeDef/RSW_CookMeatOnAStick")
        fields = (row or {}).get("fields") or {}
        got_users = str(fields.get("recipeUsers", ""))
        got_getter = str(fields.get("ingredientValueGetterClass", ""))
        got_products = str(fields.get("products", ""))
        ok = ("Campfire" in got_users and "IngredientValueGetter_Nutrition" in got_getter
              and "RSW_MeatOnAStick" in got_products)
        t._record("RSW_CookMeatOnAStick -> users=%r getter=%r products=%r"
                  % (got_users, got_getter, got_products), ok)
        if not ok:
            raise ExpectationFailed(
                "RSW_CookMeatOnAStick did not match expected recipeUsers="
                "Campfire, getter=IngredientValueGetter_Nutrition, "
                "products contains RSW_MeatOnAStick: %r/%r/%r"
                % (got_users, got_getter, got_products))

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
        r = _get_defs(t, "RecipeDef/RSW_CookVegOnAStick",
                     "ingredientValueGetterClass,products")
        row = _row_for(r, "RecipeDef/RSW_CookVegOnAStick")
        fields = (row or {}).get("fields") or {}
        got_getter = str(fields.get("ingredientValueGetterClass", ""))
        got_products = str(fields.get("products", ""))
        ok = EXCLUDE_SKEWER_GETTER in got_getter and "RSW_VegOnAStick" in got_products
        t._record("RSW_CookVegOnAStick -> getter=%r products=%r"
                  % (got_getter, got_products), ok)
        if not ok:
            raise ExpectationFailed(
                "RSW_CookVegOnAStick.ingredientValueGetterClass = %r, "
                "expected to contain %r" % (got_getter, EXCLUDE_SKEWER_GETTER))


@suite.chain("thoughtdef_readback")
def thoughtdef_readback(t):
    """RSW_AteEmptySkewer's own stat numbers, read directly off the def --
    the structural half of `eating_empty_skewer_applies_mood_thought`'s
    live proof below."""
    with t.component("ate_empty_skewer_stats", beyond_toggle=True):
        r = _get_defs(t, "ThoughtDef/RSW_AteEmptySkewer", "durationDays,stages")
        row = _row_for(r, "ThoughtDef/RSW_AteEmptySkewer")
        fields = (row or {}).get("fields") or {}
        got_dur = str(fields.get("durationDays", ""))
        got_stages = str(fields.get("stages", ""))
        ok = got_dur == "1" and "-6" in got_stages
        t._record("RSW_AteEmptySkewer -> durationDays=%r stages=%r"
                  % (got_dur, got_stages), ok)
        if not ok:
            raise ExpectationFailed(
                "RSW_AteEmptySkewer durationDays=%r stages=%r, expected "
                "durationDays=1 and a stage containing -6" % (got_dur, got_stages))


@suite.chain("skewer_and_cooked_skewer_spawn")
def skewer_and_cooked_skewer_spawn(t):
    """Walk steps 5-6: both resources actually spawn onto a real map."""
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

    with t.component("cooked_skewer_spawns", beyond_toggle=True):
        cells = t.spawn("RSW_CookedSkewer", count=1, at="point")
        x, z = cells[0] if cells else t.anchor
        r = t.bridge_call("jawa/list_things", rect="%d,%d,3,3" % (x - 1, z - 1))
        rows = (r or {}).get("things") or []
        ok = any(row.get("def") == "RSW_CookedSkewer" for row in rows)
        t._record("RSW_CookedSkewer present at (%d,%d) -> %s" % (x, z, ok), ok)
        if not ok:
            raise ExpectationFailed(
                "no RSW_CookedSkewer found at (%d,%d) after spawning: %r" % (x, z, rows))
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
        cells = t.spawn("RSW_MeatOnAStick", count=1, at="point")
        x, z = cells[0] if cells else t.anchor
        r = t.bridge_call("jawa/list_things", rect="%d,%d,3,3" % (x - 1, z - 1),
                          fields="label")
        rows = (r or {}).get("things") or []
        row = next((row for row in rows if row.get("def") == "RSW_MeatOnAStick"), None)
        label = (row or {}).get("label", "")
        ok = "roasted" not in label.lower()
        t._record("bare-spawned RSW_MeatOnAStick label -> %r" % label, ok)
        if not ok:
            raise ExpectationFailed(
                "bare-spawned RSW_MeatOnAStick label = %r, expected the "
                "unchanged fallback label (not a 'Roasted ...' rename, "
                "which needs recorded ingredients this spawn never sets)"
                % label)


@suite.chain("eating_empty_skewer_applies_mood_thought")
def eating_empty_skewer_applies_mood_thought(t):
    """Real behavioral proof of RSW_AteEmptySkewer via `jawa/pawn_thoughts`
    -- module docstring's note on why this IS a grounded, live-confirmed
    channel (Droidworks/validation.py already drives it), distinct from
    Ninefold's own "no mood read-back" finding about a different, scalar
    mechanic."""
    t.clear_area(size=12)
    x, z = t.anchor
    cells = t.spawn("RSW_CookedSkewer", count=1, at="point")
    sx, sz = cells[0] if cells else (x, z)
    eater = t.spawn_pawn("Colonist", hostile=False)

    with t.component("ate_empty_skewer_thought_applied", beyond_toggle=True):
        t.bridge_call("jawa/pawn_need", pawn=eater, action="need",
                      need="Food", level=0.1)

        things = t.bridge_call("jawa/list_things", rect="%d,%d,3,3" % (sx - 1, sz - 1))
        rows = (things or {}).get("things") or []
        skewer_id = next((row.get("id") for row in rows
                          if row.get("def") == "RSW_CookedSkewer"), None)
        if not skewer_id:
            raise ExpectationFailed(
                "could not resolve RSW_CookedSkewer's thingId from "
                "jawa/list_things: %r" % rows)

        r = t.bridge_call("jawa/ordered_job", pawnId=eater, jobDef="Ingest",
                          targetAId=skewer_id, waitTicks=60)
        if not (r or {}).get("accepted"):
            raise ExpectationFailed(
                "jawa/ordered_job(Ingest, RSW_CookedSkewer) was not "
                "accepted: %r" % r)

        t.wait_ticks(300)

        thoughts = t.bridge_call("jawa/pawn_thoughts", pawn=eater)
        defs = [th.get("def") for th in ((thoughts or {}).get("thoughts") or [])]
        ok = "RSW_AteEmptySkewer" in defs
        t._record("pawn_thoughts(%s) -> %r" % (eater, defs), ok)
        if not ok:
            raise ExpectationFailed(
                "eater has no RSW_AteEmptySkewer thought after eating a "
                "RSW_CookedSkewer: %s" % defs)
        t.screenshot()
