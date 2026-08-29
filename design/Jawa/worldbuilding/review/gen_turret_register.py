#!/usr/bin/env python3
"""Generate turret_register.html (review sheet) + turret_register.json (prefill).

Reads Transient/turret_data.json (stats+thumbs, rebuilt any time from the live
capture by the extraction steps recorded in TURRET_ROSTER_CURATION_1) and emits:
  - turret_register.json   lean prefill/register, committed (no thumbs)
  - turret_register.html   self-contained dark sheet, thumbs embedded

Regenerating the SHEET is always safe — it never touches the decisions file.
The DECISIONS file (turret_register.decisions.json) is the owner's; nothing
here writes it.
"""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "/mnt/d/Luke/dev/Rimworld/Transient/turret_data.json"
DEC_NATIVE = r"D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\turret_register.decisions.json"
SHEET_NATIVE = r"D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\turret_register.html"

turrets = json.load(open(DATA))
T = {t["defName"]: t for t in turrets}

USERS = ["Cradle / Rakatan ruins", "Forsaken vaults", "Galactic Empire", "Jawa Trade Moot",
         "Jawa clans (player)", "Homestead Defense League", "Deep Desert Tribes", "Hutt Cartel",
         "Blackstar Company", "Ascendant Helix", "Geonosian Foundry Hive", "Junkers",
         "Deepwater Compact", "Wildsteam Clan", "Free Droid Enclaves", "Forgotten Arsenal (mech)",
         "The Assailant's flesh (anomaly)", "Gravship (the Utinni)", "Common / multiple", "Nobody (cut)"]

