# -*- coding: utf-8 -*-
"""
큐테크코리아 AIoT SaaS 관제 데모 (VC 투자 심의 시연용)
CUETECH KOREA · B2G/B2B Underground Infrastructure Intelligence
테마: Enterprise Light (Clean White)

실행:
    pip install streamlit plotly pandas numpy
    streamlit run app_demo.py
"""

import base64
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ══════════════════════════════════════════════════════════════════════════
# 브랜드 토큰 — Enterprise Light
# ══════════════════════════════════════════════════════════════════════════
BG     = "#F8FAFC"   # 배경 (쿨그레이 화이트)
PANEL  = "#FFFFFF"   # 패널
BORDER = "#E2E8F0"   # 테두리
TXT    = "#334155"   # 본문 (진회색)
TXT_HI = "#0F172A"   # 강조 (짙은 네이비)
MUTED  = "#64748B"   # 보조
BLUE   = "#2563EB"   # 포인트 (엔터프라이즈 블루)
NAVY   = "#1F3864"
GREEN  = "#16A34A"   # 정상
WARN   = "#DC2626"   # 위험

FONT = ('-apple-system, BlinkMacSystemFont, "SF Pro Display", "Pretendard", '
        '"Malgun Gothic", "Apple SD Gothic Neo", sans-serif')

st.set_page_config(page_title="CUETECH KOREA · AIoT 통합 관제",
                   page_icon="◆", layout="wide",
                   initial_sidebar_state="collapsed")

