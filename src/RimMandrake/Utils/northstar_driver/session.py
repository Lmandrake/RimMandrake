"""FastSession -- rimdrive.Session over a pluggable, timed, persistent transport.

Everything modcheck's TestContext / rimdrive's mutate/paused/sweep need is inherited;
only the connection is replaced. `transport=None` opens the live bridge ONCE
(one socket for the whole run); pass a MockTransport for offline runs.
"""
import os
import sys

_UTILS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _UTILS not in sys.path:
    sys.path.insert(0, _UTILS)
from rimdrive.session import Session, SessionError  # noqa: E402
from rimdrive import session as _rs  # noqa: E402
from northstar_driver.transport import TimedTransport  # noqa: E402


class FastSession(Session):
    def __init__(self, transport=None, pipeline=False, **kw):
        kw.setdefault("focus", transport is None)   # mock needs no window focus
        kw.setdefault("quiet", True)
        super().__init__(**kw)
        self._transport = transport
        self._pipeline = pipeline

    def _open(self):
        if self._transport is None:
            from rimbridge_client import RimBridge, resolve_endpoint
            host, port, token = resolve_endpoint(self._host, self._port, self._token)
            if not token:
                raise SessionError("No bridge token (env/Player.log). Is RimWorld up "
                                   "with RimBridgeServer active?")
            self._transport = TimedTransport(RimBridge(host, port, token),
                                             pipeline=self._pipeline)
        self._rb = self._transport.__enter__()
        self.tools = {t.get("name") for t in self._rb.list_tools()}

    def _disconnect(self):
        if self._rb is not None:
            try:
                self._rb.__exit__(None, None, None)
            except Exception:
                pass
            self._rb = None

    # conveniences the bar layer uses
    def call_many(self, calls):
        self.calls += len(calls)
        return self._rb.call_many(calls)

    @property
    def timing(self):
        return self._transport.log.summary()
