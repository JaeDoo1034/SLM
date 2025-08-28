import streamlit as st
from textwrap import dedent
import re

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="MY 퇴직연금관리",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="expanded",   # 사이드 컨트롤 보이도록
)

# ---------------- Helpers ----------------
def H(s: str) -> str:
    s = dedent(s)
    s = re.sub(r"\n[ \t]+", "\n", s)
    return s.strip()

# ---------------- State ----------------
if "notify_opt_in" not in st.session_state:
    st.session_state.notify_opt_in = False
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "rise"  # 탭 기본값

# ---------------- Data ----------------
eval_amount = "15,525,024원"
principal   = "13,910,000원"
acc_profit  = "+1,615,024원"
acc_return  = "+11.61%"

alloc = {
    "원리금보장": {"pct": 0.00, "color": "#3b82f6", "amount": "0원", "ratio": "0.00%"},
    "투자상품":   {"pct": 98.11, "color": "#10b981","amount": "15,232,331원","ratio": "98.11%", "chg": "+15.41%"},
    "현금성자산": {"pct": 1.89, "color": "#f59e0b","amount": "292,693원",  "ratio": "1.89%"},
}

TABS = [
    {"id":"rise",        "label":"RISE 코리아금융고배당", "content": """
✅ 주요 요약

- **외국인 투자자, 우리금융지주 주식 대량 순매수**<br>최근 한 달 간 외국인은 우리금융지주를 490.4만 주 순매수(비중 52.6%).
- **우리금융지주, 2분기 순이익 감소 예상**<br>판관비 증가 영향으로 전년 대비 -8.6% 전망.
- **4대 금융지주, 비이자이익 증가**<br>환율 안정·수수료 확대로 2분기 순이익 +5.3%.

🔑 키워드: 외국인, 우리금융지주, 순매수, 비이자이익.
""" },
    {"id":"kr_div",      "label":"국내배당주배당주배당주주주주주주주주", "content": """
✅ 포인트
- 금융/에너지/통신 고배당 업종 비중 ↑
- 분기배당·자사주 기업 위주로 배당락 방어
- ETF 바스켓로 종목 리스크 분산
""" },
    {"id":"us_div",      "label":"미국배당주", "content": """
✅ 포인트
- 배당왕/배당귀족(25~50년 증배) 중심
- 환헤지/무헤지 혼합으로 달러분산
- 필수소비재·유틸리티·헬스케어 선호
""" },
    {"id":"bond_mix",    "label":"채권혼합", "content": """
✅ 포인트
- 채권 50~70% + 배당 30~50% 구성
- 금리 피크아웃 구간 듀레이션 4~6년
- 저변동 배당 팩터로 변동성 완화
""" },
    {"id":"global_etf",  "label":"글로벌ETF", "content": """
✅ 포인트
- 선진국/신흥국 배당 ETF로 지역분산
- 저변동+퀄리티 팩터 조합
- 월/분기배당으로 현금흐름 설계
""" },
    {"id":"cash",        "label":"현금성", "content": """
✅ 포인트
- 단기 MMF/머니마켓 ETF
- 유동성 버퍼 3~6개월 권장
- 금리 하락 시 듀레이션 자산으로 리밸런싱
""" },
]

news_items = [
    ("새소식", "2025년 8월 퇴직연금 DC·IRP 운용상품 안내", "업데이트된 라인업과 수수료 안내를 확인해 보세요."),
    ("투자전략", "잭슨홀 경계감 고조… S&P500 5거래일 하락", "연준 의장 연설 앞두고 변동성 확대 국면."),
]
quick_actions = [
    ("🧾", "IRP 입금하기"),
    ("👜", "입금예정상품 등록/변경"),
    ("📦", "보유상품 변경"),
    ("🔁", "자동이체 관리"),
    ("📈", "수익률 조회"),
]

