#!/usr/bin/env python3
"""Every modDependencies entry in every About.xml under src/ must carry a non-empty
<downloadUrl> or <steamWorkshopUrl> (Ludeon packageIds exempt).

Why: RimWorld 1.6's ModMetaData (decompiled, the "needs to have <downloadUrl> and/or
<steamWorkshopUrl> specified" warning) REMOVES a dependency lacking both from the mod's
dependency list, so the declaration silently does nothing. An empty `<steamWorkshopUrl />`
counts as missing. 73 such entries across 51 About.xml were found 2026-10-08
(WARCASKET_DEPENDENCY_DOWNLOAD_URL_1). Our own mods point at the source repo.

Sanity probe: the parser must see at least 50 dependency entries, or it is reading nothing.
"""
import glob
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def main():
    seen, bad = 0, []
    for p in sorted(glob.glob(os.path.join(ROOT, "src", "**", "About", "About.xml"), recursive=True)):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError as e:
            bad.append("%s: unparseable (%s)" % (os.path.relpath(p, ROOT), e))
            continue
        for deps in root.iter("modDependencies"):
            for li in deps.findall("li"):
                pid = (li.findtext("packageId") or "").strip()
                if not pid:
                    continue
                seen += 1
                if "ludeon" in pid.lower():
                    continue
                url = (li.findtext("downloadUrl") or "").strip() or (li.findtext("steamWorkshopUrl") or "").strip()
                if not url:
                    bad.append("%s: dependency %s has no downloadUrl/steamWorkshopUrl (the engine drops it)" % (os.path.relpath(p, ROOT), pid))
    if seen < 50:
        print("FAIL sanity probe: only %d dependency entries seen; the scan is blind" % seen)
        return 1
    for b in bad:
        print("FAIL " + b)
    print("about dependency urls: %d entries, %d failures -> %s" % (seen, len(bad), "OK" if not bad else "FAILED"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
