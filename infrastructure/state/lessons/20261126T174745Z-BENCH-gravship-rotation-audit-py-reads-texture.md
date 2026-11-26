gravship_rotation_audit.py reads texture files, so on a slim clone (no PNGs) it calls every listed defect 'STALE ... no longer a defect' and the owed defects look fixed. Make the clone full (scratch_clone.py shape . --full) before trusting any rotation-audit row; measured 2026-11-26: 24 STALE on slim, 0 problems and every defect still present on full.
item: ASTEROID_DESERT_ORES_1
home: infrastructure/state/facts/instrument_traps.md