# ---------------- CSS ----------------
CSS = H("""
html, body, .block-container { background:#f6f8fb !important; }
section.main > div { padding-top: 8px; }

/* 상단 헤더 */
.topbar-wrap { display:flex; justify-content:center; margin:10px auto 14px; max-width:520px; padding:0 8px; }
.topbar {
  width:100%; height:64px; position:relative; display:flex; align-items:center; justify-content:center;
  background:#fff; border:1px solid #edf1f7; border-radius:22px; box-shadow:0 8px 20px rgba(23,30,60,0.08), inset 0 -1px 0 #f0f3f8;
}
.topbar-title { font-weight:900; font-size:20px; color:#1b233d; }
.topbar-back { position:absolute; left:10px; top:50%; transform:translateY(-50%);
  width:38px; height:38px; border-radius:999px; display:grid; place-items:center;
  border:1px solid #e6ebf3; color:#445; background:#fff; box-shadow:0 4px 10px rgba(23,30,60,0.06); font-size:18px; }

/* 공통 카드 */
.phone-wrap{ display:flex; justify-content:center; margin:0 auto 24px; max-width:520px; }
.phone{ width:100%; }
.card{ background:#fff; border:1px solid #e7ebf3; border-radius:18px; padding:16px; box-shadow:0 6px 16px rgba(23,30,60,0.06); margin:4px 4px; }
.section-title{ font-size:16px; font-weight:900; color:#1b233d; margin-bottom:10px; }
.eval-amount{ font-size:34px; font-weight:900; color:#0f1a31; margin-top:2px; }
.row{ display:flex; align-items:center; justify-content:space-between; gap:10px; margin:10px 0 0; }

/* 운용현황 */
.alloc-bar{ width:100%; height:16px; background:#f0f3f8; border-radius:999px; overflow:hidden; box-shadow: inset 0 1px 2px rgba(15,23,42,0.06); }
.alloc-chunk{ height:100%; float:left; }
.legend{ display:flex; flex-direction:column; gap:10px; margin-top:10px; }
.actions{ display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:12px; }
.btn{ display:block; text-align:center; padding:12px 12px; border-radius:12px; border:1px solid #e7ebf3; font-weight:900; color:#1b233d; background:#fff; }

/* 프로모(알림받기) */
.promo-head-wrap { max-width:520px; margin:0 auto 0 !important; }
.promo-head { background:#fff; border:1px solid #e7ebf3; border-radius:18px 18px 0 0; padding:24px 20px; box-shadow:0 10px 24px rgba(23,30,60,.06); }
.promo-title{ font-weight:900; font-size:20px; color:#1b233d; text-align:center; }
.promo-desc { color:#5b6785; font-size:14px; text-align:center; margin-top:8px; }

div[data-testid="stVerticalBlock"]:has(.promo-cta-scope){
  max-width:520px; width:100%; margin:0 auto 24px !important;
  background:#fff; border:1px solid #e7ebf3; border-top:0; border-radius:0 0 18px 18px; padding:0 20px 20px !important; position:relative; top:-1px;
}
div[data-testid="stVerticalBlock"]:has(.promo-cta-scope) div[data-testid="stButton"]{ display:flex; justify-content:center; }
div[data-testid="stVerticalBlock"]:has(.promo-cta-scope) div[data-testid="stButton"] > button{
  width:min(420px, 88%) !important; height:56px !important; border-radius:16px !important;
  background:#eef5ff !important; border:1px solid #d7e6ff !important; color:#0b62e6 !important;
  font-weight:900 !important; font-size:18px !important; box-shadow:0 2px 0 rgba(11,98,230,.06) inset;
}

/* 요약 카드 */
.summary-wrap{ max-width:520px; margin:0 auto; }
.summary-card{ background:#fff; border:1px solid #e7ebf3; border-radius:18px; box-shadow:0 6px 16px rgba(23,30,60,.06); padding:18px; }
.summary-title{ font-size:22px; font-weight:900; color:#1765f0; margin-bottom:12px; text-align:center; }
.summary-panel{ background:#edf5ff; border:1px solid #d9e9ff; border-radius:16px; padding:16px 18px; }
.summary-badge{ display:inline-block; background:#e7f1ff; color:#0b62e6; font-weight:900; font-size:14px; border-radius:999px; padding:6px 10px; margin-bottom:8px; }
.summary-quote{ margin:10px 0 0; padding:12px 14px; background:#f4f8ff; border-left:4px solid #bcd9ff; color:#2b3a55; font-size:16px; border-radius:10px; }
.summary-link{ display:block; margin-top:12px; color:#0b62e6; font-weight:900; text-decoration:underline; text-align:center; }

/* ========= CHIP TAB BAR (가로 스크롤) ========= */
div[data-testid="stVerticalBlock"]:has(.chipbar-scope) { max-width:520px; margin:0 auto; }
div[data-testid="stVerticalBlock"]:has(.chipbar-scope) div[data-testid="stHorizontalBlock"]{
  display:flex !important; flex-wrap:nowrap !important; overflow-x:auto !important; overflow-y:hidden;
  gap:12px; padding:6px 4px; -webkit-overflow-scrolling:touch; scrollbar-width:thin; scrollbar-color:#c7d8ff transparent;
}
div[data-testid="stVerticalBlock"]:has(.chipbar-scope) div[data-testid="stHorizontalBlock"]::-webkit-scrollbar{ height:6px; }
div[data-testid="stVerticalBlock"]:has(.chipbar-scope) div[data-testid="stHorizontalBlock"]::-webkit-scrollbar-thumb{ background:#c7d8ff; border-radius:999px; }
div[data-testid="stVerticalBlock"]:has(.chipbar-scope) div[data-testid="stHorizontalBlock"]::-webkit-scrollbar-track{ background:transparent; }
div[data-testid="stVerticalBlock"]:has(.chipbar-scope) div[data-testid="stHorizontalBlock"] > div{ flex:0 0 auto !important; width:auto !important; }
div[data-testid="stVerticalBlock"]:has(.chipbar-scope) div[data-testid="stButton"] > button{
  width:auto !important; min-width:max-content !important; padding:10px 16px !important; border-radius:999px !important;
  background:#eef5ff !important; border:1px solid #d7e6ff !important; color:#0b62e6 !important; font-weight:900 !important; white-space:nowrap !important;
  box-shadow: inset 0 -2px 0 rgba(11,98,230,.06) !important;
}
div[data-testid="stVerticalBlock"]:has(.chipbar-scope) span.chip{
  display:inline-block; padding:10px 16px; border-radius:999px; white-space:nowrap; background:#0b62e6; border:1px solid #0b62e6;
  color:#fff; font-weight:900; box-shadow:0 6px 12px rgba(11,98,230,.22), inset 0 -2px 0 rgba(255,255,255,.15);
}

/* 새소식/바로가기 */
.news-card{ border:1px solid #e7ebf3; border-radius:16px; background:#fff; padding:0; overflow:hidden; }
.news-item{ padding:12px 14px; border-top:1px solid #eef2f7; }
.news-item:first-child{ border-top:0; }
.tag{ color:#0b62e6; font-weight:900; font-size:12px; }
.news-title{ font-weight:900; color:#0f1a31; margin:2px 0; }
.news-desc{ color:#5b6785; font-size:14px; }
.quick-list{ display:flex; flex-direction:column; }
.q-item{ display:flex; align-items:center; justify-content:space-between; padding:12px 4px; border-bottom:1px solid #eef2f7; }
.q-left{ display:flex; align-items:center; gap:10px; }
.q-icon{ width:28px; height:28px; display:grid; place-items:center; border-radius:8px; background:#f5f7fb; }
.q-text{ font-weight:800; color:#1b233d; }
.chev{ color:#9aa4b2; font-weight:900; }

/* ===== 중앙에 남아있을 수 있는 '알림 끄기' 버튼 블록 강제 숨김(안전장치) ===== */
section.main div[data-testid="stVerticalBlock"]:has(.summary-ctrl-marker) + div[data-testid="stVerticalBlock"]{
  display:none !important;
}

/* ===== 사이드바: 컨트롤 카드 ===== */
[data-testid="stSidebar"] div[data-testid="stVerticalBlock"]:has(.sidecard-marker){
  background:#fff; border:1px solid #e7ebf3; border-radius:16px; padding:14px;
  box-shadow:0 6px 16px rgba(23,30,60,.06); margin:10px 6px 18px;
}
[data-testid="stSidebar"] div[data-testid="stVerticalBlock"]:has(.sidecard-marker) .title{
  font-weight:900; color:#1b233d; margin-bottom:8px; font-size:16px;
}
[data-testid="stSidebar"] div[data-testid="stVerticalBlock"]:has(.sidecard-marker) .side-hint{
  color:#6b778c; font-size:12px; margin:6px 0 12px;
}
[data-testid="stSidebar"] div[data-testid="stVerticalBlock"]:has(.sidecard-marker) .stButton > button{
  width:100% !important; height:44px !important; border-radius:12px !important; font-weight:900 !important;
}
""")
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ---------------- Sidebar: 화면 제어(알림 on/off) ----------------
with st.sidebar:
    with st.container():
        # 마커 추가: 이 컨테이너를 사이드 카드로 스타일링
        st.markdown('<span class="sidecard-marker"></span>', unsafe_allow_html=True)
        st.markdown('<div class="title">화면 제어</div>', unsafe_allow_html=True)
        status_txt = "켜짐" if st.session_state.notify_opt_in else "꺼짐"
        st.markdown(f'<div class="side-hint">요약 알림 상태: <b>{status_txt}</b></div>', unsafe_allow_html=True)

        if st.session_state.notify_opt_in:
            if st.button("알림 끄기", key="sb_opt_out", use_container_width=True):
                st.session_state.notify_opt_in = False
                st.rerun()
        else:
            if st.button("알림 켜기", key="sb_opt_in", use_container_width=True):
                st.session_state.notify_opt_in = True
                st.rerun()

