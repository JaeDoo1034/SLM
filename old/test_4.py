import time
import streamlit as st
import graphviz

# ==== 당신이 제공한 기능 모듈 ====
# function/ 디렉토리와 function.py 경로가 맞는지 확인하세요.
from function.function import (
    ETF_DB, Customer, Task_collect, VectorDB, Test
)

# ---------------------------------------------------------
# 0) 초기화
# ---------------------------------------------------------
STEPS = [
    ("verify",   "고객 정보 확인", "고객/보유종목/투자성향 로딩"),
    ("crawl",    "뉴스 수집",     "보유종목·키워드 뉴스 크롤/요약"),
    ("vectordb", "VectorDB저장",  "요약/메타데이터 임베딩 & 저장"),
    ("render",   "화면 표출",     "대시보드/알림 템플릿 생성"),
]
DEPEND = {
    "verify": None,
    "crawl": "verify",
    "vectordb": "crawl",
    "render": "vectordb",
}

def status_icon(state: str) -> str:
    return {
        "waiting": "⚪️",
        "running": "⏳",
        "done": "✅",
        "error": "❌",
    }.get(state, "⚪️")

def status_color(state: str) -> str:
    return {
        "waiting": "white",
        "running": "lightyellow",
        "done": "lightgreen",
        "error": "mistyrose",
    }.get(state, "white")

def init_state():
    ss = st.session_state
    ss.setdefault("status", {k: "waiting" for k, *_ in STEPS})
    ss.setdefault("logs", [])
    ss.setdefault("tickers", [])
    ss.setdefault("news_df_len", 0)
    ss.setdefault("summary_df", None)
    # 사이드바 설정 기본값
    ss.setdefault("cfg", {
        "page_range": 5,      # 뉴스 검색 페이지 수(페이지당)
        "embed": "openai",    # openai | bge
        "use_reranker": True, # True/False
        "scope": "seg",       # seg | tot
        "top_k": 30,
    })

def log(msg: str):
    st.session_state.logs.append(msg)

# ---------------------------------------------------------
# 1) 사이드바 (실행 설정)
# ---------------------------------------------------------
def build_sidebar():
    with st.sidebar:
        st.subheader("🛠️ 실행 설정")
        cfg = st.session_state.cfg

        cfg["page_range"] = st.number_input(
            "뉴스 검색 페이지 수(페이지당)", min_value=1, max_value=50,
            value=int(cfg["page_range"]), step=1
        )

        cfg["embed"] = st.selectbox(
            "VectorDB 임베딩", options=["openai", "bge"],
            index=(0 if cfg["embed"] == "openai" else 1)
        )

        use_text = "Yes" if cfg["use_reranker"] else "No"
        use_text = st.selectbox("Re-ranker 사용", ["Yes", "No"],
                                index=(0 if use_text == "Yes" else 1))
        cfg["use_reranker"] = (use_text == "Yes")

        cfg["scope"] = st.selectbox(
            "Re-ranker 비교 대상", ["seg", "tot"],
            index=(0 if cfg["scope"] == "seg" else 1),
            help="seg: 종목별 후보만 대상으로 비교, tot: 전체 후보군에서 비교"
        )

        cfg["top_k"] = st.number_input(
            "Re-ranker Top-N (k)", min_value=5, max_value=200,
            value=int(cfg["top_k"]), step=5
        )

        st.caption("※ OpenAI 키 등은 환경변수 /.env 에서 읽습니다.")

        st.session_state.cfg = cfg

# ---------------------------------------------------------
# 2) 각 단계 실행 로직
# ---------------------------------------------------------
def set_state(step, state):
    st.session_state.status[step] = state

def can_run(step):
    prereq = DEPEND.get(step)
    return (prereq is None) or (st.session_state.status[prereq] == "done")

def run_verify():
    set_state("verify", "running"); log("· 고객 정보 확인 시작")
    try:
        etf = ETF_DB(path="DB/ETF.db")
        etf_df = etf.Show_etf_top5()

        cus = Customer(cus_path="DB/Customer.db")
        cus_df = cus.get_cus_df(data=etf_df)
        tickers = cus.get_ticker_lst(data=cus_df)
        cus.save_cus_df(data=cus_df)

        st.session_state.tickers = tickers
        log(f"· 보유 종목: {tickers}")
        set_state("verify", "done")
    except Exception as e:
        log(f"[verify error] {e}")
        set_state("verify", "error")

def run_crawl():
    set_state("crawl", "running"); log("· 뉴스 수집 시작")
    try:
        cfg = st.session_state.cfg
        tickers = st.session_state.tickers or []
        if not tickers:
            raise RuntimeError("보유 종목이 없습니다. 먼저 '고객 정보 확인'을 실행하세요.")

        coll = Task_collect()
        for t in tickers:
            log(f"· 크롤링: {t}")
            coll.extract_news_data(t, int(cfg["page_range"]))
            time.sleep(0.1)

        df = coll.save_news_df()
        st.session_state.news_df_len = len(df)
        log(f"· 저장된 기사 수: {len(df)}")
        set_state("crawl", "done")
    except Exception as e:
        log(f"[crawl error] {e}")
        set_state("crawl", "error")

