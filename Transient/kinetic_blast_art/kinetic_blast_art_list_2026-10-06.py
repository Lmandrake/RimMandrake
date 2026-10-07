# Generates the art list JSON for KINETIC_BLAST_WEAPONS_1 (design/RimMandrake/kinetic_blast_weapons_design_2026-10-06.md §6).
import json, os
ITEM = "KINETIC_BLAST_WEAPONS_1"
STYLE = ("Kinetic blast weapon commission 2026-10-06, item KINETIC_BLAST_WEAPONS_1. A RimWorld weapon class whose "
         "shots throw people rather than wound them: the shared visual signature is a pale blue-white concussion "
         "ring motif and padded, heavy, spring-loaded mechanisms. Rugged frontier engineering of riveted steel, "
         "worn paint, rubber dampers and brass fittings. Single object centred on a transparent background, "
         "silhouette filling the canvas with a small margin.")
HELD = " Side view, barrel or business end pointing right (east), lying flat as a RimWorld held weapon sprite."
TOP = " Top-down three-quarter view like vanilla RimWorld buildings."
PROJ = " Small in-flight projectile sprite seen from above, pointing right (east)."
W = "Things/Item/Equipment/WeaponRanged/KineticArms/"
P = "Things/Projectile/KineticArms/"
rows = []
def r(id_, prompt, size, target=None, tex=None, extra=""):
    row = {"id": "kba_" + id_, "rimflow_item_id": ITEM, "prompt": prompt, "canvas_w": size, "canvas_h": size,
           "style_notes": STYLE + extra, "biome_neutral": "true", "priority": 40}
    if target: row["target_def"] = target
    else: row["no_subject"] = "UI icon / effect fleck for the kinetic weapon class, not a def's main graphic"
    if tex: row["target_texpath"] = tex
    rows.append(row)
r("RM_Weapon_ThudderGrenade", "Thudder grenade: a squat drum-shaped concussion grenade with a thick padded rubber impact ring around its middle, a pale blue band and a simple pull pin", 256, "RM_Weapon_ThudderGrenade", W+"RM_ThudderGrenade", " Item sprite seen from above.")
r("RM_Proj_ThudderGrenade", "Thudder grenade tumbling in flight, a squat padded drum with a pale blue band", 128, "RM_Proj_ThudderGrenade", P+"RM_ThudderGrenade", PROJ)
r("RM_Gun_PalmThumper", "Palm thumper: a stubby heavy pistol with a short wide flared bell muzzle ringed with pale blue concussion coils, chunky grip, compact and brutal", 256, "RM_Gun_PalmThumper", W+"RM_PalmThumper", HELD)
r("RM_Proj_PalmThump", "Palm thump bolt: a small pale blue-white ripple of compressed air shaped like a short crescent ring", 128, "RM_Proj_PalmThump", P+"RM_PalmThump", PROJ)
r("RM_Gun_SlamLauncher", "Slam launcher: a two-handed single-shot launcher with a fat short barrel, a padded shoulder stock and a big spring housing under the barrel, pale blue band on the muzzle", 256, "RM_Gun_SlamLauncher", W+"RM_SlamLauncher", HELD)
r("RM_Proj_SlamCharge", "Slam charge in flight: a stubby finned cylinder with a padded blunt nose and a pale blue band", 128, "RM_Proj_SlamCharge", P+"RM_SlamCharge", PROJ)
r("RM_Gun_RepulsorRifle", "Repulsor rifle: a long sleek advanced rifle whose muzzle is a stack of flat finned emitter plates glowing faint pale blue, sealed composite body, power cell in the stock", 256, "RM_Gun_RepulsorRifle", W+"RM_RepulsorRifle", HELD)
r("RM_Proj_RepulsorBolt", "Repulsor bolt: a pale blue-white cone-shaped shimmer of pressure, brightest at its leading edge", 128, "RM_Proj_RepulsorBolt", P+"RM_RepulsorBolt", PROJ)
r("RM_KickerMine", "Kicker mine, armed and half-buried: a square steel pressure plate on a heavy spring piston, a bold arrow chevron painted on top showing the direction it kicks, dirt around its edges", 256, "RM_KickerMine", "Things/Building/Security/KineticArms/RM_KickerMine", TOP+" The arrow points up (north) on the sprite.")
r("RM_Shell_Thump", "Thump shell: a mortar shell with a blunt rounded padded nose instead of a point, olive casing with a pale blue band, stencilled markings", 256, "RM_Shell_Thump", "Things/Item/Resource/Shell/RM_Shell_Thump", " Item sprite seen from above, lying on its side.")
r("RM_Bullet_Shell_Thump", "Thump mortar shell in flight, blunt padded nose, olive with a pale blue band", 128, "RM_Bullet_Shell_Thump", P+"RM_Shell_Thump", PROJ)
r("RM_Turret_PulseCannon_Top", "Pulse cannon turret head: a wide squat emitter dish of concentric steel rings with pale blue glow in the rings, armoured shroud, pointing right", 512, "RM_Turret_PulseCannon", "Things/Building/Security/KineticArms/RM_PulseCannon_Top", TOP+" Turret top only, rotates on its base.")
r("RM_Turret_PulseCannon_Base", "Pulse cannon base: a heavy square 2x2 armoured plinth with capacitor banks, power conduit sockets and shock-absorber feet", 512, "RM_Turret_PulseCannon", "Things/Building/Security/KineticArms/RM_PulseCannon_Base", TOP)
r("RM_Proj_PulseWave", "Pulse wave: a broad pale blue-white arc of compressed air, wide and thin like a ripple", 128, "RM_Proj_PulseWave", P+"RM_PulseWave", PROJ)
r("RM_Gun_GravRam", "Grav-ram: a massive two-handed gravitic weapon, a long ram-like barrel wrapped in dark gravlite panels with violet-blue glow between them, heavy brace grips", 256, "RM_Gun_GravRam", W+"RM_GravRam", HELD)
r("RM_Proj_GravRamPulse", "Grav-ram pulse: a dense violet-blue sphere of bent space with a pale ring around it", 128, "RM_Proj_GravRamPulse", P+"RM_GravRamPulse", PROJ)
r("RM_Explosion_KineticRing", "Kinetic blast ring: a single pale blue-white shockwave ring, thin and bright, with faint dust kicked outward", 128, None, "Things/Mote/KineticArms/RM_KineticRing", " Effect sprite seen from above, fully transparent centre.")
for n, d in [("ThudderGrenade","a squat padded concussion grenade with a pale blue ring"),("PalmThumper","a stubby flared-muzzle pistol with a pale blue ring"),
             ("SlamLauncher","a fat short single-shot launcher"),("RepulsorRifle","a rifle with a finned emitter muzzle and a pale blue pressure cone"),
             ("KickerMine","a square pressure plate with an arrow chevron"),("ThumpShell","a blunt-nosed mortar shell with a pale blue band"),
             ("PulseCannon","a ring-dish turret emitting a pale blue arc"),("GravRam","a gravlite-panelled ram weapon with violet glow")]:
    r("icon_"+n, f"Research and command icon: {d}, bold and readable at small size, centred on a transparent background", 128, None, "UI/Icons/KineticArms/"+n, " Icon, slightly stylised for legibility at 32 px but in the same painted register.")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kinetic_blast_art_list_2026-10-06.json")
json.dump(rows, open(out, "w"), indent=1)
print(len(rows), out)
