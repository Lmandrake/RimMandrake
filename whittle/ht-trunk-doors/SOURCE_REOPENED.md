# Source revision after fresh Test Pilot

Do not build candidate1. Fresh tools-disabled pilot response is in evidence/pilot_raw.json.

Worker is adopting restoration-before-reload ordering, bounded threshold loops for controls, full wall identity checks, explicit end-of-round game PID comparison, and live indestructible / actual ground ClearArea-mode controls (no ship/flight).

The ClearArea control adds a bounded declared-fixture adapter to TrunkDoorValidationHooks.cs and therefore requires source-ready v2 and a fresh parent source commit before production build. Source-ready v1 snapshots remain retained as historical inputs. No production build or behavioral proof has been claimed.
