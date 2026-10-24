import json, subprocess, time
from datetime import datetime, timezone

LIVE, STATUS, TMP = "live.json", "status.json", "userdb_auto.txt"
DEST = "cowrie:/cowrie/cowrie-git/etc/userdb.txt"
WINDOW, POLL = 60, 5

RULES = {
    "Low": (["root:x:!root", "root:x:!123456", "root:x:*", "*:x:*"],
            "Basic monitoring"),
    "Medium": (["backup:x:Backup@2026", "root:x:!root", "root:x:!123456",
                "root:x:*", "*:x:*"],
               "Decoy account enabled (backup)"),
    "High": (["backup:x:Backup@2026", "root:x:!root", "root:x:!123456"],
             "Wildcard logins blocked, only decoy account works"),
}

def failed_recent():
    try:
        lines = open(LIVE, encoding="utf-8", errors="ignore").read().splitlines()
    except FileNotFoundError:
        return 0
    now, n = datetime.now(timezone.utc), 0
    for line in lines[-3000:]:
        if "cowrie.login.failed" not in line:
            continue
        try:
            t = datetime.fromisoformat(json.loads(line)["timestamp"].replace("Z", "+00:00"))
        except Exception:
            continue
        if (now - t).total_seconds() <= WINDOW:
            n += 1
    return n

def level_for(n):
    return "High" if n >= 8 else "Medium" if n >= 3 else "Low"

def write_status(level, n, applied):
    with open(STATUS, "w", encoding="utf-8") as f:
        json.dump({"level": level, "action": RULES[level][1], "applied": applied,
                   "failed_60s": n, "time": datetime.now().strftime("%H:%M:%S")}, f)

def apply(level):
    with open(TMP, "w", encoding="utf-8") as f:
        f.write("\n".join(RULES[level][0]) + "\n")
    r = subprocess.run(["docker", "cp", TMP, DEST], capture_output=True, text=True)
    if r.returncode != 0:
        print("copy fail:", r.stderr.strip())
    return r.returncode == 0

current, applied = None, False
print("Engine chalu. Band karne ke liye Ctrl+C.")
try:
    while True:
        n = failed_recent()
        lvl = level_for(n)
        if lvl != current:
            applied = apply(lvl)
            current = lvl
            print(time.strftime("%H:%M:%S"), lvl, "| failed:", n, "| applied:", applied)
        write_status(lvl, n, applied)
        time.sleep(POLL)
except KeyboardInterrupt:
    apply("Low")
    write_status("Low", 0, True)
    print("Band. Cowrie wapas normal (Low).")