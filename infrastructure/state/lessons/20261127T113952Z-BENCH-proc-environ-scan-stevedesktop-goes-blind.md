A /proc environ scan on SteveDesktop goes blind on Tailscale SSH's session child: 'tailscaled be-child ssh' runs as our uid, but reading its environ fails with EACCES, and its parent tailscaled is root. Archmagi opens about one such session every 13 s. Rule such a pid out by its parent's effective uid; never call the whole scan blind for it.
item: RIMMANDRAKE_READ_FIX_C87A073D0E_WITH_FRESH_EYES
home: design/specs/2026-11-19-run-return-reap/boundary.md