# group, tech, user, state, extra note   (state: keep | rework | cut | undecided)
PLAN = {
 # ── Rakatan relics ──────────────────────────────────────────────────────────
 "BigLaserCannon":            ("Rakatan Relics — light of the Builders", "ancient beam laser", "Cradle / Rakatan ruins", "rework", "INVENTED: 'big laser' reads as relic-grade; needs Rakatan reskin + label"),
 "GTbc_TheSingularityCannon": ("Rakatan Relics — light of the Builders", "gravitic singularity", "Forsaken vaults", "rework", "INVENTED: gravitics = terraformer tech; the vault superweapon"),
 "GTbc_GravRailArtillery":    ("Rakatan Relics — light of the Builders", "gravitic rail siege", "Forsaken vaults", "rework", "INVENTED: gravitics = Rakatan"),
 "GTbc_HugeGravBlaster":      ("Rakatan Relics — light of the Builders", "gravitic bolt, heavy", "Cradle / Rakatan ruins", "rework", "INVENTED: gravitics = Rakatan"),
 "GTbc_GravliteDefenseTurret":("Rakatan Relics — light of the Builders", "gravitic bolt, light", "Cradle / Rakatan ruins", "rework", "INVENTED: gravitics = Rakatan"),
 "Turret_GravBlaster":        ("Rakatan Relics — light of the Builders", "gravitic bolt, light", "Cradle / Rakatan ruins", "rework", "INVENTED: gravitics = Rakatan"),
 # ── Imperial ───────────────────────────────────────────────────────────────
 "OuterRim_MediumLaserCannon":("Imperial Emplacements — turbolaser doctrine", "blaster cannon", "Galactic Empire", "keep", ""),
 "OuterRim_Turbolaser":       ("Imperial Emplacements — turbolaser doctrine", "turbolaser", "Galactic Empire", "keep", "2000 dmg bolt — fortress killer, verify vs pawn balance"),
 "OuterRim_AnaxesTurret":     ("Imperial Emplacements — turbolaser doctrine", "turbolaser (Republic-era tower)", "Galactic Empire", "keep", "art is Republic-era; fine as older garrison stock"),
 "OuterRim_HeavyImperialTurbolaser":("Imperial Emplacements — turbolaser doctrine", "heavy turbolaser", "Galactic Empire", "keep", ""),
 "OuterRim_HeavyTurbolaser":  ("Imperial Emplacements — turbolaser doctrine", "heavy turbolaser (Separatist head art)", "Galactic Empire", "rework", "same stats as Imperial twin; art says Separatist — cut as duplicate, or reskin"),
 "OuterRim_HeavyLaserCannon": ("Imperial Emplacements — turbolaser doctrine", "heavy blaster cannon", "Galactic Empire", "keep", ""),
 "OuterRim_ProtonMortar":     ("Imperial Emplacements — turbolaser doctrine", "proton shell mortar", "Galactic Empire", "keep", ""),
 "OuterRim_ProtonArtillery":  ("Imperial Emplacements — turbolaser doctrine", "proton siege artillery", "Galactic Empire", "keep", "r500 map-wide siege piece"),
 "RN2SWGun_EWeb_MG":          ("Imperial Emplacements — turbolaser doctrine", "E-Web repeating blaster", "Galactic Empire", "keep", "INVENTED: E-Web is the iconic Imperial field gun — assigned Empire, not settlers"),
 # ── Jawa ion ───────────────────────────────────────────────────────────────
 "OuterRim_HeavyIonCannon":   ("Jawa Ion — capture, not kill", "heavy ion cannon", "Jawa Trade Moot", "rework", "INVENTED+CONTESTED: ion is the JAWA mechanic (JawaIonWeapons) — proposed as the Moot's one great emplacement rather than Imperial stock"),
 # ── Gravship ───────────────────────────────────────────────────────────────
 "VGE_PointDefenseTurret":    ("Gravship Hardpoints — the Utinni's guns", "point-defense battery", "Gravship (the Utinni)", "keep", ""),
 "VGE_GaussGun":              ("Gravship Hardpoints — the Utinni's guns", "gauss slug", "Gravship (the Utinni)", "keep", ""),
 "VGE_JavelinPod":            ("Gravship Hardpoints — the Utinni's guns", "missile pod", "Gravship (the Utinni)", "keep", ""),
 "VGE_AnticraftCaster":       ("Gravship Hardpoints — the Utinni's guns", "anticraft caster", "Gravship (the Utinni)", "keep", ""),
 "VGE_MassDriver":            ("Gravship Hardpoints — the Utinni's guns", "mass driver", "Gravship (the Utinni)", "keep", "could equally read Rakatan — the Utinni IS Rakatan-built; overlap is canon-friendly"),
 "VGE_HeavyChargeAnnihilator":("Gravship Hardpoints — the Utinni's guns", "heavy charge annihilator", "Gravship (the Utinni)", "keep", ""),
 # ── Forsaken sentinels ─────────────────────────────────────────────────────
 "Turret_AutoChargeBlaster":  ("Forsaken Sentinels — mech pattern", "mech charge blaster", "Forgotten Arsenal (mech)", "undecided", "CONTESTED: is this your 'auto turret' cut? If kept, it is Arsenal-only"),
 "Turret_AutoInferno":        ("Forsaken Sentinels — mech pattern", "mech incendiary launcher", "Forgotten Arsenal (mech)", "keep", "the closest thing to a flame turret on the large list"),
 "Turret_AutoMortar":         ("Forsaken Sentinels — mech pattern", "mech mortar", "Forgotten Arsenal (mech)", "keep", "art not extracted offline (vanilla bundle); exists in game"),
 # ── Settler iron ───────────────────────────────────────────────────────────
 "Turret_Autocannon":         ("Settler Iron — planetary ballistics", "autocannon (Earth-like rapid kinetic)", "Nobody (cut)", "cut", "CUT by the refined bullets rule: rapid Earth-like kinetic; big slow slug-throwers (sniper, mortars, gauss/mass drivers) stay"),
 "Turret_Sniper":             ("Settler Iron — planetary ballistics", "uranium slug rifle", "Homestead Defense League", "keep", ""),
 "Turret_Mortar":             ("Settler Iron — planetary ballistics", "shell mortar (manned)", "Common / multiple", "keep", "player-facing core siege — keep universal"),
 "Turret_RocketswarmLauncher":("Settler Iron — planetary ballistics", "one-shot rocket swarm", "Junkers", "keep", "junker-flavored: a welded rack of rockets"),
 "DP_Automortar":             ("Settler Iron — planetary ballistics", "automated mortar", "Hutt Cartel", "rework", "INVENTED: bought automation fits Hutt money; else cut as duplicate of auto-mortar"),
 "VFES_Turret_Ballista":      ("Settler Iron — planetary ballistics", "ballista (primitive)", "Deep Desert Tribes", "keep", "the one primitive emplacement — Tusken siege"),
 "DrillTurret":               ("Settler Iron — planetary ballistics", "mining drill (tool, not weapon)", "Jawa clans (player)", "keep", "owner-ruled IN: utility, definitely belongs"),
 # ── Exotic energy ──────────────────────────────────────────────────────────
 "Turret_Atomiser":           ("Exotic Energy — bought and jury-rigged", "matter atomiser", "Hutt Cartel", "rework", "INVENTED: exotic executive toys read as Hutt purchases"),
 "Turret_Vaporiser":          ("Exotic Energy — bought and jury-rigged", "vaporiser", "Hutt Cartel", "rework", "INVENTED: as Atomiser"),
 "Turret_Sludger":            ("Exotic Energy — bought and jury-rigged", "sludge thrower", "Junkers", "rework", "INVENTED: industrial waste weapon — junker chemistry"),
 "Turret_Zapper":             ("Exotic Energy — bought and jury-rigged", "arc zapper", "Junkers", "rework", "INVENTED: scrap-lightning"),
 "VFES_Turret_ChargeRailgun": ("Exotic Energy — bought and jury-rigged", "charge railgun", "Ascendant Helix", "keep", "few-and-excellent ultratech — Helix doctrine"),
 "VFES_Turret_TeslaBlaster":  ("Exotic Energy — bought and jury-rigged", "tesla arc", "Junkers", "rework", "INVENTED: jury-rigged arc thrower; alt: Deepwater (conductive water defense)"),
 # ── Living turrets ─────────────────────────────────────────────────────────
 "VFEI2_Vilelobber":          ("Living Turrets — hive and flesh", "bio-lobber (propose sonic rework)", "Geonosian Foundry Hive", "rework", "INVENTED: hive tech is SONIC — re-projectile to sonic to match KotORRanged_sonic identity"),
 "VFEI2_Thornworm":           ("Living Turrets — hive and flesh", "thorn spitter (propose sonic rework)", "Geonosian Foundry Hive", "rework", "INVENTED: as Vilelobber"),
 "AA_BlackDefiler":           ("Living Turrets — hive and flesh", "flesh spewer", "The Assailant's flesh (anomaly)", "rework", "INVENTED: the bioweapon's own emplacement — poison forest / mycotic jungle set-dressing"),
}

