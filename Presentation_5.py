import streamlit as st
from textwrap import dedent
import re

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="MY 퇴직연금관리",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------------- Helpers ----------------
def H(s: str) -> str:
    s = dedent(s)
    s = re.sub(r"\n[ \t]+", "\n", s)
    return s.strip()

# ▶ 모달 한 번만 열기 트리거(리스트 모달)
def trigger_news_modal():
    """뉴스(리스트) 모달을 이번 렌더에 한 번만 열도록 상태 세팅 후 리렌더."""
    st.session_state.open_news_modal_once = True
    st.rerun()

# ▶ 모달 한 번만 열기 트리거(요약 모달)
def trigger_alert_modal():
    """뉴스 알림(요약) 모달을 이번 렌더에 한 번만 열도록 상태 세팅 후 리렌더."""
    st.session_state.open_news_alert_modal_once = True
    st.rerun()

# ---------------- State ----------------
if "notify_opt_in" not in st.session_state:
    st.session_state.notify_opt_in = False
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "rise"

# ▶ 모달: '원샷' 트리거(페이지 진입 자동 오픈 방지)
if "open_news_modal_once" not in st.session_state:
    st.session_state.open_news_modal_once = False  # 리스트 모달
if "open_news_alert_modal_once" not in st.session_state:
    st.session_state.open_news_alert_modal_once = False  # 요약 모달

# ▶ 마크다운 링크 클릭 감지용 쿼리파라미터 처리(신/구 API 호환)
def _get_qp():
    try:
        return dict(st.query_params)  # Streamlit >= 1.30
    except Exception:
        return st.experimental_get_query_params()  # legacy

def _clear_qp_key(k: str):
    try:
        if k in st.query_params:
            del st.query_params[k]
    except Exception:
        qp = _get_qp()
        qp.pop(k, None)
        st.experimental_set_query_params(**qp)

qp = _get_qp()
val = qp.get("open_news")
val = (val[0] if isinstance(val, list) else val)
if str(val) == "1":
    st.session_state.open_news_modal_once = True
    _clear_qp_key("open_news")  # 한 번만 열리도록 즉시 제거

# 이 렌더에서만 오픈 여부 확정
OPEN_NEWS_MODAL_NOW = st.session_state.pop("open_news_modal_once", False)            # 리스트
OPEN_NEWS_ALERT_MODAL_NOW = st.session_state.pop("open_news_alert_modal_once", False)  # 요약

# 모달 카테고리 탭
if "news_active_tab" not in st.session_state:
    st.session_state.news_active_tab = "전체"

# ---------------- Data ----------------
EXTRA_NEWS_LINKS = [
    ("시황 챗봇", "https://a3djxcmkxgbebrq3azihjk.streamlit.app/#72379101"),
    ("종합 리포트 보기", "https://afhkvib6atlz5f9pnm9t6s.streamlit.app/"),
]

