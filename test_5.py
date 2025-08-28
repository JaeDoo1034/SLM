# app.py
import time
import random
from datetime import datetime
import streamlit as st
import graphviz

# ===== (선택) 실제 구현 모듈 자동 사용: 없으면 시뮬레이션 =====
HAVE_REAL = False
try:
    # 사용자가 제공한 패키지 구조에 맞춰 import 시도
    from function.function import ETF_DB, Customer, Task_collect, VectorDB, Test
    HAVE_REAL = True
except Exception:
    HAVE_REAL = False


# ========================= 기본 상태/헬퍼 =========================
STEPS = [
    ("verify",   "고객 정보 확인", "고객/보유종목/투자성향 로딩"),
    ("crawl",    "뉴스 수집",     "보유종목·키워드 뉴스 크롤/요약"),
    ("vectordb", "VectorDB저장",  "요약/메타데이터 임베딩 & 저장"),
    ("render",   "화면 표출",     "대시보드/알림 템플릿 생성"),
    ("report",   "리포트",        "결과 요약/보고서"),
]

DEPEND = {
    "verify": None,
    "crawl": "verify",
    "vectordb": "crawl",
    "render": "vectordb",
    "report": "render",
}

def status_icon(state: str) -> str:
    return {
        "waiting": "⚪️",
        "running": "⏳",
        "done":    "✅",
        "error":   "❌",
    }.get(state, "⚪️")

def status_color(state: str) -> str:
    # Graphviz fillcolor
    return {
        "waiting": "white",
        "running": "gold",
        "done":    "lightgreen",
        "error":   "mistyrose",
    }.get(state, "white")

def init_state():
    # 상태
    if "status" not in st.session_state or not isinstance(st.session_state.status, dict):
        st.session_state.status = {k: "waiting" for k, *_ in STEPS}
    # 로그 (dict[str, list[str]])
    if "logs" not in st.session_state or not isinstance(st.session_state.logs, dict):
        st.session_state.logs = {k: [] for k, *_ in STEPS}
    # 아티팩트 (예: 기사 수/문서 수 등 집계)
    if "artifacts" not in st.session_state or not isinstance(st.session_state.artifacts, dict):
        st.session_state.artifacts = {"tickers": [], "article_count": 0, "vector_count": 0}

    # 사이드바 설정 기본값
    st.session_state.setdefault("cfg_pages", 5)
    st.session_state.setdefault("cfg_embed", "openai")    # openai | bge
    st.session_state.setdefault("cfg_reranker", "Yes")    # Yes | No
    st.session_state.setdefault("cfg_rerank_target", "seg")  # seg | tot
    st.session_state.setdefault("cfg_rerank_topk", 30)

def set_status(step: str, state: str):
    st.session_state.status[step] = state

def can_run(step: str) -> bool:
    dep = DEPEND.get(step)
    if dep is None:
        return True
    return st.session_state.status.get(dep) == "done"

def add_log(step: str, msg: str):
    st.session_state.logs.setdefault(step, [])
    stamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs[step].append(f"{stamp} · {msg}")

def reset_all():
    st.session_state.status = {k: "waiting" for k, *_ in STEPS}
    st.session_state.logs = {k: [] for k, *_ in STEPS}
    st.session_state.artifacts = {"tickers": [], "article_count": 0, "vector_count": 0}

# ========================= 작업(시뮬레이션/실제) =========================
def run_verify():
    """고객/보유종목 로딩"""
    set_status("verify", "running"); add_log("verify", "실행 시작")
    time.sleep(0.3)

    try:
        if HAVE_REAL:
            etf = ETF_DB(path="DB/ETF.db")
            df = etf.Show_etf_top5()

            cus = Customer(cus_path="DB/Customer.db")
            cus_df = cus.get_cus_df(df)
            tickers = cus.get_ticker_lst(cus_df)
            cus.save_cus_df(cus_df)
        else:
            # 시뮬레이션
            tickers = ["우리금융지주", "삼성전자", "현대모비스", "카카오뱅크", "메리츠금융지주", "SK하이닉스"]
            time.sleep(0.5)

        st.session_state.artifacts["tickers"] = tickers
        add_log("verify", f"보유 종목 로딩: {tickers}")
        set_status("verify", "done")
    except Exception as e:
        add_log("verify", f"오류: {e}")
        set_status("verify", "error")

