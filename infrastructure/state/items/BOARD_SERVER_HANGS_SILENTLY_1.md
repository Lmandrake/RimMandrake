# BOARD_SERVER_HANGS_SILENTLY_1 The board accepts connections and never answers; ps says it is alive

## spec

Found on waking, 2026-08-23 11:20. `status_server.py` had been running 18h44m. Every
liveness check a seat is told to run said **UP**:

```
ps -eo pid,etime,args | grep -E '[s]tatus_server\.py'   -> alive, 18:44:51
ss -ltnp | grep 8787                                    -> LISTEN, backlog 5, pid 1289902
```

And the board was dead:

```
curl -m 5 http://localhost:8787/   -> 000, timed out, zero bytes
```

The socket was **listening and accepting**; nothing behind it ever wrote a response.
`kill` + restart fixed it instantly (`200`). Uptime unknown at what point it wedged, so
the board may have been blank for hours with every instrument reporting health.

## Why this matters more than one restart

`REP.md` teaches two liveness checks — the bracket-grep on `ps`, and
`curl -w '%{http_code}'`. This failure passes the first and only the second catches it.
A seat that ran the documented `ps` check and stopped there would have reported the
board UP. That is the same class of defect the board itself was rebuilt to kill on
2026-08-22: **an instrument answering from the wrong evidence.** A process existing is
not a service answering.

## Likely cause, unconfirmed

`status_server.py` is a stock single-threaded `HTTPServer`. One client that opens a
connection and never completes its request blocks `handle_request()` forever, and every
later connection sits in the accept backlog — which is exactly the observed shape
(LISTEN with backlog, no response). WSL plus a browser tab left open overnight is a
plausible source of such a client. UNCONFIRMED: nobody captured the stack before killing it.

## Fix

1. `ThreadingHTTPServer` instead of `HTTPServer`, plus a socket timeout on the handler.
   One-line class swap in the stdlib; this is the whole fix in the normal case.
2. Correct `REP.md`: the `ps` check is necessary and **not sufficient**. The HTTP probe
   is the one that decides. Say so where the two checks are taught, not in a note below.
3. Consider having `board_loop.sh` curl the board each cycle and restart it on a
   non-200 — it already runs every 60 s and is the only thing awake when no seat is.

## verify

- With the fix in, open a raw connection to :8787 and leave it hanging
  (`exec 3<>/dev/tcp/127.0.0.1/8787`), then `curl` the board from another shell. It must
  still return `200`. Today it would have returned `000`.
- `REP.md` no longer presents the `ps` check as sufficient.

## Watch out

- 🔴 **Restart `status_server.py` after ANY change to its Python** — the HTML is re-read
  per request, the server code is not. Editing the file changes nothing until the
  process is replaced.
- Start it detached or the harness kills it at end of turn:
  `setsid nohup python3 src/RimMandrake/Utils/status_server.py >/dev/null 2>&1 </dev/null &`
- This is REP's own file and REP's own item. It is filed rather than fixed on the spot
  because the owner asked for tickets on what is already known, and because step 2
  edits doctrine that other seats read.
