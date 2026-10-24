import json
import pandas as pd

ev = [json.loads(l) for l in open("cowrie.json", encoding="utf-8")]
S = {}
for e in ev:
    sid = e.get("session")
    if not sid:
        continue
    d = S.setdefault(sid, dict(start=None, failed=0, success=0,
                               cmds=[], downloads=0, duration=0.0))
    t = e["eventid"]
    if t == "cowrie.session.connect":
        d["start"] = e["timestamp"]
    elif t == "cowrie.login.failed":
        d["failed"] += 1
    elif t == "cowrie.login.success":
        d["success"] += 1
    elif t == "cowrie.command.input":
        d["cmds"].append(e["input"])
    elif t == "cowrie.session.file_download":
        d["downloads"] += 1
    elif t == "cowrie.session.closed":
        d["duration"] = float(e.get("duration", 0))

rows = []
for sid, d in S.items():
    if d["start"] is None:
        continue
    rows.append(dict(
        session=sid,
        start=pd.to_datetime(d["start"], utc=True).tz_localize(None),
        failed=d["failed"],
        success=d["success"],
        n_cmds=len(d["cmds"]),
        n_unique_cmds=len(set(d["cmds"])),
        downloads=d["downloads"],
        duration=d["duration"],
    ))

df = pd.DataFrame(rows).sort_values("start")

lab = pd.read_csv("labels.csv")
lab["time"] = pd.to_datetime(lab["time"]) - pd.Timedelta(hours=5, minutes=30)
lab = lab.sort_values("time")

m = pd.merge_asof(df, lab, left_on="start", right_on="time",
                  direction="backward",
                  tolerance=pd.Timedelta(seconds=30))
m = m.dropna(subset=["label"]).drop(columns=["time"])
m.to_csv("dataset.csv", index=False)

print("total sessions:", len(df))
print("labeled sessions:", len(m))
print(m["label"].value_counts())
print(m.groupby("label")[["failed", "n_cmds", "duration"]].mean())