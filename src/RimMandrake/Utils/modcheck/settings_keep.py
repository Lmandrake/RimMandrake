"""modcheck.settings_keep -- a live proof leaves the mod's settings FILES as it found them.

Item RIMMANDRAKE_RESTORE_SLACK_LOOK_FILE_AFTER_PROOF_LEFT_EXTCORD. Measured 2026-11-20/21 on game b: GimmeSomeSlack's
core block ran ST3 (sets ExtensionCord in memory) and then ST4 (StyleProbe.SettingsRoundTrip, in the mod DLL), which
writes the IN-MEMORY settings to Config/Mod_GimmeSomeSlack_GimmeSomeSlackMod.xml at its end. The file read
<style>StarWarsJawa</style> before the run and <style>ExtensionCord</style> after it, so the next cold load started on
that look. The writer is in the mod, and a mod change (or a change to the mod's own proof_all.py) moves the walk build
(build_match.py); so the run-identity hooks that every checkout already calls at its start and end keep the files.

  Keep(mod).take()      before the run: reads every Config/Mod_<mod>_*.xml of THIS game (game_paths.LOCALLOW follows
                        RM_GAME_INSTANCE) and writes them to a sidecar Config/Mod_<mod>_proof_found.json first.
  Keep(mod).put_back()  at the end: each file back to its found bytes; a file the run created is removed; then the
                        sidecar is removed.

A run killed outright (TerminateProcess from WSL runs no finally) leaves the sidecar: the next take() on that game puts
its files back before it reads; the driver lock (game_lock.py) means no live run owns that sidecar then. The game's
in-memory settings are not touched: the file is what the next load reads.

Answers stay apart: `found` {} means looked and the mod has no settings file; `unmeasured` names why it could not look
(no Config folder on this machine), and then nothing is kept; `put_back` "nothing taken" means take() did not keep.
"""
import json
import os
import re
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)


def config_dir():
    """This game's Config folder (game a's LocalLow, or a named game's own data folder)."""
    if _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    import game_paths
    return os.path.join(game_paths.LOCALLOW, "Config")


def style(text):
    """The <style> value of a settings text, for a person reading the record (None: no file)."""
    if text is None:
        return None
    m = re.search(r"<style>([^<]*)</style>", text)
    return m.group(1) if m else "(no <style>: the shipped default)"


class Keep:
    def __init__(self, mod, cfg=None):
        self.dir = cfg or config_dir()
        self.prefix = "Mod_%s_" % mod
        self.sidecar = os.path.join(self.dir, self.prefix + "proof_found.json")
        self.found = None                 # {name: text}; None = nothing kept

    def _names(self):
        try:
            return sorted(n for n in os.listdir(self.dir) if n.startswith(self.prefix) and n.endswith(".xml"))
        except OSError:
            return []

    @staticmethod
    def _read(p):
        try:
            with open(p, "rb") as f:
                return f.read().decode("latin-1")    # latin-1 round-trips every byte, a BOM included
        except FileNotFoundError:
            return None

    def _write_all(self, files):
        """Each of the mod's files to its kept text; one not kept (the run made it) is removed. -> names changed."""
        changed = []
        for n in sorted(set(files) | set(self._names())):
            p, want = os.path.join(self.dir, n), files.get(n)
            if self._read(p) == want:
                continue
            if want is None:
                os.remove(p)
            else:
                with open(p, "wb") as f:
                    f.write(want.encode("latin-1"))
            changed.append(n)
        return changed

    def _styles(self):
        return {n: style(self._read(os.path.join(self.dir, n))) for n in self._names()}

    def take(self):
        rec = {"dir": self.dir}
        if not os.path.isdir(self.dir):
            rec["unmeasured"] = "no Config folder at %s: settings files not kept" % self.dir
            return rec
        stale = self._read(self.sidecar)
        if stale is not None:                # a run on this game died before its put_back
            rec["stale_sidecar_put_back"] = self._write_all(json.loads(stale)["files"])
            os.remove(self.sidecar)
        self.found = {n: self._read(os.path.join(self.dir, n)) for n in self._names()}
        with open(self.sidecar, "w") as f:
            json.dump({"files": self.found, "pid": os.getpid(), "at": time.strftime("%Y-%m-%dT%H:%M:%S")}, f)
        rec["found"] = {n: style(t) for n, t in self.found.items()}
        return rec

    def put_back(self):
        if self.found is None:
            return {"put_back": "nothing taken"}
        rec = {"at_end": self._styles(), "rewritten": self._write_all(self.found)}
        rec["after"] = self._styles()
        os.remove(self.sidecar)
        self.found = None
        return rec
