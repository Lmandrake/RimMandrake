# scenes - cheap live scenes over the bridge

`scenelib.py` is a small library; run scripts under `python.exe` from the repo root (never WSL python:
the bridge binds Windows loopback). Add `src/RimMandrake/Utils` to `sys.path`, then
`from scenes import scenelib as S`.

    with S.Scene("dark_room", x=100, z=100, w=9, h=9) as sc:   # clears the rect on entry and exit
        sc.room(); sc.put("StandingLamp", 3, 3); print(sc.glow(4, 4), sc.temp(4, 4))

- Build: `room` (walls, floor, roof), `floor`, `put(def,dx,dz)`, `pawn`/`colonist`. Act: `hediff`, `time_of_day`, `kill`, `kill_hostiles`.
- Read: `glow`, `temp`, `things`, `hediffs`, plus raw `S.call(tool, **params)`, `S.step(ticks)`.
- Rects and cells are STRINGS ("x,z,w,h"); a dict raises InvalidCastException. Pawns die by `jawa/damage`, never `destroy_batch`.
- `sky_glow_set` is overwritten next frame; use `time_of_day`. Teardown is `jawa/clear_area` (roof stripped, things destroyed).
- Every scenario script lives in `scenarios.py` beside this file and records what it measured to stdout.
- One bridge driver at a time (`rimflow bridge who`); never run flyer visual tests here.
