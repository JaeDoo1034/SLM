import streamlit as st

st.set_page_config(
    page_title="나의 퇴직연금관리",
    page_icon="📰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ===== Router (page state) =====
if "page" not in st.session_state:
    st.session_state.page = "index"   # index, article

def go(page: str):
    st.session_state.page = page
    st.rerun()

# ===== CSS =====
CSS = """
/* 전체 */
html, body, .block-container { background: #f6f8fb !important; }
section.main > div { padding-top: 10px; }
/* 사이드바/헤더 숨김 */
[data-testid="stSidebar"], header[tabindex="0"] { display: none !important; }

/* 폰 프레임 */
.phone-wrap { display:flex; justify-content:center; margin:20px auto 40px; max-width:560px; }
.phone {
  width:100%; background:#fff; border-radius:26px; overflow:hidden;
  border:1px solid #e7ebf3; box-shadow:0 10px 25px rgba(23,30,60,0.08);
}
.phone-header {
  position:relative; padding:18px 24px;
  background:linear-gradient(180deg,#ffffff 0%,#fafcff 100%);
  border-bottom:1px solid #eef2f7;
}
.phone-title { text-align:center; font-weight:800; font-size:22px; color:#1f2a44; }
.header-close {
  position:absolute; right:12px; top:10px; width:36px; height:36px; border-radius:999px;
  background:#fff; border:1px solid #e7ebf3; box-shadow:0 2px 8px rgba(23,30,60,0.06);
  display:grid; place-items:center; font-size:20px; color:#4b5568;
}
.phone-body { padding:16px; }

/* 카드 공통 */
.card {
  background:#fff; border:1px solid #e7ebf3; border-radius:20px;
  padding:18px; box-shadow:0 6px 18px rgba(23,30,60,0.06); margin:14px 8px;
}
.sec-title { font-size:18px; font-weight:800; color:#1765f0; margin:0 0 10px; }

/* 요약 카드 */
.summary-top {
  position:relative; background:#f4f9ff; border:1px solid #e1efff; border-radius:16px; padding:14px;
}
.summary-bg {
  position:absolute; inset:0;
  background: radial-gradient(80% 60% at 80% 20%, rgba(22,160,255,0.12), rgba(22,160,255,0) 60%),
              radial-gradient(70% 60% at 20% 80%, rgba(22,160,255,0.08), rgba(22,160,255,0) 60%);
  border-radius:16px; pointer-events:none;
}
.badge { display:inline-block; padding:3px 8px; border-radius:999px; background:#e7f1ff; color:#0b62e6; font-weight:800; font-size:13px; }
.summary-text { font-size:16px; font-weight:700; color:#1f2a44; line-height:1.5; margin-top:8px; }

/* 하이퍼링크처럼 보이는 버튼 */
.link-btn > button {
  background: transparent !important;
  border: none !important;
  color: #0b62e6 !important;
  text-decoration: underline !important;
  font-weight: 700 !important;
  padding: 0 !important;
  box-shadow: none !important;
  min-height: auto !important;
}
.link-btn { margin-top: 8px; }

/* 마켓 */
.market { margin-top:10px; border-top:1px solid #e7ebf3; padding-top:10px; }
.mrow { display:grid; grid-template-columns:1fr auto auto; gap:10px; font-size:15px; padding:5px 0; }
.mname { color:#23304d; font-weight:600; }
.mval,.mchg { font-weight:700; }
.negative { color:#e03131; }
.positive { color:#0ca678; }

/* 평가금액 */
.amount { font-size:38px; font-weight:900; color:#131b2f; letter-spacing:0.5px; }
.unit { font-size:18px; font-weight:800; color:#3f4b6a; margin-left:6px; }

/* 수익률 */
.return-grid { display:grid; grid-template-columns:auto 1fr; gap:10px 24px; align-items:center; }
.label-col span, .value-col span { display:block; padding:6px 0; font-size:16px; }
.label-col span { color:#1765f0; font-weight:800; }
.value-col span { color:#1f2a44; font-weight:700; }

/* 기사 화면 */
.article-title { font-size:28px; font-weight:900; color:#0f1a31; margin:6px 0 4px; }
.article-meta { color:#5b6785; font-weight:700; margin-bottom:12px; }
.article-p { color:#26324d; font-size:17px; line-height:1.85; margin:12px 0; }
.share-btn {
  display:block; width:100%; padding:14px 18px; text-align:center;
  background:linear-gradient(180deg,#1d68ff 0%, #0052f5 100%);
  color:#fff; border-radius:12px; font-weight:900; font-size:18px; border:0;
  box-shadow:0 6px 16px rgba(0,82,245,0.28);
}
.footer-space { height:16px; }
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ===== Sample data =====
summary_date = "7월 21일 오늘의 요약"
ai_summary = "✅ 주요 요약\n\n- **외국인 투자자, 우리금융지주 대량 순매수**\n  - 최근 한 달 동안 외국인은 우리금융지주 주식을 490.4만 주 순매수하며, 특히 최근 3일 연속 29.4만 주를 순매수하여 투자자들의 관심을 끌고 있음.\n\n- **우리금융지주, 고배당 매력 부각**\n  - NH투자증권은 우리금융지주의 하반기 배당 매력이 더욱 돋보일 것이라며 투자의견을 '매수'로 유지하고 목표주가를 29,000원으로 상향 조정함.\n\n- **우리금융지주, 2분기 실적 감소 전망**\n  - 우리금융지주는 동양생명과 ABL생명 인수로 인한 일회성 비용 증가로 2분기 순이익이 8784억 원으로 전년 대비 8.6% 감소할 것으로 예상됨.\n\n- **4대 금융지주, 비이자이익 증가로 일부 실적 개선 기대**\n  - KB금융, 신한금융, 하나금융, 우리금융 등 4대 금융지주의 2분기 실적 전망이 상반된 가운데, 비이자이익 증가로 일부 금융지주는 실적 개선을 기대하고 있음.\n  - 신한금융은 순이익이 1조 4700억 원으로 1.3% 증가할 것으로, 하나금융은 1조 1221억 원으로 7% 이상 증가할 것으로 기대됨.\n\n🔑 **키워드**: 외국인 투자자, 우리금융지주, 고배당, NH투자증권, 2분기 실적, 비이자이익, 순매수, 목표주가, 투자의견."
desc_text = "기금형 퇴직 연금 근로자의 선택권이 확대됩니다. 금리 상승에 원리금보장형 퇴직연금 선호도 높아지고 있습니다."
market_rows = [
    ("코스피", "3,200", "-12.34 (10%)"),
    ("KODEX 200 TR", "1,234", "-12.34 (10%)"),
]
eval_amount = "12,345,678"
principal = "10,000,000 원"
profit = "2,345,678 원"
cum_return = "+ 99%"

# ===== Components =====
def header(title: str, back_to: str | None = None):
    st.markdown('<div class="phone-wrap"><div class="phone">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="phone-header">
      <div class="phone-title">{title}</div>
      <div class="header-close">×</div>
    </div>
    <div class="phone-body">
    """, unsafe_allow_html=True)
    # 닫기(뒤로가기) 버튼
    if back_to is not None:
        cols = st.columns([1,6,1])
        with cols[2]:
            if st.button("닫기", use_container_width=True):
                go(back_to)