# ---------------- Top bar ----------------
st.markdown(H("""
<div class="topbar-wrap"><div class="topbar">
  <div class="topbar-back">‹</div>
  <div class="topbar-title">MY 퇴직연금관리</div>
</div></div>
"""), unsafe_allow_html=True)

# ---------------- 평가금액 카드 ----------------
st.markdown(H(f"""
<div class="phone-wrap"><div class="phone"><div class="card">
  <div style="color:#6b778c;font-weight:700;display:flex;align-items:center;gap:6px;">평가금액 <span style="font-size:13px; color:#9aa4b2;">ⓘ</span></div>
  <div class="eval-amount">{eval_amount}</div>
  <div style="color:#9aa4b2;font-size:13px;margin-top:4px;">전날(영업일 기준) 기준, 오늘 입금액은 반영 안 됨</div>
  <div class="row"><div style="color:#5b6785;font-weight:700;">원금</div><div style="color:#0f172a;font-weight:800;">{principal}</div></div>
  <div class="row"><div style="color:#5b6785;font-weight:700;">누적수익</div><div style="color:#ef4444;font-weight:800;">{acc_profit}</div></div>
  <div class="row"><div style="color:#5b6785;font-weight:700;">누적수익률</div><div style="color:#ef4444;font-weight:800;">{acc_return}</div></div>
</div></div></div>
"""), unsafe_allow_html=True)

