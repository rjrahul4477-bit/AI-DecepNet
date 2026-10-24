# AI-DecepNet: Intelligent Adaptive Honeypot

Pre-final year project, Department of Computer Science and Engineering, ITS Engineering College, Greater Noida.

Team: Rishav Raj, Shashank Kumar, Rahul Raj Yadav. Guide: Sushil Chhabra (Assistant Professor).

## What it does

AI-DecepNet watches a Cowrie SSH/Telnet honeypot, classifies each attacker session with a Random Forest, and runs a small rule-based engine that changes the honeypot's login rules while an attack is happening. A Streamlit dashboard shows everything in near real time (5 second refresh).

```
Attacker -> Cowrie honeypot (Docker) -> live.json (synced every 5 s)
         -> session features -> Random Forest (attack type + confidence)
         -> rules (session threat level, recommended trap)
         -> adaptive engine (failed logins in 60 s -> Low / Medium / High -> honeypot userdb)
         -> Streamlit dashboard
```

## Adaptive engine (tested)

| Level | Failed logins in 60 s | Honeypot response |
|---|---|---|
| Low | 0 to 2 | Default rules |
| Medium | 3 to 7 | Decoy account enabled |
| High | 8 or more | Wildcard logins blocked, only the decoy account works |

It returns to Low after 60 seconds of quiet. In our lab test, 10 failed logins moved the engine to High, a normal login was then denied, the decoy account worked, and normal logins worked again after the engine returned to Low.

The model does not control the engine. The session threat level (model + rules) and the engine level (failed-login rate) are separate measurements and can disagree.

## Results (lab dataset)

- 160 labeled sessions: 80 brute force, 44 scanning, 36 command execution.
- Test accuracy about 95% (40 sessions), 5-fold cross-validation 97.5%.
- Most important feature: failed logins.

## Limitations

- Small laboratory dataset with some label noise. These numbers do not prove the same performance on real internet traffic.
- Model confidence is the model's own estimate, not a guarantee.
- Recommended traps are recommendations. The only change the engine applies is the honeypot userdb update.
- Cowrie captures SSH and Telnet sessions only, so only three attack categories are supported.
- Critical level, reinforcement learning and session isolation are future work.

## Files

| File | Purpose |
|---|---|
| `gen.py` | Generates labeled test sessions against your own local honeypot |
| `features.py` | Builds `dataset.csv` (session features and labels) from the Cowrie log |
| `train.py` | Trains the Random Forest and saves `model.pkl` |
| `engine.py` | Rule-based adaptive engine, writes `status.json` |
| `sync.bat` | Copies the Cowrie log from the container to `live.json` every 5 s (Windows) |
| `app_final.py` | Streamlit dashboard |

## Run it (Windows, Docker Desktop)

Use a local lab machine only. Do not expose the honeypot to the internet.

```
docker run -d --name cowrie -p 2222:2222 -p 2223:2223 cowrie/cowrie:latest
.\sync.bat
python engine.py
```

Dashboard (inside a Python 3.12 container, with this folder mounted):

```
docker run -it --name ml -p 8501:8501 -v "%cd%:/work" -w /work python:3.12 bash
pip install pandas scikit-learn plotly streamlit
streamlit run app_final.py --server.address 0.0.0.0 --server.port 8501
```

Open http://localhost:8501.

To rebuild the model: run `gen.py` against the honeypot, copy the Cowrie log to `cowrie.json`, then run `features.py` and `train.py`.

## Safety

Never commit real Cowrie logs. They store every password an attacker (or you) types, in plain text. `.gitignore` excludes them.
