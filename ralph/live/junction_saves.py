#!/usr/bin/env python3
"""Junction before-and-after on ONE save per look, drawn by both DLLs. Runs on Steve: python.exe ralph/live/junction_saves.py now|pre [Look ...]

    now   per look: lived_in build --fresh-map, play 1500 ticks, save gss_ba_<Look>, shots ba_now (house, yard, work, strips); writes ralph/live/ba_state.json
    pre   (after the old DLL is copied over Mods/GimmeSomeSlack/Assemblies and the game is up) per look: load gss_ba_<Look>, shots ba_pre with the same origin

Then here: python3 ralph/live/junction_ba.py <shots dir> ba_pre ba_now ba_sheet Look... (it reads house and yard; add work and strips there if wanted).
The cords are drawn from the conduit and saved nothing of their own, so the same save under both DLLs is the honest comparison.
"""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.getcwd(), "ralph", "live"))
import lived_in as LI  # noqa: E402

BA = "ralph/live/ba_state.json"
FRAMES = "house,yard,work,strips"


def main():
    mode, looks = sys.argv[1], sys.argv[2:] or ["Modern", "Scrapper", "Industrial", "Futuristic"]
    st = json.load(open(BA)) if os.path.exists(BA) else {}
    for look in looks:
        R = LI.Run()
        name = "gss_ba_%s" % look
        if mode == "now":
            R.build(look, True)
            R.play(1500)
            st[look] = R.st()
            json.dump(st, open(BA, "w"))
            print("save", json.dumps(R.B.call("rimworld/save_game", saveName=name))[:160])
            time.sleep(3)
        else:
            r = R.B.call("rimworld/load_game_ready", saveName=name, timeoutMs=240000)
            print("load", json.dumps(r)[:160])
            time.sleep(5)
            json.dump(st[look], open(LI.STATE, "w"))   # the same origin the now shots used
        R.shots("ba_" + mode, FRAMES.split(","))
        if R.notes:
            print("NOTES", R.notes[:5])


if __name__ == "__main__":
    main()