# 헤더로 올릴 1개 / 하단에 남길 나머지
HEADER_LINK = EXTRA_NEWS_LINKS[0] if EXTRA_NEWS_LINKS else None
REMAINING_LINKS = EXTRA_NEWS_LINKS[1:] if len(EXTRA_NEWS_LINKS) > 1 else []

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
    {
        "id":"rise",
        "ticker":"우리금융지주",
        "label":"RISE 코리아금융고배당",
        "components": ["우리금융지주","삼성화재","삼성생명","카카오뱅크","메리츠금융지주"],
        "content": """
✅ 주요 요약

- **국내 4대 금융지주, 평균 급여 사상 첫 반기 1억 원 돌파**<br>
   KB금융이 1억1200만원으로 가장 높은 평균 급여를 기록했으며, 금융지주들의 상반기 순이익이 10조3254억원을 넘어서며 급여 상승에 기여함.

- **금융지주 주가 하락, 정부의 세금 및 과징금 부담 증가**<br>
   교육세 인상과 과징금 부과 등으로 인해 금융지주 주가가 하락하고 있으며, 정부의 압박이 주가에 부정적 영향을 미치고 있음.

- **외국인 투자자, 정부의 금융권 압박에 우려**<br>
   외국인 지분율이 높은 금융지주사들이 정부의 압박으로 인해 주가가 하락하고 있으며, 외국인 투자자들의 우려가 증가하고 있음.
"""
    },
    {
        "id":"kr_div",
        "ticker":"현대차",
        "label":"KODEX 자율주행액티브",
        "components": ["현대모비스","현대오토에버","SK하이닉스","현대글로비스","현대차"],
        "content": """
✅ 주요 요약

- **현대차그룹, 미국에 50억 달러 추가 투자 발표**<br>
  현대차그룹은 미국 루이지애나에 270만 톤 규모의 전기로 제철소를 건설하고, 연간 3만 대 생산 가능한 로봇 공장을 신설하는 등 4년간 260억 달러를 투자하여 미래산업 경쟁력을 강화할 계획이다. 이번 투자는 제철, 자동차, 로봇 등 다양한 분야에 걸쳐 있으며, 미국 내 철강-부품-완성차로 이어지는 밸류 체인을 구축하여 경쟁력을 높일 예정이다.

- **현대차 노조, 파업 찬반 투표에서 90% 이상 찬성**<br>
  현대차 노조는 임금 인상과 근로조건 개선을 요구하며 파업을 준비 중이며, 중앙노동위원회의 조정 중지 결정으로 합법적인 파업권을 확보했다. 노조는 기본급 인상, 성과급 지급, 근로시간 단축 등을 요구하고 있다.

- **현대차, 미국 관세 영향으로 상반기 영업이익 감소**<br>
  현대차는 미국의 25% 관세로 인해 상반기 영업이익이 전년 대비 7.7% 감소했으며, 하반기에는 관세 영향이 더 커질 것으로 예상된다. 이는 미국 내 자동차 생산능력 확대와 전기차, 하이브리드 등 다양한 차종 라인업을 통해 대응할 계획이다.

- **현대차그룹, 청정에너지 장관 회의에서 수소 생태계 구축 강조**<br>
  현대차그룹은 제16차 청정에너지 장관 회의에 참가해 수소 생태계 구축의 필요성을 강조하며, 국제 협력을 통한 저탄소 산업 전환 촉진을 논의했다. 켄 라미레즈 부사장은 공공과 민간의 협력을 통한 수소 인프라 구축의 중요성을 역설했다.

"""
    },
    {
        "id":"us_div",
        "ticker":"삼성전자",
        "label":"ACE AI반도체포커스",
        "components": ["SK하이닉스","삼성전자","한미반도체","파크시스템스","DB하이텍"],
        "content": """
✅ 주요 요약

- **삼성전자, AI 엑스퍼트 프로그램 신설 및 인재 발굴 강화** <br>
  삼성전자는 AI 분야의 우수 인재를 'AI 엑스퍼트'로 선정하고, 격려금 2000만원과 자격 수당 50만원을 지급하는 프로그램을 도입했다. 선정 기준은 AI 관련 최고 수준 학회 논문 발표, 글로벌 AI 대회 수상, 사내 AI 과제 표창 등이며, 이는 AI 선도 기업으로 도약하기 위한 전략의 일환이다.

- **테슬라와의 대규모 AI 칩 공급 계약 체결**  <br>
  삼성전자는 테슬라와 수조 원대의 AI 칩 공급 계약을 체결하여, 파운드리 사업과 반도체 부문에서 중장기적 성장 동력을 확보할 수 있는 기반을 마련했다. 이는 삼성의 반도체 수요를 안정적으로 견인할 수 있는 실질적 기반으로 평가된다.

- **글로벌 메모리 시장 경쟁 심화와 기술력 개선 필요**  <br>
  SK하이닉스의 시장 점유율 확대에 따라 삼성전자는 메모리 경쟁에서 압박을 받고 있으며, 기술력 개선과 고객 다변화를 추진해야 하는 과제를 안고 있다. 특히, 고대역폭 메모리(HBM) 시장에서의 경쟁이 심화되고 있다.

"""
    },
    {
        "id":"bond_mix",
        "ticker":"LG에너지솔루션",
        "label":"ACE 2차전지&친환경차액티브",
        "components": ["현대모비스","현대차","기아","POSCO홀딩스","LG에너지솔루션"],
        "content": """
✅ 주요 요약

- **2차전지 업종, ESS 수요 증가로 성장 기대**  <br>
  이동근 대표는 2차전지 업종의 성장 가능성을 강조하며, ESS(에너지저장장치) 수요 증가가 전력 수급 균형과 전력망 안정성을 높일 것이라고 진단했습니다. 그는 LG에너지솔루션과 현대차를 유망 종목으로 꼽으며, 각각의 투자 전략을 제시했습니다.

- **전기차 배터리 기술 혁신과 안전성 강화**<br>전고체 배터리의 상용화가 2025~2026년에 본격화될 것으로 예상되며, 이는 전기차 주행거리와 안전성을 획기적으로 개선할 것으로 보입니다. 삼성SDI는 전고체 배터리 양산을 2027년 목표로 하고 있습니다.

- **시장 동향 및 기타 기업 정보**  <br>
  최근 2차전지 업종의 반등은 ESS 수요 증가와 관련이 있으며, LG에너지솔루션과 삼성SDI는 이 시장에서의 입지를 강화하고 있습니다. 또한, 전고체 배터리 기술의 발전이 가속화되면서 관련 기업들의 기술 경쟁이 심화되고 있습니다.

- **다양한 기업의 시장 전략**  <br>
  LG에너지솔루션, 삼성SDI, SK온 등 국내 배터리 3사는 전기차 배터리 시장에서의 입지를 강화하기 위해 연구개발(R&D) 투자를 늘리고 있으며, 각 사의 차입금 증가와 함께 미래 기술 개발을 위한 노력을 지속하고 있습니다. 

"""
    }
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

