import json, os, html
import streamlit as st, pandas as pd, joblib
import plotly.express as px, plotly.graph_objects as go

st.set_page_config(page_title="AI-DecepNet", page_icon="🍯", layout="wide")

st.markdown("""<style>
.stApp{background:#020805}
.stApp::before{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(34,255,136,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(34,255,136,.07) 1px,transparent 1px);background-size:48px 48px;animation:grid 22s linear infinite;pointer-events:none;z-index:0}
.stApp::after{content:"";position:fixed;inset:-20%;background:radial-gradient(circle at 20% 30%,rgba(34,255,136,.20),transparent 35%),radial-gradient(circle at 80% 75%,rgba(16,185,129,.18),transparent 40%);animation:drift 14s ease-in-out infinite alternate;pointer-events:none;z-index:0}
.block-container{position:relative;z-index:1}
header[data-testid="stHeader"]{background:transparent}
section[data-testid="stSidebar"]{background:rgba(0,255,140,.04);backdrop-filter:blur(22px);border-right:1px solid rgba(34,255,136,.25)}
.glass,div[data-testid="stPlotlyChart"]{background:rgba(0,255,140,.05);backdrop-filter:blur(18px) saturate(170%);-webkit-backdrop-filter:blur(18px) saturate(170%);border:1px solid rgba(34,255,136,.25);border-radius:22px;padding:16px 18px;box-shadow:0 8px 32px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.08);transition:transform .25s ease,box-shadow .25s ease,border-color .25s ease}
.glass:hover,div[data-testid="stPlotlyChart"]:hover{transform:translateY(-6px);border-color:rgba(34,255,136,.7);box-shadow:0 14px 44px rgba(34,255,136,.25)}
.kpi-label{color:rgba(190,255,220,.7);font-size:.78rem;letter-spacing:.1em;text-transform:uppercase}
.kpi-val{font-size:2.5rem;font-weight:700;line-height:1.15;color:#fff;font-family:ui-monospace,Consolas,monospace}
.title{font-size:2.7rem;font-weight:800;margin:0;background:linear-gradient(90deg,#fff,#22ff88,#a7f3d0,#fff);background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:shine 6s linear infinite}
.sub{color:rgba(190,255,220,.7);margin:0 0 16px 0}
.live{color:#22ff88;font-weight:700}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:8px;background:currentColor;animation:pulse 1.6s infinite}
.story{color:#eafff3;font-size:1.05rem;margin-bottom:14px;border-left:4px solid #22ff88}
.feed{background:rgba(0,255,140,.05);backdrop-filter:blur(14px);border:1px solid rgba(34,255,136,.18);border-radius:16px;padding:12px 16px;margin:8px 0;color:#fff;transition:transform .2s ease,background .2s ease;animation:slide .5s ease both}
.feed:hover{transform:translateX(8px);background:rgba(34,255,136,.12)}
.badge{border:1px solid;border-radius:999px;padding:2px 10px;font-size:.75rem;font-weight:700;margin-right:10px}
.sm{color:rgba(190,255,220,.65);font-size:.85rem;margin-top:4px}
.term{background:#000;color:#22ff88;font-family:ui-monospace,Consolas,monospace;border:1px solid rgba(34,255,136,.4);border-radius:14px;padding:14px 16px;margin-top:10px;box-shadow:0 0 24px rgba(34,255,136,.15)}
.flow{display:flex;flex-wrap:wrap;gap:14px;margin-top:10px}
.step{flex:1 1 150px;position:relative;background:rgba(0,255,140,.06);backdrop-filter:blur(16px);border:1px solid rgba(34,255,136,.25);border-radius:18px;padding:16px;color:#fff;text-align:center;transition:transform .25s ease,box-shadow .25s ease}
.step:hover{transform:translateY(-8px) scale(1.03);box-shadow:0 12px 36px rgba(34,255,136,.3)}
.step:not(:last-child)::after{content:"→";position:absolute;right:-13px;top:38%;color:#22ff88;font-size:1.3rem}
.ic{font-size:1.8rem;margin-bottom:6px}
.row{color:#fff;margin:6px 0}
button[data-baseweb="tab"]{color:#9fe8c0}
button[data-baseweb="tab"][aria-selected="true"]{color:#22ff88}
div[data-baseweb="tab-highlight"]{background:#22ff88}
@keyframes grid{to{background-position:0 48px,48px 0}}
@keyframes drift{from{transform:translate(-3%,-2%) scale(1)}to{transform:translate(3%,3%) scale(1.12)}}
@keyframes shine{to{background-position:200% center}}
@keyframes pulse{0%{box-shadow:0 0 0 0 currentColor}100%{box-shadow:0 0 0 14px transparent}}
@keyframes slide{from{opacity:0;transform:translateX(-14px)}to{opacity:1;transform:none}}
</style>""", unsafe_allow_html=True)

