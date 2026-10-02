"""northstar_driver -- ultra-fast, refuse-on-dirty-site driver for north-star validation.

Layered ON rimdrive.Session (reconnect, verified pause, litter sweep) and modcheck's
Suite/northstar parser -- it adds: a timed persistent transport with optional
pipelined batches, a pre-flight site check, a bar runner producing modcheck-consumable
JSON, and a mock game so all of it is provable with the game down.

Run under Windows Python for live work (WSL cannot reach the bridge), repo-relative
paths:  python.exe src/RimMandrake/Utils/northstar_driver/cli.py --help
Item: NORTHSTAR_FAST_DRIVER_1.
"""
PASS, FAIL, UNMEASURED = "PASS", "FAIL", "UNMEASURED"