# ---------------- 자산운용현황 ----------------
chunks_html = "".join(
    f'<div class="alloc-chunk" style="width:{max(0.0, min(100.0, v["pct"]))}%; background:{v["color"]};"></div>'
    for v in alloc.values()
)
legend_rows = []
for name, v in alloc.items():
    chg_html = f'<span style="color:#ef4444;font-weight:800;font-size:13px;margin-left:6px;">({v["chg"]})</span>' if "chg" in v else ""
    legend_rows.append(
        f'''<div style="display:flex; align-items:center; justify-content:space-between; gap:8px;">
               <div style="display:flex; align-items:center; gap:8px;">
                 <span style="width:10px; height:10px; border-radius:999px; display:inline-block; background:{v["color"]};"></span>
                 <span style="color:#41506b; font-weight:800;">{name}</span>
               </div>
               <div style="text-align:right;">
                 <div style="font-weight:900; color:#0f172a;">{v["amount"]}</div>
                 <div style="color:#8a96ab; font-weight:700; font-size:13px;">{v["ratio"]}{chg_html}</div>
               </div>
            </div>'''
    )
st.markdown(H(f"""
<div class="phone-wrap"><div class="phone"><div class="card">
  <div class="section-title">자산운용현황</div>
  <div class="alloc-bar">{chunks_html}</div>
  <div class="legend">{''.join(legend_rows)}</div>
  <div class="actions">
    <a class="btn" href="#">운용현황 조회</a>
    <a class="btn" href="#">퇴직연금 진단</a>
  </div>
</div></div></div>
"""), unsafe_allow_html=True)

