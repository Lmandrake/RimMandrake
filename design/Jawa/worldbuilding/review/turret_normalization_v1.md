# Turret normalization v1 — worksheet (PROPOSAL, not yet patched)

Generated 2026-08-29 by BENCH from `turret_register.json` (56-def canon roster,
frozen 213032f2) under the owner's four rulings of this sitting:

1. **Per-volley**: a turret's full burst delivers anchor × multiplier; per-shot = volley ÷ burstCount.
2. **Both directions**: over-doctrine turrets come DOWN.
3. **Blast-class** (explosive ordnance): volley damage = anchor × squares, blast radius × side
   (damage·area = squares², the doctrine total); radius capped at 14.9, remainder spills into damage.
4. **Fiat anchors**: living/bio = 25 (acid spewer), tesla arc = 20 (chain tesla gun), gravitic = 3 (grav blaster, measured).
   Gravitic shockwaves keep their radius (it is their identity) and use the direct rule.
   CONTROL rows (stun/EMP) are proposed LINEAR (anchor × squares) — durations don't square well. NOT yet ratified.

Q-flags in the last column are the open bench questions. Vehicle when ratified:
a generated patch beside the armoury ladder, `src/Jawa/Jawa_Armoury` pattern.

| defName | size | user | rule | anchor | current dmg×burst | proposed | Δ volley | retype | rename | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| AA_FoamBelcher | 1x1 | The Assailant's flesh (anomaly) | EXEMPT | —  | 9999×41 | exempt |  |  |  |  |
| AB_Turret_Propane | 1x1 | Junkers | DIRECT | Plasma Projector 33 | 2×1 | 33×1 (volley 33) | 16.5× |  |  | owner note 'BIG flamer' rework may change size — number tracks current 1x1 |
| DetColumnMod | 1x1 | Jawa Trade Moot | BLAST | AA rocket 140 | 250×1 r3.9 | 140×1 (volley 140) r3.9 | ÷1.8 |  |  | Q-TRAP: trap column — exempt as trap, or take 250→140? |
| EMPColumnMod | 1x1 | Jawa Trade Moot | CONTROL | chain tesla gun 20 | 30×1 r4.9 | 20×1 (volley 20) | ÷1.5 | Stun → EMP | ion surge column | owner note: rework to ion effect |
| FlameColumnMod | 1x1 | Jawa Trade Moot | BLAST | Plasma Projector 33 | 120×1 r3.9 | 33×1 (volley 33) r3.9 | ÷3.6 |  |  | Q-TRAP: 120→33 guts a keep — exempt traps? |
| OuterRim_LightIonCannon | 1x1 | Galactic Empire | DIRECT | wrist blaster (ion) 5 | 10×2 | 2×2 (volley 5) | ÷4.0 |  |  | Q-ION: anchor 5 (same def) vs heavy ion rifle 9 |
| OuterRim_LightLaserCannon_Corellia | 1x1 | Common / multiple | DIRECT | blaster cannon 69 | 200×4 | 17×4 (volley 69) | ÷11.6 |  |  |  |
| OuterRim_LightLaserCannon_Coruscant | 1x1 | Common / multiple | DIRECT | blaster cannon 69 | 200×4 | 17×4 (volley 69) | ÷11.6 |  |  |  |
| OuterRim_LightLaserCannon_Tatooine | 1x1 | Common / multiple | DIRECT | blaster cannon 69 | 200×4 | 17×4 (volley 69) | ÷11.6 |  |  |  |
| OuterRim_PTowerTurret | 1x1 | Common / multiple | DIRECT | blaster cannon 69 | 200×1 | 69×1 (volley 69) | ÷2.9 |  |  |  |
| Turret_AutoChargeBlaster_OP | 1x1 | Free Droid Enclaves | HOLD | Infinity Gun 60 | 187×10 | HOLD (doctrine would say volley 60) |  |  |  | Q-ARCHO: doctrine says 60-volley (6/shot ×10) — archotech fiat exemption instead? |
| Turret_BeamRepeater | 1x1 | Hutt Cartel | HOLD | unique beam repeater 64 | 64×30 | HOLD (doctrine would say volley 64) |  |  |  | Q-BEAM: burst 30 → 2/shot under per-volley; cut burst or rework (state=rework already) |
| Turret_FoamTurret | 1x1 | Common / multiple | EXEMPT | —  | 9999×41 | exempt |  |  |  |  |
| VFEI2_Thornspitter | 1x1 | Geonosian Foundry Hive | DIRECT | FIAT bio 25 | 86×1 | 25×1 (volley 25) | ÷3.4 |  |  |  |
| VFES_Complex_GraserCannon | 1x1 | Hutt Cartel | UNMEAS | salvaged laser sniper 39 | ?×8 | target volley 39 (UNMEASURED current) |  |  |  | damage in C#/unread — patch pass reads mod XML |
| VFES_Complex_HeavyIncineratorComplex | 1x1 | Hutt Cartel | UNMEAS | Plasma Projector 33 | ?×1 | target volley 33 (UNMEASURED current) |  |  |  | damage in C#/unread — patch pass reads mod XML |
| VFES_Turret_Flame | 1x1 | Wildsteam Clan | DIRECT | Plasma Projector 33 | 12×1 | 33×1 (volley 33) | 2.8× |  |  | still UNDECIDED keep (register open question) |
| VFES_Turret_Searchlight | 1x1 | Common / multiple | EXEMPT | —  | ?×1 | exempt |  |  |  |  |
| AA_BlackDefiler | 2x2 | Geonosian Foundry Hive | BLAST | FIAT bio 25 | 107×1 r3.9 | 100×1 (volley 100) r7.8 | ÷1.1 |  |  |  |
| DP_Automortar | 2x2 | Hutt Cartel | BLAST | AA rocket 140 | ?×1 r3.0 | 560×1 (volley 560) r6.0 |  |  |  | shell-fed: clone shell if shared |
| GTbc_GravliteDefenseTurret | 2x2 | Cradle / Rakatan ruins | EXEMPT | —  | ?×1 | exempt |  |  |  | interceptor — no ground damage |
| OuterRim_MediumLaserCannon | 2x2 | Galactic Empire | DIRECT | blaster cannon 69 | 200×6 | 184×6 (volley 1104) | ÷1.1 |  |  |  |
| OuterRim_ProtonMortar | 2x2 | Deepwater Compact | BLAST | AA rocket 140 | ?×1 r5.9 | 560×1 (volley 560) r11.8 |  |  |  | shell-fed |
| OuterRim_Turbolaser | 2x2 | Galactic Empire | DIRECT | blaster cannon 69 | 2000×2 | 552×2 (volley 1104) | ÷3.6 |  |  |  |
| RN2SWGun_EWeb_MG | 2x2 | Galactic Empire | DIRECT | blaster cannon 69 | 14×3 | 368×3 (volley 1104) | 26.3× | Bullet → blaster | E-Web repeating blaster | Q-EWEB: lore says repeating blaster, fires Bullet 14 |
| Turret_Atomiser | 2x2 | Junkers | DIRECT | salvaged laser sniper 39 | 86×1 | 624×1 (volley 624) | 7.3× |  | atomiser beam turret |  |
| Turret_AutoChargeBlaster | 2x2 | Forgotten Arsenal (mech) | HOLD | Infinity Gun 60 | 15×9 | HOLD (doctrine would say volley 960) |  |  |  | UNDECIDED — is this the owner's 'auto turret' cut? (register open question) |
| Turret_AutoInferno | 2x2 | Forgotten Arsenal (mech) | BLAST | Plasma Projector 33 | ?×1 r2.4 | 132×1 (volley 132) r4.8 |  |  |  | shell-fed |
| Turret_AutoMortar | 2x2 | Forgotten Arsenal (mech) | BLAST | AA rocket 140 | ?×1 r2.9 | 560×1 (volley 560) r5.8 |  |  |  | shell-fed |
| Turret_GravBlaster | 2x2 | Cradle / Rakatan ruins | DIRECT | grav blaster 3 | 7×1 r7.5 | 48×1 (volley 48) | 6.9× |  | grav shockwave turret | shockwave radius is its identity — radius kept |
| Turret_RocketswarmLauncher | 2x2 | Junkers | BLAST | AA rocket 140 | 24×12 r2.9 | 47×12 (volley 560) r5.8 | 1.9× |  |  |  |
| Turret_Sludger | 2x2 | Junkers | CONTROL | stun carbine 25 | ?×1 | 100×1 (volley 100) |  |  | sludge sprayer | Stun 0 now; rework row — needs a real effect at bench |
| Turret_Sniper | 2x2 | Homestead Defense League | DIRECT | Infinity Gun 60 | 200×1 | 960×1 (volley 960) | 4.8× |  |  |  |
| Turret_Vaporiser | 2x2 | Junkers | HOLD | salvaged laser sniper 39 | 86×180 | HOLD (doctrine would say volley 624) |  |  | vaporiser beam turret | Q-BEAM: burst 180 → 4/shot under per-volley; cut burst instead? |
| Turret_Zapper | 2x2 | Junkers | DIRECT | salvaged laser sniper 39 | 97×1 | 624×1 (volley 624) | 6.4× |  | scrap beam zapper | zapper name implies electric, deals Burn |
| VFEI2_Thornworm | 2x2 | Geonosian Foundry Hive | DIRECT | FIAT bio 25 | 86×3 | 133×3 (volley 400) | 1.6× |  |  |  |
| VFEI2_Vilelobber | 2x2 | Geonosian Foundry Hive | BLAST | FIAT bio 25 | 86×1 r3.9 | 100×1 (volley 100) r7.8 | 1.2× |  |  |  |
| VFES_Turret_Ballista | 2x2 | Deep Desert Tribes | DIRECT | Huge Javelin 50 | 278×1 r1.9 | 800×1 (volley 800) | 2.9× |  |  |  |
| VFES_Turret_ChargeRailgun | 2x2 | Ascendant Helix | HOLD | Infinity Gun 60 | 187×3 | HOLD (doctrine would say volley 960) |  |  | helical charge railgun | Q-HELIX: owner wants better than bullets — arc/burn/kept-kinetic? |
| VFES_Turret_TeslaBlaster | 2x2 | Ascendant Helix | CONTROL | chain tesla gun 20 | 10×1 | 80×1 (volley 80) | 8.0× | Smoke → EMP arc | tesla arc projector | deals Smoke 10 today — plain wrong |
| BigLaserCannon | 3x3 | Cradle / Rakatan ruins | UNMEAS | salvaged laser sniper 39 | ?×1 | target volley 3159 (UNMEASURED current) |  |  | ancient beam cannon | Rakatan; damage unread offline |
| DrillTurret | 3x3 | Junkers | EXEMPT | —  | ?×1 | exempt |  |  |  |  |
| GTbc_HugeGravBlaster | 3x3 | Cradle / Rakatan ruins | DIRECT | grav blaster 3 | 4×6 r12.5 | 40×6 (volley 243) | 10.1× |  |  | shockwave — radius kept |
| OuterRim_AnaxesTurret | 3x3 | Galactic Empire | DIRECT | blaster cannon 69 | 200×4 | 1397×4 (volley 5589) | 7.0× |  |  |  |
| OuterRim_HeavyImperialTurbolaser | 3x3 | Galactic Empire | DIRECT | blaster cannon 69 | 2000×2 r1.9 | 2794×2 (volley 5589) | 1.4× |  |  |  |
| OuterRim_HeavyIonCannon | 3x3 | Galactic Empire | DIRECT | wrist blaster (ion) 5 | 20×2 | 202×2 (volley 405) | 10.1× |  |  | Q-ION anchor |
| OuterRim_HeavyLaserCannon | 3x3 | Galactic Empire | DIRECT | blaster cannon 69 | 200×6 | 932×6 (volley 5589) | 4.7× |  |  |  |
| OuterRim_HeavyTurbolaser | 3x3 | Galactic Empire | DIRECT | blaster cannon 69 | 2000×2 r1.9 | 2794×2 (volley 5589) | 1.4× |  |  | near-duplicate of heavy imperial turbolaser (state=rework) |
| OuterRim_ProtonArtillery | 3x3 | Galactic Empire | BLAST | AA rocket 140 | ?×1 r7.9 | 3188×1 (volley 3188) r14.9 |  |  |  | shell-fed |
| VGE_AnticraftCaster | 3x3 | Gravship (the Utinni) | HOLD | —  | 86×20 | HOLD |  |  |  | anticraft showpiece (owner-filed) — hold for bench |
| VGE_GaussGun | 3x3 | Junkers | BLAST | AA rocket 140 | 161×1 r3.9 | 1260×1 (volley 1260) r11.7 | 7.8× |  |  |  |
| VGE_HeavyChargeAnnihilator | 3x3 | Cradle / Rakatan ruins | DIRECT | Infinity Gun 60 | 15×36 | 135×36 (volley 4860) | 9.0× |  |  |  |
| VGE_JavelinPod | 3x3 | Junkers | BLAST | AA rocket 140 | 118×6 r2.9 | 210×6 (volley 1260) r8.7 | 1.8× |  |  |  |
| GTbc_GravRailArtillery | 5x5 | Forsaken vaults | BLAST | AA rocket 140 | 280×1 r8.9 | 31219×1 (volley 31219) r14.9 | 111.5× |  |  |  |
| VGE_MassDriver | 5x5 | Galactic Empire | BLAST | AA rocket 140 | 50×3 r4.9 | 3154×3 (volley 9463) r14.9 | 63.1× |  |  |  |
| GTbc_TheSingularityCannon | 7x7 | Forsaken vaults | BLAST | AA rocket 140 | 308×1 r6.9 | 72085×1 (volley 72085) r14.9 | 234.0× |  |  |  |