GROUP_ORDER = ["Rakatan Relics — light of the Builders", "Imperial Emplacements — turbolaser doctrine",
               "Jawa Ion — capture, not kill", "Gravship Hardpoints — the Utinni's guns",
               "Forsaken Sentinels — mech pattern", "Settler Iron — planetary ballistics",
               "Exotic Energy — bought and jury-rigged", "Living Turrets — hive and flesh",
               "Small Emplacements — keep and rework", "Small Emplacements — ancient relics",
               "Wall-mounted — class undecided", "Small Emplacements — CUT: bullets rule",
               "Small Emplacements — CUT: mod rulings and register"]

# ---- 1x1 layer (owner 2026-08-29: "eliminate any 1x1 turrets that obviously use
# bullets except for sniper turrets"). Baseline is DATA-DRIVEN: projectile
# damageDef == Bullet -> cut, unless the label says sniper. Explicit overrides below.
VFES_KEEP_1 = {"VFES_Turret_Flame"}   # pending the 4th-keep ruling; all other VFES 1x1s die with the mod ruling
PLAN_1X1 = {
 "Turret_FoamTurret":          ("Small Emplacements — keep and rework", "containment foam", "Common / multiple", "keep", "utility, not a weapon — containment"),
 "FlameColumnMod":             ("Small Emplacements — keep and rework", "flame column", "Common / multiple", "keep", "INVENTED: this covers the flamer need the large list lacks"),
 "EMPColumnMod":               ("Small Emplacements — keep and rework", "stun pulse (ion-adjacent)", "Jawa clans (player)", "rework", "INVENTED: EMP pulse reads as Jawa ion doctrine"),
 "DetColumnMod":               ("Small Emplacements — keep and rework", "cluster charge column", "Common / multiple", "undecided", "deliberately open — mine-field verb, who gets it?"),
 "DeadColumnMod":              ("Small Emplacements — keep and rework", "Deadlife dust column", "The Assailant's flesh (anomaly)", "undecided", "deliberately open — anomaly verb on a buildable column"),
 "AB_Turret_Propane":          ("Small Emplacements — keep and rework", "propane burner", "Junkers", "rework", "INVENTED: jury-rigged fire = junker chemistry"),
 "VFEI2_Thornspitter":         ("Small Emplacements — keep and rework", "thorn spitter (propose sonic rework)", "Geonosian Foundry Hive", "rework", "INVENTED: as the large living turrets — hive tech is sonic"),
 "AA_FoamBelcher":             ("Small Emplacements — keep and rework", "living foam gland", "The Assailant's flesh (anomaly)", "undecided", "living containment — flesh or hive?"),
 "OuterRim_LightIonCannon":    ("Small Emplacements — keep and rework", "light ion cannon", "Jawa Trade Moot", "keep", "ion = capture-not-kill, the Jawa identity"),
 "OuterRim_LightLaserCannon_Coruscant": ("Small Emplacements — keep and rework", "light blaster cannon", "Common / multiple", "keep", ""),
 "OuterRim_LightLaserCannon_Corellia":  ("Small Emplacements — keep and rework", "light blaster cannon", "Common / multiple", "keep", ""),
 "OuterRim_LightLaserCannon_Tatooine":  ("Small Emplacements — keep and rework", "light blaster cannon", "Homestead Defense League", "keep", "INVENTED: the Tatooine pattern belongs on moisture-farm walls"),
 "OuterRim_PTowerTurret":      ("Small Emplacements — keep and rework", "P-Tower dish (old anti-armor)", "Homestead Defense League", "keep", "INVENTED: cheap old Rebel-surplus dish — settler iron"),
 "VFES_Turret_Flame":          ("Small Emplacements — keep and rework", "flamer turret", "Common / multiple", "undecided", "OPEN: dies with the VFE-Security ruling unless named a 4th keep"),
 "Turret_AncientArmoredTurret":("Small Emplacements — ancient relics", "ancient defender", "Cradle / Rakatan ruins", "rework", "INVENTED: 'ancient' emplacements read Rakatan after the reskin"),
 "VQE_AncientShieldedTurret":  ("Small Emplacements — ancient relics", "ancient shielded turret", "Forsaken vaults", "rework", "INVENTED: as ancient defender"),
 "Turret_BeamRepeater":        ("Small Emplacements — ancient relics", "beam repeater (shield-bypass)", "Cradle / Rakatan ruins", "rework", "INVENTED: gravtech = Rakatan premise"),
 "Turret_AutoChargeBlaster_OP":("Small Emplacements — CUT: mod rulings and register", "archotech charge turret", "Nobody (cut)", "cut", "INVENTED: archotech OP one-off, wrong register"),
 "BMAD_ShrinkTurret":          ("Small Emplacements — CUT: mod rulings and register", "shrink ray", "Nobody (cut)", "cut", "INVENTED: gene-ray joke piece, wrong fiction"),
 "BMAD_GrowthTurret":          ("Small Emplacements — CUT: mod rulings and register", "growth ray", "Nobody (cut)", "cut", "INVENTED: as shrink ray"),
 "HMC_Wall_Emp_Turret":        ("Wall-mounted — class undecided", "wall EMP pulse", "Jawa clans (player)", "undecided", "EMP fits ion doctrine; the wall-mount CLASS needs a ruling"),
 "HMC_Wall_Emp_Turret_Ship":   ("Wall-mounted — class undecided", "naval wall EMP pulse", "Gravship (the Utinni)", "undecided", "as wall EMP"),
 "HMC_Wall_Foam_Turret":       ("Wall-mounted — class undecided", "wall foam sprayer", "Common / multiple", "undecided", ""),
 "HMC_Wall_Rocket_Turret":     ("Wall-mounted — class undecided", "wall rocket rack", "Junkers", "undecided", "rockets, not bullets — survives the rule, needs the class ruling"),
}
WALL_WARNING = "⚠️ wall-mounted: dev-spawning these FREE-STANDING breaks PowerNetManager (root-caused 2026-08-29 — the render-killing NRE); only judge them on a wall."

