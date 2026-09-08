import time
LOG = r"/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
MARK = "GABP server running standalone"
deadline = time.time() + 900
while time.time() < deadline:
    try:
        with open(LOG, encoding="utf-8", errors="ignore") as f:
            data = f.read()
        if MARK in data:
            print("BRIDGE UP")
            break
    except Exception as e:
        print("read error", e)
    time.sleep(10)
else:
    print("TIMEOUT after 900s")
