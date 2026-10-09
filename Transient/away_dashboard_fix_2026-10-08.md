# Away dashboard fix 2026-10-08

## Symptom
## Root cause
## Fix
## Test

### Measured 21:2x (debugger)
- Mirror lantern.pyw/index.html byte-identical to bench HEAD (diff -q clean) — not a mirror issue.
- Hung pid 5232: form hwnd 12322666 owned by tid 24496 (pywebview STA GUI thread, in app.Run), IsHungAppWindow=True.
- py-spy dump (installed --user into Store Python): Thread "generate_js_object" stuck deep in
  webview/util.py get_functions recursion (5 levels). pywebview walks EVERY public attribute of js_api
  recursively; Api.window = the pywebview Window -> .native (WinForms BrowserForm) -> .NET object graph,
  touched cross-thread from a worker while the GUI thread is pumping. That wedges the GUI thread.
- No "placed at" line is NOT a symptom: place_initial returns silently when the window was created at the saved spot.

## Fix (lantern.pyw)
- Api's non-API attrs underscored (_window/_toasted/_lock) so pywebview's js_api walker never enters .NET.
- Worker thread no longer touches window.native; hwnd found by EnumWindows(pid,title); all SetWindowPos ASYNC.
- Stage logging: launch, mutex, window created, bg thread up, hwnd found, restored/placed, page+api ready.
- Watchdog on launch: mutex held -> holder answers WM_NULL in 3 s? leave it (exit 0) : kill holder PID (python-only check) and take over.
- Self-watchdog: GUI unanswering 60 s or no window in 90 s -> faulthandler stack dump to lantern.log, relaunch (max 3/h).

### Second cause (measured after first publish)
- Task State=Running, MultipleInstances=IgnoreNew. The task instance IS the widget process, so while it lives every
  re-run is refused (0x800710E0 = "operator refused the request") — the new python never even started (no log line).
  So "re-launch exits silently on the mutex" was actually "re-launch never launched". Fix: MultipleInstances Parallel.

## Test (21:22-21:25)
- Reinstalled task (Parallel), Start-ScheduledTask once: new pid 28436 logged every stage; watchdog killed hung 5232 by PID.
- Restored at saved 2656,1240; page + js api ready 5.1 s after launch.
- Responding polled every 15 s for 150 s: 10/10 True.
- Screenshot D:\Luke\dev\_rmscratch\pulse_shot.bmp: widget rendered, "live 4s", clock 21:25, rows ticking.
- Published 0d93c27be (lantern.pyw) + 281d1b91d (install_autostart.ps1). py-spy left installed (--user) for next time.