rows = []
small = json.load(open("/mnt/d/Luke/dev/Rimworld/Transient/turret_1x1.json"))
T1 = {t["defName"]: t for t in small}
for t in small:
    dn = t["defName"]
    dmg = t.get("damage"); dd = t.get("damageDef") or "?"
    eff = "%s %s dmg" % (dd, dmg if dmg not in (None, -1) else "?")
    if t.get("explosionRadius"): eff += " · blast r%.1f" % t["explosionRadius"]
    eff += " · range %s" % t.get("range")
    if t.get("burst") and (t["burst"] or 0) > 1: eff += " · burst %d" % t["burst"]
    label = str(t.get("label") or "")
    is_sniper = "sniper" in label.lower() or "sniper" in dn.lower()
    if dn in PLAN_1X1:
        grp, tech, user, state, note = PLAN_1X1[dn]
        if dn.startswith("HMC_Wall") or dn == "ShipWallMountMiniTurret":
            note = (note + " · " if note else "") + WALL_WARNING
    elif dd == "Bullet" and not is_sniper:
        grp, tech, user, state = "Small Emplacements — CUT: bullets rule", "slugthrower (bullets)", "Nobody (cut)", "cut"
        note = "CUT by the owner's rule: obviously uses bullets (no sniper exception applies)"
    elif t["mod"] == "Vanilla Furniture Expanded - Security" and dn not in VFES_KEEP_1:
        grp, tech, user, state = "Small Emplacements — CUT: mod rulings and register", "(VFE-Security)", "Nobody (cut)", "cut"
        note = "dies with the VFE-Security ruling (only railgun/ballista/tesla + the open flamer survive)"
    elif t["mod"] == "Fortifications - Industrial":
        grp, tech, user, state = "Small Emplacements — CUT: mod rulings and register", "(Fortifications)", "Nobody (cut)", "cut"
        note = "dies with the Fortifications-Industrial ruling"
    else:
        grp, tech, user, state = "Small Emplacements — keep and rework", dd, "Common / multiple", "undecided"
        note = "no rule matched — deliberately open"
    rows.append({
        "defName": dn, "label": label, "mod": t["mod"], "size": "1x1",
        "group": grp, "stats": eff, "desc": t.get("desc") or "",
        "prefill": {"tech": tech, "effect": eff, "user": user, "state": state},
        "prefillNote": note,
        "contested": ("CONTESTED" in note) or ("INVENTED" in note) or ("OPEN" in note),
    })