def run_vectordb():
    set_state("vectordb", "running"); log("· VectorDB 저장 시작")
    try:
        cfg = st.session_state.cfg
        tickers = st.session_state.tickers or []
        if not tickers:
            raise RuntimeError("보유 종목이 없습니다. 먼저 '고객 정보 확인'을 실행하세요.")

        df = Task_collect.save_news_df()
        Vec = VectorDB()
        Vec.save_vectordb(target_list=tickers, df=df, kind=cfg["embed"])
        Vec.show_cnts(kind=cfg["embed"])
        set_state("vectordb", "done")
    except Exception as e:
        log(f"[vectordb error] {e}")
        set_state("vectordb", "error")

def run_render():
    set_state("render", "running"); log("· 화면 표출(요약) 시작")
    try:
        cfg = st.session_state.cfg
        tickers = st.session_state.tickers or []
        if not tickers:
            raise RuntimeError("보유 종목이 없습니다.")

        # Re-ranker 사용 시: 한 종목 샘플 요약 생성 (데모)
        if cfg["use_reranker"]:
            target = tickers[0]
            log(f"· Re-ranker 사용: {cfg['scope']} / Top-{cfg['top_k']}, 종목: {target}")

            # get_original_news_after_reranker 내부에서 k는 모델 생성 시 사용
            # (Test.reranker_model(k=?)) — 아래처럼 변경하여 전달
            Test.reranker_model = staticmethod(lambda k=cfg["top_k"]:
                                               Test.__dict__['reranker_model'](k=cfg["top_k"]))
            total_text = Test.get_original_news_after_reranker(
                ticker=target, kind=cfg["embed"]
            )
            cross = Test()
            df_sum = cross.summarize_top_articles_after_reranker(
                total_contents=total_text, ticker=target, max_iters=3
            )
            st.session_state.summary_df = df_sum
            log("· 요약 생성 완료")
        else:
            log("· Re-ranker 미사용 — 요약 스킵(또는 사용자 정의 경로)")

        set_state("render", "done")
    except Exception as e:
        log(f"[render error] {e}")
        set_state("render", "error")

RUNNERS = {
    "verify": run_verify,
    "crawl": run_crawl,
    "vectordb": run_vectordb,
    "render": run_render,
}

def run_step(step_key):
    RUNNERS[step_key]()

# ---------------------------------------------------------
# 3) UI
# ---------------------------------------------------------
st.set_page_config(page_title="단계별 파이프라인", page_icon="🧭", layout="wide")
init_state()
build_sidebar()

st.title("🧭 단계별 파이프라인 실행기")
st.caption("상단 컨트롤은 항상 고정. 각 단계는 버튼 클릭 또는 순차 실행으로 동작합니다.")

# 상단 고정 컨트롤
colA, colB, _ = st.columns([1.5, 1.2, 6])
with colA:
    if st.button("▶️ 순차 실행 (처음부터)", use_container_width=True):
        # 모든 단계 순차 실행
        for k, *_ in STEPS:
            if can_run(k):
                run_step(k)
            else:
                st.warning(f"이전 단계가 완료되지 않아 '{k}'를 건너뜁니다.")
                break
with colB:
    if st.button("🧼 상태 초기화", use_container_width=True):
        st.session_state.status = {k: "waiting" for k, *_ in STEPS}
        st.session_state.logs = []
        st.session_state.tickers = []
        st.session_state.news_df_len = 0
        st.session_state.summary_df = None
        st.rerun()

st.markdown("---")

# 단계 버튼(상단 4개)
cols = st.columns(len(STEPS))
for i, (key, label, desc) in enumerate(STEPS):
    with cols[i]:
        icon = status_icon(st.session_state.status[key])
        disabled = not can_run(key)
        if st.button(f"{icon} {label}", key=f"btn_{key}", disabled=disabled, use_container_width=True):
            run_step(key)
        st.caption(desc)

# 상태 다이어그램
dot = graphviz.Digraph()
dot.attr(rankdir="LR", splines="polyline", nodesep="1")
dot.attr(size="12,2!", ratio="compress")  # 가로 12인치, 세로 2인치로 강제
for key, label, _ in STEPS:
    dot.node(key, label, shape="box", style="filled,rounded",
             fillcolor=status_color(st.session_state.status[key]))
dot.edge("verify", "crawl")
dot.edge("crawl", "vectordb")
dot.edge("vectordb", "render")
st.graphviz_chart(dot)

# 결과/로그
st.subheader("📊 단계별 결과/로그")
st.info(f"보유 종목: {st.session_state.tickers or '-'} / 저장된 기사 수: {st.session_state.news_df_len}")

with st.expander("로그 열기", expanded=True):
    if st.session_state.logs:
        st.write("\n\n".join([f"- {m}" for m in st.session_state.logs]))
    else:
        st.write("아직 로그가 없습니다.")

# 요약 표
if st.session_state.summary_df is not None:
    st.subheader("📝 샘플 요약 결과")
    st.dataframe(st.session_state.summary_df, use_container_width=True)
