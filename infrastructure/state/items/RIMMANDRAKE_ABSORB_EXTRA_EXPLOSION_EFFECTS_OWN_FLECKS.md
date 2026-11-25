## spec
**2026-11-24: the design of record is `design/specs/2026-11-24-knockback-blast-show/design.md`**, and this is work of
Design Version 0.2.0 (the nine `blast_show_*` bars in `design/concepts/ExplosiveKnockback/record.json`). Owner, 2026-11-24
(OWNER:1795565769863524396): "Our own blast show YES. They look horrible right now. Let's drop all those mods and replace
them with SO MUCH BETTER stuff. Screen shake, bright fiery explosions. Air distortion ripples. Proportional to the damage
done. Realistic and wonderful. Smoke that looks like smoke, not rotating cartoon cotton. Ugly crater scars that look like
ugly crater scars. Black soot like Pyrelands (black paint left on things). Soot on affected pawns."
Where the text below differs from the design, the design holds. Two points changed:
- Point 4 below is void. His word of 2026-11-24 drops all three explosion-visual mods (Extra Explosion Effects, Better
  Explosions, Dynamic Effects Forge), so our show is the only show and no stacking with a kept mod is designed or proven.
- Point 3's two switches become one on/off per part of the show and one strength slider for the screen shake (the design,
  §Mod Settings).

The first text of this item, 2026-11-13:

Owner by card, 2026-11-12 ~4:5x PM PST (ledger note on RIMMANDRAKE_DECIDE_EXPLOSION_MODS_KEEP_ABSORB, OWNER tsn 1794530931586663595): Extra Explosion Effects -> "Absorb the idea into Knockback". The idea, not the mod: Explosive Knockback draws its own bigger, showier blasts with our own flecks and art; nothing of Keshash's code or textures is copied.

What the donor does (design/RimMandrake/explosion_mods_characterized_2026-11-12.md, section 1): a Postfix on GenExplosion.DoExplosion adds, for Bomb blasts, extra blast flecks, lingering smoke, dirt or stone debris, soot, a crater and orange sparks; for big blasts (damage over 300 or radius 2 or more) a shockwave and screen quake; for Stun, sparks and ripples. It changes no damage, radius or trigger.

Build in ExplosiveKnockback:
1. Our own FleckDefs (defName RM_KnockbackBlast*, at least debris, smoke, soot/scorch, sparks) with our own textures under ExplosiveKnockback/Textures; art goes through the art pipeline and its judge (rimworld-art-evaluation), never donor art.
2. A Harmony hook at the start of an explosion (Explosion.StartExplosion or GenExplosion.DoExplosion) that spawns them; visuals only, no damage, radius or trigger change, and no effect on the throw.
3. Mod Settings: `blastShow` (on by default) and `blastShowBig` for the shockwave/quake branch (on by default), saved and drawn; all off = today's look.
4. Kept mods stay (owner card 2026-11-12 ~5:2x PM PST: Better Explosions and Dynamic Effects Forge "Keep both for good"): our show must sit beside Forge's (Forge sets doVisualEffects=false and draws its own) without doubling; decide the stacking in the design, and prove it on one live blast with both loaded.
5. After it ships, drop Extra Explosion Effects from the test lists (a mod-list change, not a code one).

Owner, 2026-11-12 5:36 PM PST: "I can already certify that I like how they look, no test needed." That struck the owed look of the KEPT mods; it does not certify art not yet drawn, so our new flecks go through the art judge.

Acceptance test, 2026-11-24: the build stage grows `proof/absorb_blast_show_check.py` into T_BLAST_SHOW_OFFLINE, one line
per part of the 0.2.0 set in the design (§The 0.2.0 set), each seen red first; the live scene is sc_blast_show; the look is
the art judge's call. The check as first filed stays the base (red today on A1, A3, A4, A5); its line A4 (`blastShow` and
`blastShowBig`) is replaced by the design's switches.

Acceptance test as first filed: `python3 src/RimMandrake/ExplosiveKnockback/proof/absorb_blast_show_check.py`, exit 0 with "PASS absorb blast show: 0 failing line(s)" (checks A1-A6: >= 4 own FleckDefs, textures resolve under EK, a StartExplosion/DoExplosion HarmonyPatch, `blastShow` and `blastShowBig` saved and drawn, no donor name). Watched failing on c20328a876 (4 failing lines: A1, A3, A4, A5). Its green side is unproven (no build exists to pass it); the look is a judge agent's call and a live blast, not this script.