def run_crawl():
    """뉴스 수집"""
    set_status("crawl", "running"); add_log("crawl", "실행 시작")
    tickers = st.session_state.artifacts.get("tickers", [])
    pages = int(st.session_state.cfg_pages)

    try:
        total = 0
        if HAVE_REAL:
            col = Task_collect()
            for t in tickers:
                add_log("crawl", f"크롤링: {t} (pages={pages})")
                col.extract_news_data(t, pages)
            df = col.save_news_df()
            total = len(df)
        else:
            # 시뮬레이션
            for t in tickers:
                add_log("crawl", f"크롤링: {t} (pages={pages})")
                time.sleep(0.2)
                total += random.randint(5, 20)

        st.session_state.artifacts["article_count"] = total
        add_log("crawl", f"수집 기사 수: {total}")
        set_status("crawl", "done")
    except Exception as e:
        add_log("crawl", f"오류: {e}")
        set_status("crawl", "error")

def run_vectordb():
    """임베딩 후 VectorDB 저장"""
    set_status("vectordb", "running"); add_log("vectordb", "실행 시작")
    embed_kind = st.session_state.cfg_embed
    tickers = st.session_state.artifacts.get("tickers", [])

    try:
        vector_count = 0
        if HAVE_REAL:
            # 실제: 뉴스 DB에서 읽어서 저장
            df = Task_collect.save_news_df()
            vec = VectorDB()
            vec.save_vectordb(target_list=tickers, df=df, kind=embed_kind)
            # 카운트 추정/조회
            vector_count = len(df)
        else:
            # 시뮬레이션
            time.sleep(0.5)
            vector_count = st.session_state.artifacts.get("article_count", 0) * 3

        st.session_state.artifacts["vector_count"] = vector_count
        add_log("vectordb", f"VectorDB 저장 문서 수: {vector_count} (embed={embed_kind})")
        set_status("vectordb", "done")
    except Exception as e:
        add_log("vectordb", f"오류: {e}")
        set_status("vectordb", "error")

def run_render():
    """화면/요약 생성"""
    set_status("render", "running"); add_log("render", "실행 시작")
    try:
        use_rr = st.session_state.cfg_reranker
        target = st.session_state.cfg_rerank_target
        topk = int(st.session_state.cfg_rerank_topk)
        tickers = st.session_state.artifacts.get("tickers", [])

        if HAVE_REAL and tickers:
            cross = Test()
            # 간단 샘플 실행
            _ = cross.eval_test(ticker_list=tickers, kind=st.session_state.cfg_embed,
                                state=("Yes" if use_rr == "Yes" else "No"),
                                total=target)
        else:
            time.sleep(0.5)

        add_log("render", f"렌더링/요약 완료 (Reranker={use_rr}, 대상={target}, TopN={topk})")
        set_status("render", "done")
    except Exception as e:
        add_log("render", f"오류: {e}")
        set_status("render", "error")

def run_report():
    """리포트 요약"""
    set_status("report", "running"); add_log("report", "실행 시작")
    try:
        # 시뮬레이션
        time.sleep(0.3)
        add_log("report", "보고서 생성/저장 완료")
        set_status("report", "done")
    except Exception as e:
        add_log("report", f"오류: {e}")
        set_status("report", "error")


# ========================= UI =========================
st.set_page_config(page_title="단계별 파이프라인 실행기", layout="wide")
init_state()

# ---- 헤더/컨트롤 라인
st.markdown("## 🧭 단계별 파이프라인 실행기")
st.caption("상단 컨트롤은 항상 고정. 각 단계는 버튼 클릭 또는 순차 실행으로 동작합니다.")