st.markdown(f"""
<style>
  .stApp {{ background:{BG}; }}
  html, body, [class*="css"] {{ font-family:{FONT}; color:{TXT}; }}
  #MainMenu, header, footer {{ visibility:hidden; }}
  .block-container {{ padding:2.6rem 3.4rem 3rem 3.4rem; max-width:1620px; }}

  .so-eyebrow {{ letter-spacing:.30em; font-size:.78rem; color:{BLUE};
                 font-weight:700; text-transform:uppercase; }}
  .so-title {{ font-size:2.1rem; font-weight:800; color:{TXT_HI};
               margin:.15rem 0; letter-spacing:-.01em; }}
  .so-sub {{ font-size:.98rem; color:{MUTED}; }}
  .so-rule {{ height:3px; width:60px; background:linear-gradient(90deg,{BLUE},{GREEN});
              border:none; margin:.9rem 0 1.3rem 0; border-radius:3px; }}

  .panel-h {{ font-size:1.05rem; font-weight:800; color:{TXT_HI}; margin:.1rem 0 .1rem 0; }}
  .panel-c {{ font-size:.82rem; color:{MUTED}; margin-bottom:.5rem; }}

  div[data-testid="stMetric"] {{
      background:{PANEL}; border:1px solid {BORDER}; border-radius:16px;
      padding:1.0rem 1.2rem; box-shadow:0 1px 3px rgba(15,23,42,.06); }}
  div[data-testid="stMetricLabel"] p {{ font-size:.8rem; color:{MUTED}; font-weight:700; }}
  div[data-testid="stMetricValue"] {{ font-size:1.7rem; font-weight:800; color:{TXT_HI}; }}

  .glass {{ background:{PANEL}; border:1px solid {BORDER}; border-radius:16px;
            padding:1.1rem 1.3rem; box-shadow:0 1px 3px rgba(15,23,42,.06); }}

  /* 위험 점멸 배지 */
  @keyframes blink {{ 0%,100% {{opacity:1;}} 50% {{opacity:.3;}} }}
  .chip {{ display:inline-block; padding:.28rem .8rem; border-radius:999px;
           font-size:.8rem; font-weight:800; }}
  .chip-ok   {{ background:#F0FDF4; color:{GREEN}; border:1px solid #BBF7D0; }}
  .chip-warn {{ background:#FEF2F2; color:{WARN}; border:1px solid #FECACA;
                animation:blink 1.1s infinite; }}
  .chip-sync {{ background:#EFF6FF; color:{BLUE}; border:1px solid #BFDBFE; }}

  .plan {{ border:1px solid {BORDER}; border-radius:14px; padding:.85rem 1rem;
           margin-bottom:.55rem; background:{PANEL}; }}
  .plan b {{ color:{TXT_HI}; font-size:.95rem; }}
  .plan .pr {{ float:right; color:{BLUE}; font-weight:800; }}
  .plan .ds {{ font-size:.78rem; color:{MUTED}; margin-top:.15rem; }}

  .stButton>button {{ width:100%; background:{NAVY}; color:#fff; font-weight:800;
      font-size:1.0rem; border:none; border-radius:12px; padding:.72rem 1rem;
      box-shadow:0 2px 8px rgba(31,56,100,.25); }}
  .stButton>button:hover {{ filter:brightness(1.12); }}
  div[data-testid="stDownloadButton"]>button {{ width:100%; background:#fff;
      color:{NAVY}; font-weight:800; border:1.5px solid {NAVY}; border-radius:12px;
      padding:.66rem 1rem; }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# 가상 데이터 (외부 DB 없음 · 시드 고정으로 재현 가능)
# ══════════════════════════════════════════════════════════════════════════
rng = np.random.default_rng(42)
NOW = datetime.now()

BASE_LAT, BASE_LON = 35.531, 129.352   # 울산 산업단지 인근
NODE_TYPES = ["맨홀", "맨홀", "맨홀", "지하관로", "지하관로", "맨홀",
              "지하관로", "맨홀", "물순환", "맨홀", "지하관로", "맨홀"]

nodes = pd.DataFrame({
    "id":   [f"ND-{i+1:03d}" for i in range(12)],
    "type": NODE_TYPES,
    "lat":  BASE_LAT + rng.uniform(-0.028, 0.028, 12),
    "lon":  BASE_LON + rng.uniform(-0.040, 0.040, 12),
    "gas":  np.round(rng.uniform(8, 28, 12), 1),
    "temp": np.round(rng.uniform(18, 26, 12), 1),
    "hum":  np.round(rng.uniform(55, 78, 12), 1),
    "batt": rng.integers(72, 100, 12),
})
nodes["name"] = nodes["type"] + "-" + nodes["id"].str[-3:]

DANGER_IDX = [3, 9]
nodes["status"] = "정상"
nodes.loc[DANGER_IDX, "status"] = "위험"
nodes.loc[DANGER_IDX, "gas"] = [61.4, 47.8]

def series_24h(node_row):
    seed = int(node_row["id"][-3:])
    r = np.random.default_rng(seed)
    idx = pd.date_range(NOW - timedelta(hours=23), NOW, freq="h")
    base_gas = node_row["gas"]
    if node_row["status"] == "위험":
        trend = np.concatenate([np.linspace(12, 18, 14), np.linspace(18, base_gas, 10)])
        gas = trend + r.normal(0, 1.1, 24)
    else:
        gas = base_gas + r.normal(0, 1.6, 24)
    temp = node_row["temp"] + np.sin(np.linspace(0, 2*np.pi, 24)) * 1.8 + r.normal(0, .3, 24)
    hum  = node_row["hum"]  + np.cos(np.linspace(0, 2*np.pi, 24)) * 3.0 + r.normal(0, .8, 24)
    return pd.DataFrame({"time": idx, "가스(ppm)": gas, "온도(℃)": temp, "습도(%)": hum})

def ai_prob(node_row):
    if node_row["status"] == "위험":
        return float(np.clip(60 + (node_row["gas"] - 40) * 1.3, 60, 97))
    return float(np.clip(node_row["gas"] * 0.35 + 1.5, 1, 12))

nodes["ai"] = nodes.apply(ai_prob, axis=1).round(1)

danger_n = int((nodes["status"] == "위험").sum())
avg_ai = nodes["ai"].mean()
GRADE = ("A" if danger_n == 0 and avg_ai < 6 else
         "B" if danger_n == 0 else
         "C" if danger_n <= 2 else
         "D" if danger_n <= 4 else "F")
GRADE_COLOR = {"A": GREEN, "B": GREEN, "C": "#D97706", "D": WARN, "F": WARN}[GRADE]

# ══════════════════════════════════════════════════════════════════════════
# A4 리포트 (HTML) — 결재란 · 등급 · 이상 징후 · CUETECH 인증
# ══════════════════════════════════════════════════════════════════════════
def build_report_html() -> str:
    anomalies = nodes[nodes["status"] == "위험"]
    rows = "".join(
        f"<tr><td>{r.name}</td><td>{r.type}</td><td class='warn'>{r.gas} ppm</td>"
        f"<td class='warn'>{r.ai}%</td><td>가스 농도 급상승 — 현장 점검 요망</td></tr>"
        for r in anomalies.itertuples()
    ) or "<tr><td colspan='5'>금일 이상 징후 없음</td></tr>"

    summary_rows = "".join(
        f"<tr><td>{r.name}</td><td>{r.type}</td><td>{r.status}</td>"
        f"<td>{r.gas}</td><td>{r.temp}</td><td>{r.hum}</td><td>{r.batt}%</td><td>{r.ai}%</td></tr>"
        for r in nodes.itertuples()
    )

    return f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<title>일간 통합 안전 리포트</title>
<style>
  @page {{ size:A4; margin:0; }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif; color:#1F2733;
          background:#EDEFF3; }}
  .page {{ width:210mm; min-height:297mm; margin:0 auto; background:#fff;
           padding:16mm 15mm 14mm 15mm; position:relative; }}
  .top {{ display:flex; justify-content:space-between; align-items:flex-start; }}
  .brand {{ font-size:9pt; letter-spacing:.22em; color:#2E4A7A; font-weight:700; }}
  h1 {{ font-size:19pt; color:#1F3864; margin:2mm 0 1mm 0; }}
  .meta {{ font-size:9pt; color:#6B7280; margin-bottom:5mm; }}
  .approve {{ border-collapse:collapse; }}
  .approve th, .approve td {{ border:1px solid #33415C; font-size:8pt; text-align:center; }}
  .approve th {{ background:#EEF2F8; width:18mm; padding:1.6mm 0; color:#1F3864; }}
  .approve td {{ height:16mm; width:18mm; }}
  h2 {{ font-size:11.5pt; color:#1F3864; border-bottom:2px solid #1F3864;
        padding-bottom:1.2mm; margin:6mm 0 2.6mm 0; }}
  table.data {{ width:100%; border-collapse:collapse; font-size:8.6pt; }}
  table.data th {{ background:#1F3864; color:#fff; padding:1.8mm 1mm; border:1px solid #33415C; }}
  table.data td {{ border:1px solid #C9D2E0; padding:1.5mm 1mm; text-align:center; }}
  table.data tr:nth-child(even) td {{ background:#F4F7FB; }}
  .warn {{ color:#C00000; font-weight:700; }}
  .gradebox {{ display:flex; gap:6mm; align-items:center; border:1px solid #C9D2E0;
               border-radius:3mm; padding:4mm 6mm; background:#F8FAFD; }}
  .gletter {{ font-size:30pt; font-weight:800; color:{GRADE_COLOR};
              border:3px solid {GRADE_COLOR}; border-radius:50%;
              width:22mm; height:22mm; display:flex; align-items:center; justify-content:center; }}
  .gdesc {{ font-size:9.4pt; line-height:1.7; }}
  .seal {{ position:absolute; right:16mm; bottom:20mm; width:24mm; height:24mm;
           border:2.4pt double #C0392B; border-radius:50%; color:#C0392B;
           display:flex; align-items:center; justify-content:center; text-align:center;
           font-size:8pt; font-weight:800; transform:rotate(-8deg); opacity:.85;
           letter-spacing:.08em; }}
  .foot {{ position:absolute; bottom:10mm; left:15mm; right:15mm;
           border-top:1px solid #C9D2E0; padding-top:2mm;
           font-size:8pt; color:#8A94A6; display:flex; justify-content:space-between; }}
  .printbtn {{ position:fixed; top:10px; right:12px; background:#1F3864; color:#fff;
               border:none; border-radius:8px; padding:9px 16px; font-weight:700;
               cursor:pointer; }}
  @media print {{ .printbtn {{ display:none; }} body {{ background:#fff; }} }}
</style></head><body>
<button class="printbtn" onclick="window.print()">🖨 인쇄 / PDF 저장</button>
<div class="page">
  <div class="top">
    <div>
      <div class="brand">CUETECH KOREA · AI INFRASTRUCTURE INTELLIGENCE</div>
      <h1>일간 통합 안전 리포트</h1>
      <div class="meta">보고 일자: {NOW.strftime('%Y년 %m월 %d일 %H:%M')} 기준 &nbsp;·&nbsp;
        관제 구역: 울산 산업단지 지하 인프라 &nbsp;·&nbsp; 문서번호: CT-{NOW.strftime('%Y%m%d')}-D01</div>
    </div>
    <table class="approve"><tr><th>기안</th><th>검토</th><th>승인</th></tr>
      <tr><td></td><td></td><td></td></tr></table>
  </div>

  <h2>1. AI 종합 안전 등급</h2>
  <div class="gradebox">
    <div class="gletter">{GRADE}</div>
    <div class="gdesc">
      전체 <b>{len(nodes)}개</b> 노드 중 정상 <b>{len(nodes)-danger_n}개</b> ·
      <span class="warn">위험 {danger_n}개</span><br>
      평균 AI 사고 예측 확률 <b>{avg_ai:.1f}%</b> ·
      최고 위험 노드 <b>{nodes.loc[nodes['ai'].idxmax(),'name']}
      ({nodes['ai'].max():.1f}%)</b><br>
      판정 근거: 가스 농도 임계(40ppm) 초과 노드 및 24시간 상승 추세 감지 결과를
      종합하여 산정하였습니다.
    </div>
  </div>

  <h2>2. 이상 징후 발생 리스트</h2>
  <table class="data">
    <tr><th>노드</th><th>유형</th><th>가스 농도</th><th>AI 예측 확률</th><th>조치 권고</th></tr>
    {rows}
  </table>

  <h2>3. 전체 노드 상태 요약</h2>
  <table class="data">
    <tr><th>노드</th><th>유형</th><th>상태</th><th>가스(ppm)</th><th>온도(℃)</th>
        <th>습도(%)</th><th>배터리</th><th>AI 확률</th></tr>
    {summary_rows}
  </table>

  <div class="seal">CUETECH<br>안전인증</div>
  <div class="foot">
    <span>본 보고서는 AI 분석 플랫폼에 의해 자동 생성되었습니다.</span>
    <span>ⓒ CUETECH KOREA — Confidential</span>
  </div>
</div></body></html>"""

# ══════════════════════════════════════════════════════════════════════════
# 헤더
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="so-eyebrow">CUETECH KOREA · AIoT SaaS Control</div>', unsafe_allow_html=True)
st.markdown('<div class="so-title">지하 인프라 통합 관제 플랫폼</div>', unsafe_allow_html=True)
st.markdown('<div class="so-sub">VC 투자 심의 시연 · 실시간 관제 → AI 예측 → 구독 리포트 · 데모 데이터</div>',
            unsafe_allow_html=True)
st.markdown('<hr class="so-rule">', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4, gap="medium")
k1.metric("관제 노드", f"{len(nodes)} 개")
k2.metric("정상 가동", f"{len(nodes)-danger_n} 개")
k3.metric("위험 감지", f"{danger_n} 개", delta="점검 필요", delta_color="inverse")
k4.metric("AI 종합 안전 등급", GRADE)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# 3-패널 레이아웃 (지도 클릭 ↔ AI 패널 동기화)
# ══════════════════════════════════════════════════════════════════════════
if "node_sel" not in st.session_state:
    st.session_state["node_sel"] = nodes.loc[DANGER_IDX[0], "name"]

left, right = st.columns([1.15, 1], gap="large")

# ── A. 실시간 관제 (좌측 · 지도 · 클릭 연동) ──
with left:
    st.markdown('<div class="panel-h">A. 실시간 관제</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-c">울산 산업단지 · 센서 노드를 <b>클릭</b>하면 우측 AI 패널이 '
                '해당 노드로 전환됩니다 (<span style="color:#16A34A;">●</span> 정상 / '
                '<span style="color:#DC2626;">●</span> 위험 점멸)</div>', unsafe_allow_html=True)

    ok = nodes[nodes["status"] == "정상"]
    ng = nodes[nodes["status"] == "위험"]

    fig_map = go.Figure()
    # 위험 — 이중 헤일로 (클릭 대상은 내부 마커)
    fig_map.add_trace(go.Scattermap(
        lat=ng["lat"], lon=ng["lon"], mode="markers", name="위험(외곽)",
        marker=dict(size=34, color=WARN, opacity=0.18),
        customdata=ng["name"], hoverinfo="skip", showlegend=False))
    fig_map.add_trace(go.Scattermap(
        lat=ng["lat"], lon=ng["lon"], mode="markers+text", name="위험",
        marker=dict(size=16, color=WARN, opacity=0.95),
        text=ng["name"], textposition="top center",
        textfont=dict(color=WARN, size=11),
        customdata=ng["name"],
        hovertemplate="<b>%{text}</b> — 클릭하여 상세<extra></extra>"))
    fig_map.add_trace(go.Scattermap(
        lat=ok["lat"], lon=ok["lon"], mode="markers", name="정상",
        marker=dict(size=12, color=GREEN, opacity=0.9),
        text=ok["name"], customdata=ok["name"],
        hovertemplate="<b>%{text}</b> — 클릭하여 상세<extra></extra>"))
    fig_map.update_layout(
        map=dict(style="carto-positron",
                 center=dict(lat=BASE_LAT, lon=BASE_LON), zoom=12.1),
        height=520, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=0.02, x=0.02,
                    font=dict(color=TXT, size=12), bgcolor="rgba(255,255,255,.75)"),
        hoverlabel=dict(bgcolor="#0F172A", font=dict(family=FONT, color="#FFFFFF")))

    # ★ 지도 클릭 이벤트 → session_state 동기화
    event = st.plotly_chart(fig_map, width="stretch", key="map",
                            on_select="rerun", selection_mode="points",
                            config={"displayModeBar": False})
    try:
        pts = event["selection"]["points"] if event else []
    except Exception:
        pts = []
    if pts:
        clicked = pts[0].get("customdata")
        if isinstance(clicked, (list, tuple)):
            clicked = clicked[0]
        if clicked in nodes["name"].values and clicked != st.session_state["node_sel"]:
            st.session_state["node_sel"] = clicked

    chips = " ".join(
        f'<span class="chip chip-warn">⚠ {r["name"]} · {r["gas"]}ppm</span>'
        for _, r in ng.iterrows())
    st.markdown(f'<div style="margin-top:.3rem;">{chips}</div>', unsafe_allow_html=True)