# ---------------- 프로모 ↔ 요약 ----------------
if not st.session_state.notify_opt_in:
    # 프로모 카드 (상단 헤드 + CTA 하단)
    st.markdown(H("""
    <div class="promo-head-wrap"><div class="promo-head">
      <div class="promo-title">AI로 보유 종목의 소식을 요약해서 알려드릴까요?</div>
      <div class="promo-desc">아래 알림받기 버튼을 통해서 요약을 받아보세요.</div>
    </div></div>
    """), unsafe_allow_html=True)
    with st.container():
        st.markdown('<span class="promo-cta-scope"></span>', unsafe_allow_html=True)
        if st.button("알림받기", key="open_consent"):
            if hasattr(st, "dialog"):
                @st.dialog("알림 동의")
                def _dlg():
                    st.markdown(
                        '<div style="font-size:18px; line-height:1.7; color:#2a344e; text-align:center; margin:8px 0 18px;">'
                        '<b>고객님</b>, 보유하고 계신 <b>보유종목</b> 관련 소식을 AI로 요약해드릴게요.'
                        '</div>', unsafe_allow_html=True
                    )
                    c1, c2 = st.columns(2, gap="small")
                    with c1:
                        if st.button("동의하기", key="consent_yes", use_container_width=True):
                            st.session_state.notify_opt_in = True
                            st.rerun()
                    with c2:
                        st.button("닫기", key="consent_no", use_container_width=True)
                _dlg()
            else:
                st.session_state.notify_opt_in = True
                st.rerun()
else:
    # 칩 탭바 (가로 스크롤)
    with st.container():
        st.markdown('<div class="chipbar-wrap"><span class="chipbar-scope"></span></div>', unsafe_allow_html=True)
        cols = st.columns(len(TABS), gap="small")
        for i, t in enumerate(TABS):
            with cols[i]:
                if t["id"] == st.session_state.active_tab:
                    st.markdown(f'<span class="chip">{t["label"]}</span>', unsafe_allow_html=True)
                else:
                    if st.button(t["label"], key=f"chip_{t['id']}"):
                        st.session_state.active_tab = t["id"]
                        st.rerun()

    # 선택된 탭 내용
    tab = next((x for x in TABS if x["id"] == st.session_state.active_tab), TABS[0])
    st.markdown(H(f"""
    <div class="summary-wrap"><div class="summary-card">
      <div class="summary-title">7월 21일 오늘의 요약</div>
      <div class="summary-panel">
        <span class="summary-badge">{tab["label"]}</span>
        <div class="summary-quote">{tab["content"]}</div>
        <a class="summary-link" href="#">뉴스 보기</a>
      </div>
    </div></div>
    """), unsafe_allow_html=True)
    # ⛔ 중앙의 '알림 끄기' 버튼은 더 이상 만들지 않음(사이드바에서만 제어)

# ---------------- 뉴스 ----------------
news_html = []
for tag, title, desc in news_items:
    news_html.append(f"""
      <div class="news-item">
        <div class="tag">{tag}</div>
        <div class="news-title">{title}</div>
        <div class="news-desc">{desc}</div>
      </div>
    """)
st.markdown(H(f"""
<div class="phone-wrap"><div class="phone"><div class="card news-card">
  {''.join(news_html)}
</div></div></div>
"""), unsafe_allow_html=True)

# ---------------- 바로가기 ----------------
quick_html = []
for icon, text in quick_actions:
    quick_html.append(f"""
      <div class="q-item">
        <div class="q-left"><div class="q-icon">{icon}</div><div class="q-text">{text}</div></div>
        <div class="chev">›</div>
      </div>
    """)
st.markdown(H(f"""
<div class="phone-wrap"><div class="phone"><div class="card">
  <div class="section-title">퇴직연금서비스 바로가기</div>
  <div class="quick-list">{''.join(quick_html)}</div>
</div></div></div>
"""), unsafe_allow_html=True)