ctrl1, ctrl2 = st.columns([1, 1])
with ctrl1:
    if st.button("▶️ 순차 실행 (처음부터)", use_container_width=True):
        # 순차 실행
        for k, *_ in STEPS:
            if not can_run(k):
                add_log(k, "선행 단계가 완료되지 않아 대기")
                continue
            if k == "verify":
                run_verify()
            elif k == "crawl":
                run_crawl()
            elif k == "vectordb":
                run_vectordb()
            elif k == "render":
                run_render()
            elif k == "report":
                run_report()
        st.toast("순차 실행 완료")

with ctrl2:
    if st.button("🧼 상태 초기화", use_container_width=True):
        reset_all()
        st.toast("상태/로그 초기화 완료")

st.divider()

# ---- 단계 버튼 행
cols = st.columns(len(STEPS))
for i, (key, label, desc) in enumerate(STEPS):
    with cols[i]:
        disabled = not can_run(key)
        icon = status_icon(st.session_state.status[key])
        if st.button(f"{icon} {label}", key=f"btn_{key}", disabled=disabled, use_container_width=True):
            if key == "verify":
                run_verify()
            elif key == "crawl":
                run_crawl()
            elif key == "vectordb":
                run_vectordb()
            elif key == "render":
                run_render()
            elif key == "report":
                run_report()

    st.caption(desc)

# ---- 큰 Graphviz 다이어그램 (크게 / 화면폭 꽉 차게)
dot = graphviz.Digraph(format="svg")
dot.attr(
    rankdir="LR",
    nodesep="1.1",   # 노드 간격
    ranksep="1.15",  # 레벨 간격
    pad="0.2",
    dpi="160"
)
dot.node_attr.update(
    shape="box",
    style="filled,rounded",
    fontsize="20",
    width="3.2",
    height="1.3",
    margin="0.15,0.10",
    penwidth="2"
)
dot.edge_attr.update(
    penwidth="2",
    arrowsize="0.9"
)

for key, label, _ in STEPS:
    dot.node(key, label, fillcolor=status_color(st.session_state.status[key]))

dot.edge("verify", "crawl")
dot.edge("crawl", "vectordb")
dot.edge("vectordb", "render")
dot.edge("render", "report")

st.graphviz_chart(dot, use_container_width=True)

# ---- 요약/메타 정보 표시
art = st.session_state.artifacts
meta = st.container()
with meta:
    st.subheader("📊 단계별 결과/로그")
    with st.expander(f"보유 종목: {len(art.get('tickers', []))} / 저장된 기사 수: {art.get('article_count', 0)}", expanded=True):
        pass

    # 단계별 로그
    for key, label, _ in STEPS:
        with st.expander(label, expanded=False):
            for line in st.session_state.logs.get(key, []):
                st.markdown(f"- {line}")

# ---- 사이드바: 설정
with st.sidebar:
    st.header("⚙️ 실행 설정")
    st.session_state.cfg_pages = st.number_input("뉴스 검색 페이지 수(페이지당)", 1, 30, st.session_state.cfg_pages)
    st.session_state.cfg_embed = st.selectbox("VectorDB 임베딩", ["openai", "bge"], index=0 if st.session_state.cfg_embed=="openai" else 1)
    st.session_state.cfg_reranker = st.selectbox("Re-ranker 사용", ["Yes", "No"], index=0 if st.session_state.cfg_reranker=="Yes" else 1)
    st.session_state.cfg_rerank_target = st.selectbox("Re-ranker 비교 대상", ["seg", "tot"], index=0 if st.session_state.cfg_rerank_target=="seg" else 1)
    st.session_state.cfg_rerank_topk = st.number_input("Re-ranker Top-N (k)", 5, 100, st.session_state.cfg_rerank_topk, step=5)
    st.caption("※ OpenAI 키 등은 환경변수(.env)에서 읽습니다(실제 모드일 때).")