def tail():
    st.markdown('<div class="footer-space"></div></div></div>', unsafe_allow_html=True)

def summary_section():
    st.markdown(f"""
    <div class="card">
      <div class="sec-title">{summary_date}</div>

      <div class="summary-top">
        <div class="summary-bg"></div>
        <span class="badge">AI 요약</span>
        <div class="summary-text">{ai_summary}</div>
      </div>
    """, unsafe_allow_html=True)

    # "원문 보기"를 링크처럼 보이는 버튼으로 구현 → 클릭 즉시 article 페이지로
    col = st.container()
    with col:
        if st.button("원문 보기", key="go_article", help="기사 원문 보기", type="secondary"):
            go("article")
    st.markdown("</div>", unsafe_allow_html=True)  # .card 닫기

    # 기사 설명 + 마켓
    st.markdown(f"""
    <div class="card" style="margin-top:10px;">
      <div style="color:#303a53; font-size:15px; line-height:1.6; margin-bottom:10px;">
        {desc_text}
      </div>
      <div class="market">
        {"".join([
          f'<div class="mrow">'
          f'  <div class="mname">{name}</div>'
          f'  <div class="mval negative">{val}</div>'
          f'  <div class="mchg negative">{chg}</div>'
          f'</div>'
          for (name, val, chg) in market_rows
        ])}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 버튼을 링크 스타일로 보이게 CSS 주입 (렌더 후에 적용)
    st.markdown(
        """
        <style>
        /* 방금 만든 "원문 보기" 버튼을 하이퍼링크처럼 보이게 */
        div[data-testid="stButton"][id*="go_article"] > button {
          background: transparent !important;
          border: none !important;
          color: #0b62e6 !important;
          text-decoration: underline !important;
          font-weight: 700 !important;
          padding: 0 !important;
          box-shadow: none !important;
          min-height: auto !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def eval_box():
    st.markdown(f"""
    <div class="card">
      <div class="sec-title" style="color:#3b82f6;">평가금액</div>
      <div class="amount">{eval_amount} <span class="unit">원</span></div>
    </div>
    """, unsafe_allow_html=True)

def return_box():
    st.markdown(f"""
    <div class="card">
      <div class="sec-title" style="color:#3b82f6;">투자수익률 현황</div>
      <div class="return-grid">
        <div class="label-col">
          <span>원금</span>
          <span>누적수익</span>
          <span>누적수익률</span>
        </div>
        <div class="value-col">
          <span>{principal}</span>
          <span>{profit}</span>
          <span class="positive">{cum_return}</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def article_section():
    st.markdown(f"""
    <div class="card">
      <div class="article-title">지난해 퇴직연금 8.4% 수익률… 역대 두번째로 높아</div>
      <div class="article-meta">아시아투데이 / 2025-07-15 10:00</div>
      <div class="article-p">
        최근 금융시장 호조로 국내 퇴직연금 수익률이 크게 상승했다. 금융감독원 월별에 따르면 2024년 말 퇴직연금 연평균 수익률은 8.4%를 기록해 2011년 이후 두번째로 높은 수준에 도달했다.
      </div>
      <div class="article-p">
        금리 상승과 함께 원리금 보장형 상품의 수익률이 개선된 것이 주요 요인으로 분석된다. 특히 채권형 상품이 안정적인 수익을 보이며 기업과 개인의 퇴직연금 가입자 모두에게 긍정적인 영향을 줬다.
      </div>
      <div class="article-p">
        전문가들은 "단기적인 시장 변동성에도 불구하고 연금 투자자들이 장기적 관점에서 안정적인 포트폴리오를 유지하는 것이 중요하다"고 조언했다.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 공유하기
    if st.button("공유하기", use_container_width=True):
        st.toast("공유 기능은 프로토타입에서만 제공됩니다.", icon="ℹ️")

# ===== Pages =====
def render_index():
    header("나의 퇴직연금관리", back_to=None)
    summary_section()
    eval_box()
    return_box()
    tail()

def render_article():
    header("원문 기사", back_to="index")
    article_section()
    tail()

# ===== Router Switch =====
if st.session_state.page == "index":
    render_index()
elif st.session_state.page == "article":
    render_article()
else:
    render_index()
