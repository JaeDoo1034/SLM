import streamlit as st
import time
import graphviz

# ------------------------------------------------------------------
# 1) 세션 상태 초기화
# ------------------------------------------------------------------
if "status" not in st.session_state:
    st.session_state.status = {
        "schedule_trigger": "waiting",
        "mysql": "waiting",
        "compare": "waiting",
        "create_person": "waiting",
        "create_contact": "waiting",
    }

# ------------------------------------------------------------------
# 2) 상태 → 아이콘 / 색상 매핑
# ------------------------------------------------------------------
def status_icon(state: str) -> str:
    return {
        "waiting": "⚪️",
        "running": "⏳",
        "done": "✅",
        "error": "❌",
    }.get(state, "⚪️")


def status_color(state: str) -> str:
    """Graphviz 색상 (fillcolor)용"""
    return {
        "waiting": "white",
        "running": "yellow",
        "done": "lightgreen",
        "error": "red",
    }.get(state, "white")


# ------------------------------------------------------------------
# 3) 실제 작업 함수(시뮬레이션)
# ------------------------------------------------------------------
def run_job(job_name: str):
    st.session_state.status[job_name] = "running"
    # 실제 작업이 들어가는 부분 (여기선 sleep으로 대체)
    time.sleep(1.2)
    st.session_state.status[job_name] = "done"


# ------------------------------------------------------------------
# 4) UI 타이틀
# ------------------------------------------------------------------
st.title("🔄 Job 프로세스 실행기")

# ------------------------------------------------------------------
# 5) 단계 정의 및 의존 관계
# ------------------------------------------------------------------
steps = [
    ("schedule_trigger", "Schedule Trigger", "스케줄 기반 트리거"),
    ("mysql", "MySQL Query", "DB 대상 추출"),
    ("compare", "Compare Datasets", "변경 데이터 비교"),
    ("create_person", "Create Person", "신규 고객 생성"),
    ("create_contact", "Create Contact", "연락처 생성"),
]

dependencies = {
    "schedule_trigger": None,
    "mysql": "schedule_trigger",
    "compare": "mysql",
    "create_person": "compare",
    "create_contact": "compare",
}

# ------------------------------------------------------------------
# 6) 버튼 UI (가로 배치)
# ------------------------------------------------------------------
cols = st.columns(len(steps))
for idx, (key, label, desc) in enumerate(steps):
    with cols[idx]:
        # 의존 단계가 완료되지 않았으면 disabled
        prereq = dependencies[key]
        disabled = False if prereq is None else st.session_state.status[prereq] != "done"

        if st.button(f"{status_icon(st.session_state.status[key])} {label}", key=key, disabled=disabled):
            run_job(key)

        st.caption(desc)

# ------------------------------------------------------------------
# 7) Graphviz 흐름도 (상태 색상 반영 + 선 연결)
# ------------------------------------------------------------------
dot = graphviz.Digraph()
dot.attr(rankdir="LR", splines="polyline", nodesep="1")

for key, label, _ in steps:
    dot.node(
        key,
        label,
        shape="box",
        style="filled,rounded",
        fillcolor=status_color(st.session_state.status[key]),
    )

# 연결선
dot.edge("schedule_trigger", "mysql")
dot.edge("mysql", "compare")
dot.edge("compare", "create_person")
dot.edge("compare", "create_contact")

st.graphviz_chart(dot)

# ------------------------------------------------------------------
# 8) 리셋 버튼
# ------------------------------------------------------------------
st.divider()
if st.button("🔄 상태 초기화"):
    for k in st.session_state.status:
        st.session_state.status[k] = "waiting"
