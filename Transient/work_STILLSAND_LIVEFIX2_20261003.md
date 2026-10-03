# Stillsand live fix 2
started
- SunLance: invalid <minifiable> replaced by <minifiedDef>MinifiedThing</minifiedDef> (vanilla Turret_* form, Buildings_Security.xml). No other <minifiable> in Stillsand Defs. RM_OldLineTurret config error is outside Stillsand (not touched).
- Cause of gale/eruption/devil dry-run failures: live fire_incident returns success=False with canFireNow=False; _ok raised. Added _dry_fire in validation.py (accepts any reply carrying canFireNow); eruption now reaches its UNMEASURED branch, gale/devil off arms read False as PASS. selftest fake now mimics success=False.