# 모달 더미 피드
RESEARCH_FEED = [
    {"cat":"우리금융지주",  "title":"우리금융, APEC 정상회의 공식 후원", "date":"2025.08.28"},
    {"cat":"우리금융지주",  "title":"정부 전방위 압박에…은행株, 일제히 내리막", "date":"2025.08.25"},
    {"cat":"우리금융지주",  "title":"금융지주 비이자이익도 '은행 쏠림' 뚜렷", "date":"2025.08.20"},
    {"cat":"우리금융지주",  "title":"금융권 연봉 '2억 시대' 여나…삼성전자·현대차는 절반도 안 돼", "date":"2025.08.15"},
    {"cat" : "삼성화재",  "title":"삼성화재, 유방암 환자의 치료 시작부터 암 이후의 삶까지 고충 살펴봐", "date":"2025.08.29"},
    {"cat":"삼성화재",   "title":"국내 주요 보험사 기후리스크 관리 수준, 글로벌 기준과 격차", "date":"2025.08.27"},
    {"cat":"삼성화재",   "title":"삼성화재 해외여행보험, '해외 2시간 항공지연 특약' 출시",            "date":"2025.08.27"},
    {"cat":"삼성화재",   "title":"취업문 활짝 삼성 19개 계열사, 하반기 신입 채용 시작",      "date":"2025.08.27"},
    {"cat":"삼성생명",   "title":"[토요칼럼] 중대재해, 처벌만이 능사 아닌 이유",            "date":"2025.08.29"},
    {"cat":"삼성생명",   "title":"삼성생명, 화성 시니어 주민을 위한 ‘건강 세미나’ 개최",            "date":"2025.08.29"},
    {"cat":"삼성생명",   "title":"'인재 제일' 삼성, 하반기 공채 스타트",            "date":"2025.08.26"},
    {"cat":"삼성생명",   "title":"소비자 보호 내재화…디지털 활용 돋보여",            "date":"2025.08.26"},
    {"cat":"카카오뱅크", "title":"'사법 리스크' 김범수 운명은?…카카오 '초긴장' [종합]",                 "date":"2025.08.29"},
    {"cat":"카카오뱅크", "title":"연 4%대 업계 최저 금리로 저렴하게! 간편하게 모바일로도 OK!",                 "date":"2025.08.27"},
    {"cat":"카카오뱅크", "title":"대출 줄 곳 없네…국공채 투자 내몰린 인뱅",                 "date":"2025.08.27"},
    {"cat":"카카오뱅크", "title":"은행마다 다른 혜택…'모임카드' 어떤게 좋을까",                 "date":"2025.08.24"},
    {"cat":"메리츠금융지주", "title":"'메리츠금융지주' 52주 신고가 경신, 확신의 Top Pick - 신한투자증권, 매수",                 "date":"2025.08.24"},
    {"cat":"메리츠금융지주", "title":"메리츠금융, 주주환원 강화에 장중 5%대 급등",                 "date":"2025.08.21"},
    {"cat":"메리츠금융지주", "title":"메리츠금융, 호실적·주주환원책 영향에 장 초반 7%대 급등",                 "date":"2025.08.14"},
]