import streamlit.components.v1 as components

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap');
.stApp,.stMarkdown,label,p,button[data-baseweb="tab"]{font-family:'Inter',system-ui,sans-serif}
.title,h1,h2,h3{font-family:'Space Grotesk','Inter',sans-serif!important;letter-spacing:-.02em}
.kpi-val,.term,.badge,.gt,.live{font-family:'JetBrains Mono',Consolas,monospace}
.glass,.step,.feed{position:relative}
.glass::before,.step::before,.feed::before{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;opacity:0;transition:opacity .25s;background:radial-gradient(220px circle at var(--x,50%) var(--y,50%),rgba(34,255,136,.20),transparent 70%)}
.glass:hover::before,.step:hover::before,.feed:hover::before{opacity:1}
div[data-testid="stPlotlyChart"]{touch-action:pan-y}
div[data-testid="stPlotlyChart"]:hover{transform:none!important}
.modebar{display:none!important}
.scrollbox{max-height:480px;overflow-y:auto;padding-right:8px}
*{scrollbar-width:thin;scrollbar-color:#22ff88 transparent}
*::-webkit-scrollbar{width:9px;height:9px}
*::-webkit-scrollbar-track{background:transparent}
*::-webkit-scrollbar-thumb{background:linear-gradient(#22ff88,#0e9f6e);border-radius:9px}
</style>""", unsafe_allow_html=True)

try:
    components.html("""<script>
(function(){
 const P=window.parent, D=P.document;
 if(P.__glow) return; P.__glow=true;
 const g=D.createElement('div');
 g.style.cssText='position:fixed;inset:0;pointer-events:none;z-index:0;mix-blend-mode:screen';
 D.body.appendChild(g);
 let x=-999,y=-999,tx=-999,ty=-999;
 D.addEventListener('mousemove',function(e){
  tx=e.clientX; ty=e.clientY;
  const el=e.target.closest&&e.target.closest('.glass,.step,.feed');
  if(el){const b=el.getBoundingClientRect();
   el.style.setProperty('--x',(e.clientX-b.left)+'px');
   el.style.setProperty('--y',(e.clientY-b.top)+'px');}
 });
 (function loop(){
  x+=(tx-x)*.15; y+=(ty-y)*.15;
  g.style.background='radial-gradient(200px circle at '+x+'px '+y+'px,rgba(34,255,136,.15),transparent 70%)';
  P.requestAnimationFrame(loop);
 })();
})();
</script>""", height=0)
except Exception:
    pass

COLS = ["failed", "success", "n_cmds", "n_unique_cmds", "downloads"]
ORDER = ["Low", "Medium", "High", "Critical"]
COLOR = {"Low": "#22c55e", "Medium": "#facc15", "High": "#fb923c", "Critical": "#ef4444"}
ICON = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
ACTION = {
    "Low": "Basic monitoring",
    "Medium": "Increase logging + activate decoy",
    "High": "Activate deeper honeypot interaction",
    "Critical": "Isolate interaction + intensive monitoring",
}
PLAIN = {
    "brute_force": "Someone is guessing passwords to break in.",
    "command_exec": "Someone got inside the decoy and is typing commands.",
    "scanning": "Someone is knocking on doors to see what is open.",
}
TZ = "Asia/Kolkata"

@st.cache_resource
def get_model():
    return joblib.load("model.pkl")

def decide(r):
    if r["predicted"] == "brute_force":
        lvl, trap = ("Critical" if r["success"] > 0 else "Medium"), "Fake Login + Honey Credential"
    elif r["predicted"] == "command_exec":
        lvl, trap = ("Critical" if r["downloads"] > 0 else "High"), "High-Interaction Trap (fake files)"
    else:
        lvl, trap = "Low", "Basic Monitor"
    return pd.Series([lvl, ACTION[lvl], trap])

def enrich(df):
    if df.empty:
        return df
    m = get_model()
    p = m.predict_proba(df[COLS])
    df["predicted"] = m.classes_[p.argmax(1)]
    df["confidence"] = (p.max(1) * 100).round(1)
    df[["threat", "action", "trap"]] = df.apply(decide, axis=1)
    return df

def parse_live(path="live.json"):
    if not os.path.exists(path):
        return pd.DataFrame()
    S = {}
    for line in open(path, encoding="utf-8", errors="ignore"):
        try:
            e = json.loads(line)
        except Exception:
            continue
        sid = e.get("session")
        if not sid:
            continue
        d = S.setdefault(sid, dict(start=None, ip="-", failed=0, success=0, cmds=[], downloads=0))
        t = e.get("eventid", "")
        if t == "cowrie.session.connect":
            d["start"] = e["timestamp"]
            d["ip"] = e.get("src_ip", "-")
        elif t == "cowrie.login.failed":
            d["failed"] += 1
        elif t == "cowrie.login.success":
            d["success"] += 1
        elif t == "cowrie.command.input":
            d["cmds"].append(e.get("input", ""))
        elif t == "cowrie.session.file_download":
            d["downloads"] += 1
    rows = [dict(session=k, start=pd.to_datetime(v["start"], utc=True).tz_convert(TZ),
                 ip=v["ip"], failed=v["failed"], success=v["success"],
                 n_cmds=len(v["cmds"]), n_unique_cmds=len(set(v["cmds"])),
                 downloads=v["downloads"], cmds="\n".join(v["cmds"]), source="live")
            for k, v in S.items() if v["start"]]
    return enrich(pd.DataFrame(rows))

def load_history():
    df = pd.read_csv("dataset.csv")
    df["start"] = pd.to_datetime(df["start"]).dt.tz_localize("UTC").dt.tz_convert(TZ)
    df["ip"] = "-"
    df["cmds"] = ""
    df["source"] = "recorded"
    return enrich(df)

def style(fig):
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_color="white", font_family="Inter, sans-serif", dragmode=False, margin=dict(l=10, r=10, t=45, b=10), legend_title_text="")
    fig.update_xaxes(fixedrange=True, gridcolor="rgba(34,255,136,.08)")
    fig.update_yaxes(fixedrange=True, gridcolor="rgba(34,255,136,.08)")
    return fig

def kpi(col, label, val, color="#fff"):
    col.markdown(f'<div class="glass"><div class="kpi-label">{label}</div><div class="kpi-val" style="color:{color}">{val}</div></div>', unsafe_allow_html=True)

def gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number={"suffix": "%", "font": {"color": "#fff"}},
        gauge={"axis": {"range": [0, 100], "tickcolor": "#9fe8c0"},
               "bar": {"color": "#22ff88"}, "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
               "steps": [{"range": [0, 25], "color": "rgba(34,197,94,.35)"},
                         {"range": [25, 50], "color": "rgba(250,204,21,.35)"},
                         {"range": [50, 75], "color": "rgba(251,146,60,.35)"},
                         {"range": [75, 100], "color": "rgba(239,68,68,.4)"}]}))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=270,
                      margin=dict(l=20, r=20, t=50, b=10), title="Overall threat meter")
    return fig

def story(d):
    parts = []
    for k, t in [("brute_force", "password-guessing attempt"),
                 ("command_exec", "break-in with commands"),
                 ("scanning", "door-knocking scan")]:
        c = int((d["predicted"] == k).sum())
        if c:
            parts.append(f"{c} {t}{'s' if c > 1 else ''}")
    return ("In simple words: our decoy computer saw " + str(len(d)) + " visits (" +
            ", ".join(parts) + "). Every one was recorded, and no real system was touched.")

def feed_html(show, simple):
    out = ""
    for _, r in show.iterrows():
        col = COLOR[r["threat"]]
        txt = PLAIN[r["predicted"]] if simple else f'{r["predicted"]} · {r["confidence"]}% · {r["ip"]}'
        out += (f'<div class="feed" style="border-left:4px solid {col}">'
                f'<span class="badge" style="color:{col};border-color:{col}">{r["threat"]}</span>'
                f'<b>{r["start"].strftime("%d %b %H:%M:%S")}</b> &nbsp; {txt}'
                f'<div class="sm">Recommended trap: {r["trap"]}</div></div>')
    return out

STEPS = [
    ("🎯", "Attacker", "SSH/Telnet probes and login attempts", "Someone tries to break in"),
    ("🍯", "Honeypot", "Cowrie records every session", "A decoy computer that looks real"),
    ("📊", "Features", "Failed logins, commands, downloads", "We count what the attacker did"),
    ("🧠", "ML Model", "Random Forest predicts attack type", "AI decides what kind of attack it is"),
    ("⚖️", "Decision", "Maps attack to threat level + trap", "We decide how dangerous it is"),
    ("🖥️", "Dashboard", "Live view, refreshes every 5 s", "You see it all here, live"),
]

st.markdown('<h1 class="title">🍯 AI-DecepNet</h1><p class="sub"><span class="live"><span class="dot"></span>LIVE</span> · adaptive honeypot threat dashboard · auto-refresh 5s</p>', unsafe_allow_html=True)

st.sidebar.header("Controls")
simple = st.sidebar.toggle("Simple mode (non-technical)", value=False)
hist = st.sidebar.checkbox("Include recorded dataset (160 sessions)", value=False)
types = ["brute_force", "command_exec", "scanning"]
sel = st.sidebar.multiselect("Attack type", types, default=types)
lv = st.sidebar.multiselect("Threat level", ORDER, default=ORDER)
conf = st.sidebar.slider("Min confidence %", 0, 100, 0)

def show_status():
    try:
        s = json.load(open("status.json", encoding="utf-8"))
    except Exception:
        st.markdown('<div class="glass">⚪ Adaptive engine offline (engine.py chalao)</div>', unsafe_allow_html=True)
        return
    col = COLOR.get(s["level"], "#22ff88")
    mark = "✅ Trap applied" if s.get("applied") else "⚠️ Apply failed"
    st.markdown(f'<div class="glass" style="border-left:4px solid {col}"><b style="color:{col}">● {s["level"]}</b> &nbsp; {mark} &nbsp; <span class="sm">{s["action"]} · {s["failed_60s"]} failed logins in last 60s · {s["time"]}</span></div>', unsafe_allow_html=True)

@st.fragment(run_every=5)
def dashboard():
    show_status()
    st.write("")
    df = parse_live()
    if hist:
        df = pd.concat([df, load_history()], ignore_index=True)
    if df.empty:
        st.info("Abhi koi session nahi. Ek test SSH attack karo: ssh -p 2222 admin@localhost")
        return
    d = df[df["predicted"].isin(sel) & df["threat"].isin(lv) & (df["confidence"] >= conf)]
    if d.empty:
        st.warning("Is filter pe koi session nahi mila.")
        return

    if simple:
        st.markdown(f'<div class="glass story">{story(d)}</div>', unsafe_allow_html=True)
        st.write("")

    L = ("Total visits", "Dangerous", "Attack kinds", "AI sureness") if simple else \
        ("Total sessions", "Critical", "Attack types", "Avg confidence")
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, L[0], len(d))
    kpi(c2, L[1], int((d["threat"] == "Critical").sum()), COLOR["Critical"])
    kpi(c3, L[2], d["predicted"].nunique(), "#22ff88")
    kpi(c4, L[3], f'{d["confidence"].mean():.1f}%', "#a7f3d0")
    st.write("")

    t1, t2, t3, t4 = st.tabs(["📊 Overview", "🔴 Live Feed", "🔍 Inspect", "🧠 How it works"])

    with t1:
        score = d["threat"].map({o: i for i, o in enumerate(ORDER)}).mean() / 3 * 100
        a, b = st.columns(2)
        a.plotly_chart(gauge(score), use_container_width=True, key="g1")
        b.plotly_chart(style(px.pie(d, names="predicted", hole=0.6, title="Attack types",
                                    color_discrete_sequence=["#22ff88", "#a7f3d0", "#10b981"])),
                       use_container_width=True, key="p1")
        x, y = st.columns([2, 3])
        cnt = pd.DataFrame({"threat": ORDER, "sessions": [int((d["threat"] == o).sum()) for o in ORDER]})
        x.plotly_chart(style(px.bar(cnt, x="threat", y="sessions", color="threat",
                                    color_discrete_map=COLOR, title="Threat levels")),
                       use_container_width=True, key="b1")
        y.plotly_chart(style(px.scatter(d, x="start", y="confidence", color="threat", symbol="predicted",
                                        color_discrete_map=COLOR, hover_data=["session", "trap", "source"],
                                        title="Sessions timeline")),
                       use_container_width=True, key="s1")

    with t2:
        show = d.sort_values("start", ascending=False).head(30)
        st.markdown('<div class="scrollbox">' + feed_html(show, simple) + '</div>', unsafe_allow_html=True)

    with t3:
        pick = d.sort_values("start", ascending=False).head(50)
        sid = st.selectbox("Choose a session", pick["session"].tolist(), key="sid_pick")
        r = pick[pick["session"] == sid].iloc[0]
        st.markdown(
            f'<div class="glass"><div class="row" style="color:{COLOR[r["threat"]]}"><span class="dot"></span><b>{r["threat"]}</b></div>'
            f'<div class="row">Attack: <b>{r["predicted"]}</b> ({r["confidence"]}%)</div>'
            f'<div class="row">From IP: <b>{r["ip"]}</b></div>'
            f'<div class="row">Recommended trap: <b>{r["trap"]}</b></div>'
            f'<div class="row">Action: {r["action"]}</div></div>', unsafe_allow_html=True)
        c = r["cmds"] if isinstance(r["cmds"], str) else ""
        body = html.escape(c).replace("\n", "<br>$ ") if c else "(no commands in this session)"
        st.markdown(f'<div class="term">$ {body}</div>', unsafe_allow_html=True)

    with t4:
        cards = "".join(
            f'<div class="step"><div class="ic">{ic}</div><b>{n}</b><div class="sm">{s if simple else t}</div></div>'
            for ic, n, t, s in STEPS)
        st.markdown(f'<div class="flow">{cards}</div>', unsafe_allow_html=True)

dashboard()