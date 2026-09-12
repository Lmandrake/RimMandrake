"""modcheck.report -- the HTML flip-through sheet, per spec §3.

One file per run: `Transient/modcheck/<mod>_<UTC>.html`. Transient shelf
life (~14 days) is fine here -- the `rimflow verify` event is the durable
record; a sheet is a human's way to flip through what happened. `render()`
is a pure function of a run summary so it can be unit-tested without a
game, a bridge, or a filesystem write.
"""
import html


def _row(component):
    v = component["verdict"] or ""
    color = {"PASS": "#1a7f37", "FAIL": "#cf222e",
            "UNMEASURED": "#9a6700"}.get(v.split("(")[0], "#57606a")
    shots = "".join(
        '<div class="shot">%s</div>' % html.escape(s)
        for s in component.get("screenshots") or [])
    evid = "<br>".join(
        html.escape("%s -> %r" % (e["call"], e["result"]))
        for e in component.get("evidence") or [])
    return (
        '<tr><td>%s</td><td>%s</td><td style="color:%s">%s</td>'
        '<td>%s</td><td>%s%s</td></tr>'
        % (html.escape(component["name"]),
          html.escape(component.get("toggle") or
                      ("beyond-toggle" if component.get("beyond_toggle") else "")),
          color, html.escape(str(v)), html.escape(component.get("detail") or ""),
          evid, shots))


def render(mod, summary):
    chains_html = []
    for chain in summary["chains"]:
        rows = "".join(_row(c) for c in chain["components"])
        chains_html.append(
            '<h2>%s</h2><table><tr><th>component</th><th>toggle</th>'
            '<th>verdict</th><th>detail</th><th>evidence</th></tr>%s</table>'
            % (html.escape(chain["name"]), rows))
    overall = "GREEN" if summary["all_green"] else "RED"
    return """<!doctype html><html><head><meta charset="utf-8">
<title>modcheck: %s</title>
<style>
body{font-family:system-ui,sans-serif;background:#faf7f2;color:#2a231c;margin:2em}
h1{color:%s} table{border-collapse:collapse;width:100%%;margin-bottom:2em}
td,th{border:1px solid #ccc;padding:.4em .6em;text-align:left;vertical-align:top;font-size:.9em}
th{background:#eee2d0} .shot{font-family:monospace;font-size:.8em;color:#666}
</style></head><body>
<h1>%s -- %s</h1>
%s
</body></html>""" % (html.escape(mod), "#1a7f37" if overall == "GREEN" else "#cf222e",
                     html.escape(mod), overall, "".join(chains_html))