# ---------------- CSS ----------------
CSS = H("""
html, body, .block-container { background:#f6f8fb !important; }
section.main > div { padding-top: 8px; }

/* 상단 헤더 */
.topbar-wrap { display:flex; justify-content:center; margin:10px auto 14px; max-width:520px; padding:0 8px; }
topbar{}

/* (중략) —— 아래 CSS는 기존 그대로 ————————————————————————————— */
.topbar {
  width:100%; height:64px; position:relative; display:flex; align-items:center; justify-content:center;
  background:#fff; border:1px solid #edf1f7; border-radius:22px; box-shadow:0 8px 20px rgba(23,30,60,0.08), inset 0 -1px 0 #f0f3f8;
}
.topbar-title { font-weight:900; font-size:20px; color:#1b233d; }
.topbar-back { position:absolute; left:10px; top:50%; transform:translateY(-50%);
  width:38px; height:38px; border-radius:999px; display:grid; place-items:center;
  border:1px solid #e6ebf3; color:#445; background:#fff; box-shadow:0 4px 10px rgba(23,30,60,0.06); font-size:18px; }

.phone-wrap{ display:flex; justify-content:center; margin:0 auto 24px; max-width:520px; }
.phone{ width:100%; }
.card{ background:#fff; border:1px solid #e7ebf3; border-radius:18px; padding:16px; box-shadow:0 6px 16px rgba(23,30,60,0.06); margin:4px 4px; }
.section-title{ font-size:16px; font-weight:900; color:#1b233d; margin-bottom:10px; }
.eval-amount{ font-size:34px; font-weight:900; color:#0f1a31; margin-top:2px; }
.row{ display:flex; align-items:center; justify-content:space-between; gap:10px; margin:10px 0 0; }

.alloc-bar{ width:100%; height:16px; background:#f0f3f8; border-radius:999px; overflow:hidden; box-shadow: inset 0 1px 2px rgba(15,23,42,0.06); }
.alloc-chunk{ height:100%; float:left; }
.legend{ display:flex; flex-direction:column; gap:10px; margin-top:10px; }
.actions{ display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:12px; }
.btn{ display:block; text-align:center; padding:12px 12px; border-radius:12px; border:1px solid #e7ebf3; font-weight:900; color:#1b233d; background:#fff; }

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

.summary-wrap{ max-width:520px; margin:0 auto; }
.summary-card{ background:#fff; border:1px solid #e7ebf3; border-radius:18px; box-shadow:0 6px 16px rgba(23,30,60,.06); padding:18px; }
.summary-title{ font-size:22px; font-weight:900; color:#1765f0; margin-bottom:12px; text-align:center; }
.summary-panel{ background:#edf5ff; border:1px solid #d9e9ff; border-radius:16px; padding:16px 18px; }
.summary-badge{ display:inline-block; background:#e7f1ff; color:#0b62e6; font-weight:900; font-size:14px; border-radius:999px; padding:6px 10px; margin-bottom:8px; }
.summary-quote{ margin:10px 0 0; padding:12px 14px; background:#f4f8ff; border-left:4px solid #bcd9ff; color:#2b3a55; font-size:16px; border-radius:10px; }

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

.summary-quote{
  margin:10px 0 0;
  padding:12px 14px;
  background:#f4f8ff;
  border-left:4px solid #bcd9ff;
  color:#2b3a55;
  font-size:16px;
  border-radius:10px;
  text-align:left !important;
  line-height:1.8;
}
.summary-quote p,
.summary-quote li,
.summary-quote div{ text-align:left !important; }

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

.modal-news-item{ padding:16px 4px; border-bottom:1px solid #eef2f7; }
.modal-news-title{ font-weight:900; color:#0f1a31; }
.modal-news-meta{ color:#5b6785; font-size:14px; margin-top:4px; }
.badge-new{ display:inline-block; margin-left:6px; padding:2px 6px; border-radius:999px; font-weight:900; font-size:11px; background:#ff5a65; color:#fff; }

div[data-testid="stVerticalBlock"]:has(.summary-cta-scope){
  max-width:520px; 
  margin:-6px auto 8px !important;
  text-align:center;
}
div[data-testid="stVerticalBlock"]:has(.summary-cta-scope) div[data-testid="stButton"]{
  display:flex; justify-content:center;
}
div[data-testid="stVerticalBlock"]:has(.summary-cta-scope) div[data-testid="stButton"] > button{
  width:100% !important; height:44px !important;
  border-radius:12px !important;
  background:#eef5ff !important; 
  border:1px solid #d7e6ff !important; 
  color:#0b62e6 !important;
  font-weight:900 !important;
  box-shadow: inset 0 -2px 0 rgba(11,98,230,.06) !important;
}

.summary-tags{ display:flex; gap:12px; flex-wrap:wrap; justify-content:flex-start; margin:6px 0 8px; }
.summary-tag{
  display:inline-block; background:#e7f1ff; border:1px solid #d9e9ff; color:#0b62e6;
  font-weight:900; font-size:12px; padding:6px 10px; border-radius:999px; box-shadow: inset 0 -1px 0 rgba(11,98,230,.06);
}
div[data-testid="stVerticalBlock"]:has(.summary-cta-scope) a.link-cta{
  display:block; width:100%; height:44px; line-height:44px; border-radius:12px; text-decoration:none; text-align:center;
  background:#eef5ff; border:1px solid #d7e6ff; color:#0b62e6; font-weight:900; box-shadow: inset 0 -2px 0 rgba(11,98,230,.06); margin-top:8px;
}
""")
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ---------------- Sidebar ----------------
with st.sidebar:
    with st.container():
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

        # ▶ 사이드바 '뉴스 알림' → 요약 모달 전용 트리거
        if st.button("뉴스 알림", key="sb_open_news_alert_modal", use_container_width=True):
            trigger_alert_modal()