# ── B + C (우측) ──
with right:
    st.markdown('<div class="panel-h">B. AI 예측</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-c">지도 클릭 또는 목록 선택 → 최근 24시간 추이 및 사고 예측 확률</div>',
                unsafe_allow_html=True)

    sel_name = st.selectbox("관측 노드", nodes["name"].tolist(),
                            key="node_sel", label_visibility="collapsed")
    sel = nodes[nodes["name"] == sel_name].iloc[0]
    ts = series_24h(sel)

    st.markdown(f'<span class="chip chip-sync">🔗 지도 연동 · 현재 노드: {sel_name}</span>',
                unsafe_allow_html=True)
    st.markdown('<div style="margin-top:.5rem;"></div>', unsafe_allow_html=True)

    b1, b2 = st.columns([1, 1.6], gap="medium")
    with b1:
        prob = sel["ai"]
        color = WARN if prob >= 50 else (BLUE if prob >= 15 else GREEN)
        badge = ('<span class="chip chip-warn">위험 · 점검 요망</span>'
                 if sel["status"] == "위험" else '<span class="chip chip-ok">정상</span>')
        st.markdown(
            f'<div class="glass" style="text-align:center;">'
            f'<div style="font-size:.8rem;color:{MUTED};font-weight:700;">AI 사고 예측 확률</div>'
            f'<div style="font-size:2.7rem;font-weight:800;color:{color};line-height:1.15;">{prob:.1f}%</div>'
            f'<div style="margin-top:.35rem;">{badge}</div>'
            f'<div style="margin-top:.6rem;font-size:.76rem;color:{MUTED};">'
            f'가스 {sel["gas"]}ppm · 배터리 {sel["batt"]}%</div></div>',
            unsafe_allow_html=True)
    with b2:
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(x=ts["time"], y=ts["가스(ppm)"], name="가스(ppm)",
                                    line=dict(color=BLUE, width=2.6),
                                    hovertemplate="%{y:.1f} ppm<extra>가스</extra>"))
        fig_ts.add_trace(go.Scatter(x=ts["time"], y=ts["온도(℃)"], name="온도(℃)",
                                    line=dict(color="#94A3B8", width=1.6, dash="dot"),
                                    hovertemplate="%{y:.1f} ℃<extra>온도</extra>"))
        fig_ts.add_trace(go.Scatter(x=ts["time"], y=ts["습도(%)"], name="습도(%)",
                                    line=dict(color=GREEN, width=1.6, dash="dot"),
                                    hovertemplate="%{y:.1f} %<extra>습도</extra>"))
        if sel["status"] == "위험":
            fig_ts.add_hline(y=40, line_color=WARN, line_dash="dash",
                             annotation_text="임계 40ppm",
                             annotation_font_color=WARN)
        fig_ts.update_layout(height=252, margin=dict(l=6, r=6, t=8, b=4),
                             paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                             font=dict(family=FONT, color=TXT, size=12),
                             legend=dict(orientation="h", y=1.14, x=0, font=dict(size=11)),
                             hovermode="x unified",
                             hoverlabel=dict(bgcolor="#0F172A", font=dict(color="#FFFFFF")))
        fig_ts.update_xaxes(showgrid=False, tickfont=dict(color=MUTED, size=10))
        fig_ts.update_yaxes(showgrid=True, gridcolor=BORDER, tickfont=dict(color=MUTED, size=10))
        st.plotly_chart(fig_ts, width="stretch", config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="panel-h">C. 구독 서비스 · Data-as-a-Service</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-c">데이터 자산화 기반 AI 구독 — 노드당 월 요금</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
<div class="glass">
  <div class="plan"><b>Basic</b><span class="pr">₩29,000<span style="font-size:.7rem;color:{MUTED};">/노드·월</span></span>
    <div class="ds">실시간 관제 · 임계 알림 · 월간 리포트</div></div>
  <div class="plan" style="border-color:{BLUE};"><b>Pro ★</b><span class="pr">₩59,000<span style="font-size:.7rem;color:{MUTED};">/노드·월</span></span>
    <div class="ds">AI 사고 예측 · 일간 통합 리포트 · 위험등급 자동보고</div></div>
  <div class="plan"><b>Enterprise</b><span class="pr">협의</span>
    <div class="ds">전용 관제센터 연동 · API · 중대재해처벌법 대응 증적 패키지</div></div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div style="margin-top:.8rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-h" style="font-size:.95rem;">📄 안전 진단 리포트 생성</div>',
                unsafe_allow_html=True)

    if st.button("일간 통합 리포트 생성"):
        st.session_state["report_html"] = build_report_html()

    if "report_html" in st.session_state:
        html = st.session_state["report_html"]
        st.download_button("⬇ 리포트 다운로드 (HTML · 인쇄→PDF 저장)",
                           data=html.encode("utf-8"),
                           file_name=f"CueTech_일간통합리포트_{NOW.strftime('%Y%m%d')}.html",
                           mime="text/html")
        with st.expander("리포트 미리보기 (A4)", expanded=True):
            b64 = base64.b64encode(html.encode("utf-8")).decode()
            st.iframe(f"data:text/html;base64,{b64}", height=760)

st.markdown(
    f'<div style="margin-top:2.2rem;font-size:.74rem;color:{MUTED};text-align:center;">'
    f'ⓒ CUETECH KOREA · 본 화면은 투자 심의용 데모이며 모든 데이터는 가상으로 생성되었습니다.'
    f'</div>', unsafe_allow_html=True)