for dn, (grp, tech, user, state, note) in PLAN.items():
    t = T.get(dn)
    if not t:
        raise SystemExit("PLAN names %s but data lacks it" % dn)
    dmg = t.get("damage"); dd = t.get("damageDef") or "?"
    eff = "%s %s dmg" % (dd, dmg if dmg not in (None, -1) else "?")
    if t.get("explosionRadius"): eff += " · blast r%.1f" % t["explosionRadius"]
    eff += " · range %s" % t.get("range")
    if t.get("burst") and t["burst"] > 1: eff += " · burst %d" % t["burst"]
    rows.append({
        "defName": dn, "label": t["label"], "mod": t["mod"], "size": t["size"],
        "group": grp, "stats": eff, "desc": t.get("desc") or "",
        "prefill": {"tech": tech, "effect": eff, "user": user, "state": state},
        "prefillNote": note,
        "contested": ("CONTESTED" in note) or ("INVENTED" in note),
    })
rows.sort(key=lambda r: (GROUP_ORDER.index(r["group"]), r["size"], r["defName"]))

register = {
    "posture": "whitelist",
    "postureMeaning": "ALL turret sizes now in scope. A turret def not on this sheet, or on it with state=cut, is to be cut when we normalize.",
    "rulingSource": "owner at the bench, 2026-08-29",
    "rules": [
        "BULLETS RULE (owner, verbatim): 'eliminate any 1x1 turrets that obviously use bullets except for sniper turrets' — applied data-driven: projectile damageDef == Bullet -> cut; no 1x1 on the roster is a sniper, so the exception matched nothing (noted, not silently dropped)",
        "REFINED (owner, 2026-08-29, later): remove obviously Earth-like bullet versions at every size — big, slow slug-throwers are fine (the sniper rationale; mortars, gauss gun, mass driver stay; the E-Web stays because it is a Star Wars repeating blaster despite the MG name)",
    ],
    "alreadyCut": ["all VFE Props & Decor props", "all VFE Pirates", "all Fortifications-Industrial",
                   "VFE-Security except ChargeRailgun/Ballista/TeslaBlaster/(Flame? open)",
                   "BreadMoAM_Turret_LargeShotgun", "VQE_AncientSpacerAutocannon"],
    "openQuestions": [
        "Which def is the owner's 'auto turret' cut? (Turret_AutoChargeBlaster flagged undecided)",
        "VFES_Turret_Flame (1x1 flamer) — 4th VFE-Security keep, or dies with the mod cut?",
        "Wall-mounted turret CLASS (HMC walls, ship wall mounts) — keep the category at all?",
    ],
    "turrets": rows,
}
json.dump(register, open(os.path.join(HERE, "turret_register.json"), "w"), indent=1)

# ---------------------------------------------------------------- the sheet
def esc(s): return html.escape(str(s), quote=True)
cards = []
for r in rows:
    t = T.get(r["defName"]) or T1.get(r["defName"]) or {}
    img = ('<img src="data:image/png;base64,%s" alt="">' % t["thumb"]) if t.get("thumb") else '<div class="noart">art in game bundle<br>not extracted</div>'
    cards.append({**r, "img": img})

USERS_OPT = "".join('<option>%s</option>' % esc(u) for u in USERS)
ROWS_JSON = json.dumps([{k: v for k, v in c.items()} for c in cards])

page = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Turret Register — Ash'karr</title>
<style>
body{margin:0;background:#14161a;color:#e8e6e3;font:13px/1.45 system-ui,sans-serif}
header{position:sticky;top:0;z-index:20;background:#14161a;border-bottom:1px solid #2a2f37}
.hrow{display:flex;align-items:center;gap:12px;padding:10px 22px}
h1{font-size:16px;margin:0}
.sub{color:#9aa3ad;font-size:12px}
#fold{margin-left:auto;cursor:pointer;background:#0f1216;border:1px solid #2a2f37;color:#e8e6e3;border-radius:5px;padding:5px 12px;font:inherit}
body.folded #brief{display:none}
#brief{padding:2px 22px 10px;max-width:1100px}
.panel{background:#0f1216;border:1px solid #2a2f37;border-radius:5px;padding:9px 12px;margin:8px 0;font-size:12px}
.panel.warn{border-color:#7a5a1e;background:#1a150c}
.panel b{color:#ffb454}
.pathbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;background:#0f1216;border:1px solid #2a2f37;border-radius:5px;padding:9px 12px;margin:8px 0;font-size:12px}
.pathbar code{color:#cfe3ff;font-family:ui-monospace,monospace;word-break:break-all}
.pathbar button,#linkbtn,#exportbtn{cursor:pointer;background:#1d2733;border:1px solid #2f4358;color:#cfe3ff;border-radius:4px;padding:4px 10px;font:inherit}
.bar{display:flex;gap:8px;align-items:center;padding:8px 22px;flex-wrap:wrap;border-top:1px solid #20242b}
.bar select,.bar input[type=text]{background:#0f1216;border:1px solid #2a2f37;color:#e8e6e3;border-radius:4px;padding:4px 8px;font:inherit}
#counts{color:#9aa3ad;font-size:12px}
#savestate{font-size:12px;color:#8fbf8f}
#savestate.bad{color:#e08f8f}
.gh{position:sticky;z-index:10;background:#10141a;border-top:1px solid #2a2f37;border-bottom:1px solid #2a2f37;padding:6px 22px;font-size:12px;font-weight:600;color:#ffb454}
.gh.nostick{position:static}
.card{display:grid;grid-template-columns:120px 1fr 460px;gap:14px;padding:12px 22px;border-bottom:1px solid #20242b}
.card.contested{background:#171310}
.card img{max-width:110px;max-height:110px;image-rendering:auto;background:#0b0d10;border:1px solid #2a2f37;border-radius:4px}
.noart{width:110px;height:80px;border:1px dashed #2a2f37;border-radius:4px;color:#667;display:flex;align-items:center;justify-content:center;text-align:center;font-size:11px}
.t{font-weight:600}
.meta{color:#9aa3ad;font-size:11px}
.stats{color:#cfe3ff;font-size:12px;margin:2px 0}
.desc{color:#aab;font-size:11px;max-width:60ch}
.pn{color:#c9a15a;font-size:11px;margin-top:4px}
.dec{display:grid;grid-template-columns:1fr 1fr;gap:6px;align-content:start}
.dec label{font-size:10px;color:#889;display:block}
.dec input[type=text],.dec select,.dec textarea{width:100%;box-sizing:border-box;background:#0f1216;border:1px solid #2a2f37;color:#e8e6e3;border-radius:4px;padding:4px 6px;font:inherit}
.dec textarea{grid-column:1/3;min-height:34px;border-color:#3a4a3a;background:#0e130e}
.dec .full{grid-column:1/3}
.touched .dec input,.touched .dec select{border-color:#5a7}
.statesel.cut{color:#e08f8f}.statesel.keep{color:#8fbf8f}.statesel.rework{color:#e0c98f}
</style></head><body>
<header>
 <div class="hrow"><h1>Turret Register — the allowed large turrets of Ash'karr</h1>
  <span class="sub" id="counts"></span><span id="savestate">decisions not linked</span>
  <button id="linkbtn">link decisions file</button><button id="exportbtn">copy JSON</button>
  <button id="fold">▾ brief</button></div>
 <div id="brief">
  <div class="panel"><b>The ruling this records</b> (owner, 2026-08-29): <b>posture: WHITELIST, ALL turret sizes — anything not on this sheet, or marked cut, gets cut at normalization</b>. Cut already: VFE Props, VFE Pirates, Fortifications-Industrial, VFE-Security (except charge railgun / ballista / tesla blaster), the large shotgun, the ancient spacer autocannon. MiningCo drill turret stays (owner: a tool, not a weapon). <b>BULLETS RULE</b> (owner, verbatim): 1×1 turrets that obviously use bullets are cut, sniper turrets excepted — applied as projectile damageDef == Bullet; no 1×1 on the roster is a sniper, so the exception matched nothing.<br>
  <b>The three decisions per row:</b> ① what technology/damage it projects · ② how powerful / what effect · ③ who uses it. Prefilled; overrule freely — the notes you write are worth more than the agreements.</div>
  <div class="panel warn"><b>Rules the agent INVENTED (rows tinted, filter: contested):</b> ① gravitic weapons (GravTech) = Rakatan relic tech · ② the heavy ion cannon goes to the Jawa Trade Moot (ion = capture-not-kill is the Jawa identity), not the Empire · ③ E-Web assigned Imperial · ④ insect living turrets re-projectiled to SONIC to match Geonosian identity · ⑤ black defiler = the Assailant's flesh (anomaly set-dressing). None of these were asked for — each is one click to overturn.<br>
  <b>Open questions:</b> which def is your "auto turret" cut (auto CHARGE turret flagged undecided)? · does VFES_Turret_Flame (1×1 flamer, found alive) become a 4th VFE-Security keep? </div>
  <div class="panel"><b>Criterion:</b> grouped by projected TECHNOLOGY FAMILY, matched to the faction armory survey (ion=Jawa, blaster=Empire, sonic=Geonosian, mech=Arsenal, slugthrower=Homestead). This ranks coherence with existing assignments — not worth, and not your vision. Stats lines are MEASURED from the live 585 capture 2026-08-29T20-07-29Z.</div>
  <div class="pathbar"><b>Save decisions to</b> <code id="p1">%DEC%</code><button data-copy="p1">copy path</button>
   <span>the picker cannot be given a folder — copy this into its filename box</span></div>
  <div class="pathbar"><b>This sheet</b> <code id="p2">%SHEET%</code><button data-copy="p2">copy path</button></div>
 </div>
 <div class="bar">
  <input type="text" id="q" placeholder="search def / label / tech / note…">
  <select id="fgroup"><option value="">all groups</option></select>
  <select id="fstate"><option value="">all states</option><option>keep</option><option>rework</option><option>cut</option><option>undecided</option></select>
  <label><input type="checkbox" id="fcontested"> contested only</label>
  <label><input type="checkbox" id="ftouched"> my overrides only</label>
 </div>
</header>
<div id="list"></div>
<script>
const ROWS = %ROWS%;
const USERS_OPT = `%USERS_OPT%`;
const el = i => document.getElementById(i);
let dec = {};           // defName -> {tech,effect,user,state,note,touched}
let extraKeys = {};     // unknown top-level keys carried through verbatim
let handle = null, dirty = false, saveTimer = null;

// ---------- fold
const FOLDKEY='turret_sheet_folded';
function setFold(f){document.body.classList.toggle('folded',f);el('fold').textContent=f?'▸ brief':'▾ brief';try{localStorage.setItem(FOLDKEY,f?'1':'')}catch(e){};measure();}
el('fold').onclick=()=>setFold(!document.body.classList.contains('folded'));
try{setFold(localStorage.getItem(FOLDKEY)==='1')}catch(e){setFold(false)}
for(const b of document.querySelectorAll('[data-copy]'))b.onclick=async()=>{const n=el(b.dataset.copy);try{await navigator.clipboard.writeText(n.textContent);const t=b.textContent;b.textContent='copied ✓';setTimeout(()=>b.textContent=t,1200);}catch(e){const r=document.createRange();r.selectNode(n);getSelection().removeAllRanges();getSelection().addRange(r);b.textContent='press Ctrl+C';}};
function measure(){const h=document.querySelector('header').offsetHeight;for(const g of document.querySelectorAll('.gh'))g.style.top=h+'px';}
addEventListener('resize',measure);

// ---------- state seed: per-row merge, never all-or-nothing
function seed(existing){
  let kept=0, filled=0;
  for(const r of ROWS){
    const ex = existing && existing[r.defName];
    if(ex && ex.touched){ dec[r.defName]=ex; kept++; }
    else { dec[r.defName]={...r.prefill, note:'', touched:false}; filled++; }
  }
  return {kept, filled};
}
function loadLocal(){ try{return JSON.parse(localStorage.getItem('turret_dec')||'null')}catch(e){return null} }
function persistLocal(){ try{localStorage.setItem('turret_dec',JSON.stringify(dec))}catch(e){} }

// ---------- File System Access
async function idb(mode,val){return new Promise((res,rej)=>{const rq=indexedDB.open('turret_sheet',1);rq.onupgradeneeded=()=>rq.result.createObjectStore('kv');rq.onsuccess=()=>{const tx=rq.result.transaction('kv',mode==='get'?'readonly':'readwrite');const st=tx.objectStore('kv');const q=mode==='get'?st.get('handle'):st.put(val,'handle');q.onsuccess=()=>res(q.result);q.onerror=()=>rej(q.error);};rq.onerror=()=>rej(rq.error);});}
async function link(){
  try{
    handle = await showSaveFilePicker({suggestedName:'turret_register.decisions.json',types:[{accept:{'application/json':['.json']}}]});
    await idb('put',handle);
    try{const f=await handle.getFile();const txt=await f.text();if(txt.trim()){const j=JSON.parse(txt);
      for(const k of Object.keys(j)) if(k!=='decisions'&&k!=='sheetSavedAt'&&k!=='decidedCount') extraKeys[k]=j[k];
      const m=seed(j.decisions||{}); banner(`linked · kept ${m.kept} of your decisions, filled ${m.filled} from prefill`);
    }}catch(e){}
    render(); save(true);
  }catch(e){ banner('link cancelled',true); }
}
el('linkbtn').onclick=link;
(async()=>{try{const h=await idb('get');if(h){const p=await h.queryPermission({mode:'readwrite'});handle=h;
  if(p==='granted'){banner('decisions file reconnected');}else{banner('click "link decisions file" to reconnect (browser needs a gesture)',true);}
}}catch(e){}})();
function payload(){
  const decided=Object.values(dec).filter(d=>d.touched).length;
  return {...extraKeys, posture:'whitelist', sheetSavedAt:new Date().toISOString(), decidedCount:decided, decisions:dec};
}
async function save(force){
  persistLocal();
  if(!handle) { banner('decisions not linked — work is in localStorage only', true); return; }
  const decided=Object.values(dec).filter(d=>d.touched).length;
  if(!force && decided===0 && el('savestate').dataset.had>0){ banner('refusing truncating write (0 decided rows in memory)',true); return; }
  try{
    const w=await handle.createWritable(); await w.write(JSON.stringify(payload(),null,1)); await w.close();
    el('savestate').dataset.had=decided;
    banner('saved '+new Date().toLocaleTimeString()+' · '+decided+' overrides');
  }catch(e){ banner('SAVE FAILED: '+e.message,true); }
}
function queueSave(){ dirty=true; clearTimeout(saveTimer); saveTimer=setTimeout(()=>save(false),1000); }
el('exportbtn').onclick=async()=>{const s=JSON.stringify(payload(),null,1);try{await navigator.clipboard.writeText(s);banner('JSON copied');}catch(e){prompt('copy:',s);}};
function banner(msg,bad){const s=el('savestate');s.textContent=msg;s.className=bad?'bad':'';}

// ---------- render
function counts(){
  const v=Object.values(dec);
  const c=s=>v.filter(d=>d.state===s).length;
  el('counts').textContent=`${ROWS.length} turrets · keep ${c('keep')} · rework ${c('rework')} · cut ${c('cut')} · undecided ${c('undecided')} · your overrides ${v.filter(d=>d.touched).length}`;
}
const groups=[...new Set(ROWS.map(r=>r.group))];
for(const g of groups){const o=document.createElement('option');o.textContent=g;el('fgroup').appendChild(o);}
function card(r){
  const d=dec[r.defName];
  return `<div class="card ${r.contested?'contested':''} ${d.touched?'touched':''}" data-def="${r.defName}">
   <div>${r.img}<div class="meta">${r.size} · ${r.mod}</div></div>
   <div><div class="t">${r.label} <span class="meta">(${r.defName})</span></div>
     <div class="stats">${r.stats}</div>
     <div class="desc">${r.desc}</div>
     ${r.prefillNote?`<div class="pn">◆ ${r.prefillNote}</div>`:''}</div>
   <div class="dec">
     <div><label>① technology / damage</label><input type="text" data-f="tech" value="${d.tech.replace(/"/g,'&quot;')}"></div>
     <div><label>③ who uses it</label><select data-f="user">${USERS_OPT}</select></div>
     <div class="full"><label>② power / effect</label><input type="text" data-f="effect" value="${d.effect.replace(/"/g,'&quot;')}"></div>
     <div><label>state</label><select data-f="state" class="statesel ${d.state}"><option>keep</option><option>rework</option><option>cut</option><option>undecided</option></select></div>
     <div></div>
     <textarea data-f="note" placeholder="your note — worth more than agreement">${d.note||''}</textarea>
   </div></div>`;
}
function render(){
  const q=el('q').value.toLowerCase(), fg=el('fgroup').value, fs=el('fstate').value;
  const fc=el('fcontested').checked, ft=el('ftouched').checked;
  const shown=ROWS.filter(r=>{
    const d=dec[r.defName];
    if(fg&&r.group!==fg)return false;
    if(fs&&d.state!==fs)return false;
    if(fc&&!r.contested)return false;
    if(ft&&!d.touched)return false;
    if(q&&!(r.defName+' '+r.label+' '+r.stats+' '+d.tech+' '+d.user+' '+(d.note||'')+' '+r.prefillNote).toLowerCase().includes(q))return false;
    return true;});
  const gm=new Map();
  for(const r of shown){if(!gm.has(r.group))gm.set(r.group,[]);gm.get(r.group).push(r);}
  let h='';
  for(const [name,items] of gm){h+=`<div class="gh${items.length<=3?' nostick':''}">${name} · ${items.length}</div>`;h+=items.map(card).join('');}
  el('list').innerHTML=h;
  for(const c of document.querySelectorAll('.card')){
    const dn=c.dataset.def, d=dec[dn];
    const us=c.querySelector('[data-f=user]'); us.value=d.user; if(us.value!==d.user){const o=document.createElement('option');o.textContent=d.user;us.appendChild(o);us.value=d.user;}
    c.querySelector('[data-f=state]').value=d.state;
    for(const inp of c.querySelectorAll('[data-f]')){
      inp.oninput=inp.onchange=()=>{d[inp.dataset.f]=inp.value;d.touched=true;c.classList.add('touched');
        if(inp.dataset.f==='state')inp.className='statesel '+inp.value;
        counts();queueSave();};
    }
  }
  counts(); measure();
}
for(const id of ['q','fgroup','fstate','fcontested','ftouched'])el(id).oninput=render;
const local=loadLocal();
const m=seed(local||{});
if(local)banner(`localStorage: kept ${m.kept} decisions, prefill on ${m.filled}`);
render();
</script></body></html>"""
page = page.replace("%DEC%", DEC_NATIVE).replace("%SHEET%", SHEET_NATIVE)
page = page.replace("%ROWS%", ROWS_JSON).replace("%USERS_OPT%", USERS_OPT)
out = os.path.join(HERE, "turret_register.html")
open(out, "w").write(page)
print("wrote", out, len(page)//1024, "KB;", len(rows), "rows; register JSON",
      os.path.getsize(os.path.join(HERE, "turret_register.json"))//1024, "KB")