# ---------------- Top bar ----------------
st.markdown(H(f"""
<div class="topbar-wrap"><div class="topbar">
  <div class="topbar-back">‹</div>
  <div class="topbar-title">MY 퇴직연금관리</div>
  {f'<a class="topbar-news" href="{HEADER_LINK[1]}" target="_blank" rel="noopener noreferrer">{HEADER_LINK[0]}</a>' if HEADER_LINK else ''}
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
    # 칩 탭바
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

    # 선택된 탭 내용 + 카드 내부 하단에 '뉴스 보기'
    tab = next((x for x in TABS if x["id"] == st.session_state.active_tab), TABS[0])
    chips = "".join(f'<span class="summary-tag">{c}</span>' for c in tab.get("components", []))

    st.markdown(H(f"""
    <div class="summary-wrap"><div class="summary-card">
      <div class="summary-title">8월 29일 오늘의 요약</div>
      <div class="summary-panel">
        {f'<div class="summary-tags">{chips}</div>' if chips else ''}
        <div class="summary-quote">{tab["content"]}</div>
      </div>
    </div></div>
    """), unsafe_allow_html=True)

    with st.container():
        st.markdown('<span class="summary-cta-scope"></span>', unsafe_allow_html=True)
        if st.button("뉴스 보기", key="open_news_modal"):
            st.session_state.open_news_modal_once = True  # 리스트 모달
            st.rerun()
        for label, url in REMAINING_LINKS:
            st.markdown(
                f'<a class="link-cta" href="{url}" target="_blank" rel="noopener noreferrer">{label}</a>',
                unsafe_allow_html=True
            )

# ---------------- 뉴스 모달 (기사 리스트) ----------------
def open_news_modal():
    if not hasattr(st, "dialog"):
        st.warning("현재 Streamlit 버전에서 모달을 지원하지 않습니다.")
        return

    @st.dialog("종목 뉴스 기사")
    def _news_dlg():
        cats = ["전체","우리금융지주","삼성화재","삼성생명","카카오뱅크","메리츠금융지주"]
        with st.container():
            st.markdown('<span class="chipbar-scope"></span>', unsafe_allow_html=True)
            st.markdown('기준일자 : 2025.08.29')
            cols = st.columns(len(cats), gap="small")
            for i, c in enumerate(cats):
                with cols[i]:
                    if st.session_state.news_active_tab == c:
                        st.markdown(f'<span class="chip">{c + " +5%"}</span>', unsafe_allow_html=True)
                    else:
                        if st.button(c, key=f"news_tab_{c}"):
                            st.session_state.news_active_tab = c
                            st.session_state.open_news_modal_once = True
                            st.rerun()

        selected = st.session_state.news_active_tab
        items = [x for x in RESEARCH_FEED if selected == "전체" or x["cat"] == selected]
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        for it in items:
            st.markdown(H(f"""
            <div class="modal-news-item">
              <div class="modal-news-title">{it['title']}</div>
              <div class="modal-news-meta">{it['cat']} | {it['date']} <span class="badge-new">N</span></div>
            </div>
            """), unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("닫기", key="news_close_btn"):
            st.rerun()

    _news_dlg()

# ---------------- 뉴스 알림 모달 (요약) ----------------
def open_news_alert_modal():
    if not hasattr(st, "dialog"):
        st.warning("현재 Streamlit 버전에서 모달을 지원하지 않습니다.")
        return

    @st.dialog("종목기사")
    def _alert_dlg():
        cats = ["우리금융지주"]
        with st.container():
            st.markdown('<span class="chipbar-scope"></span>', unsafe_allow_html=True)
            st.markdown('기준일자 : 2025.08.29')
            cols = st.columns(len(cats), gap="small")
            for i, c in enumerate(cats):
                with cols[i]:
                    if st.session_state.news_active_tab == c:
                        st.markdown(f'<span class="chip">{c + " +5%"}</span>', unsafe_allow_html=True)
                    else:
                        if st.button(c, key=f"alert_tab_{c}"):
                            st.session_state.news_active_tab = c
                            st.session_state.open_news_alert_modal_once = True
                            st.rerun()

        # 요약 박스 (이미지 #3 스타일)
        summary_html = H("""
        <div class="summary-panel" style="margin-top:12px;">
          <div style="display:flex; align-items:center; gap:8px; font-weight:900; color:#1b2a44;">
            <span style="font-size:18px;">✅</span><span>주요 요약</span>
          </div>
          <ul style="margin:10px 0 0; padding-left:20px; line-height:1.9; color:#2b3a55;">
            <li><b>외국인 투자자, 우리금융지주 주식 대량 순매수</b><br>
                최근 한 달 간 외국인은 우리금융지주를 490.4만 주 순매수(비중 52.6%).</li>
            <li><b>우리금융지주, 2분기 순이익 감소 예상</b><br>
                판관비 증가 영향으로 전년 대비 -8.6% 전망.</li>
            <li><b>4대 금융지주, 비이자이익 증가</b><br>
                환율 안정·수수료 확대로 2분기 순이익 +5.3%.</li>
          </ul>
          <div style="margin-top:10px; color:#6b778c;">🔑 키워드: 외국인, 우리금융지주, 순매수, 비이자이익.</div>
        </div>
        """)
        st.markdown(summary_html, unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("닫기", key="alert_close_btn"):
            st.rerun()

    _alert_dlg()

# ▶ 이번 렌더에서만 해당 모달 오픈
if OPEN_NEWS_MODAL_NOW:
    open_news_modal()
if OPEN_NEWS_ALERT_MODAL_NOW:
    open_news_alert_modal()

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
