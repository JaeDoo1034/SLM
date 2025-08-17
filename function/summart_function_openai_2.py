from typing import TypedDict
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable
import re
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate

# --- State: optional 필드 허용(total=False) ---
class NewsSummaryState(TypedDict, total=False):
    article: str
    summary: str
    feedback: str
    iteration: int
    # 최종 산출물
    final_summary: str
    last_feedback: str
    # 내부 제어용(최소 1회 리파인 보장)
    refined_once: bool

class SummaryOutput(BaseModel):
    refined_summary: str = Field(..., description="개선된 뉴스 요약문")

class NewsSummaryAgent:
    def __init__(
        self,
        model_name: str = "gpt-4o",
        temperature: float = 0.3,
        max_tokens: int = 2048,
        max_iters: int = 3,
    ):
        self.max_iters = max_iters

        self.llm = ChatOpenAI(model=model_name, temperature=temperature, max_tokens=max_tokens)
        self.llm_strict_output = ChatOpenAI(model=model_name, temperature=0, max_tokens=max_tokens)\
            .with_structured_output(SummaryOutput)

    def _call_llm(self, prompt: str) -> str:
        return self.llm.invoke(prompt).content

    def generate_initial_summary(self, state: NewsSummaryState) -> NewsSummaryState:
        article = state["article"]
        prompt = f"""
      당신은 금융 시장 관련 전문 뉴스 편집자입니다.
      다음 뉴스 기사의 가장 중요한 내용 세 가지를 불릿 포인트 형식으로 요약해주세요.
      각 불릿 포인트는 하나의 핵심 아이디어를 담고 간결해야 합니다.
      각 불릿 포인트 아래에는 해당 불릿 포인트를 설명해주세요.
      요약 후에 해당 뉴스기사의 키워드를 추출하여 사용자에게 제공해주세요.
      
      너가 알고 있는 정보를 활용하지 말고, 뉴스 기사 내용만을 가지고 요약을 해야합니다.
      
      
      아래는 당신이 수행해야 할 업무의 예시입니다.
      아래 예시를 참고하여 <TASK>를 수행해주세요.

      <EXAMPLE>
      뉴스 기사:
      다이아몬드힐인베스트먼트그룹(DHIL, DIAMOND HILL INVESTMENT GROUP INC )은 CEO와의 고용 계약을 갱신했다.
      13일 미국 증권거래위원회에 따르면 2025년 6월 12일, 다이아몬드힐인베스트먼트그룹(이하 ‘회사’)은 CEO인 헤더 E. 브릴리언트와 수정 및 재작성된 고용 계약을 체결했다.
      이 계약은 2021년 10월 26일에 체결된 이전 계약을 대체하며, 브릴리언트의 고용 기간을 2030년 6월 30일까지 연장한다.
      계약에 따르면, 브릴리언트는 연간 40만 달러의 기본 급여를 받으며, 연간 현금 인센티브 상한액은 175만 달러로 설정된다. 이 금액은 회사의 성과와 브릴리언트의 성과에 따라 결정되며, 최소 60만 달러는 지급된다.
      또한, 브릴리언트는 연간 85만 달러의 장기 인센티브 주식 보상을 받을 수 있으며, 이는 3년 동안 비례적으로 분배된다. 2025년 6월 30일에는 400만 달러의 가치가 있는 제한 주식이 지급되며, 이는 5년 후에 완전히 소유권이 이전된다.
      계약에 따라 브릴리언트는 건강 및 생명 보험, 장애 프로그램, 퇴직 연금 계획 등 다양한 복리후생을 제공받는다. 만약 브릴리언트가 사망할 경우, 그녀의 수혜자는 미지급된 기본 급여와 연간 현금 인센티브 상을 받을 수 있다.
      계약 종료 시, 브릴리언트는 회사의 모든 직책에서 사임해야 하며, 계약의 모든 조건을 준수해야 한다. 이 계약은 회사의 이익을 보호하기 위해 비경쟁, 비유인, 비밀유지 조항을 포함하고 있다.계약의 전체 내용은 첨부된 문서에서 확인할 수 있다.

      결과:

      ✅ 주요 요약
      - 다이아몬드힐인베스트먼트그룹, CEO 고용 계약 2030년까지 연장
        기존 계약을 대체하는 새로운 고용 계약이 체결되었으며, 브릴리언트 CEO의 재임 기간은 2030년 6월까지로 연장됨.

      - CEO 보수 패키지, 기본급 외 최대 175만 달러 인센티브 및 주식 보상 포함
        브릴리언트는 최소 60만 달러 이상의 연간 인센티브와 85만 달러 상당의 장기 주식 보상, 400만 달러 상당의 제한 주식도 수령 예정.

      - 계약에 비경쟁·비유인·비밀유지 조항 포함, 회사 이익 보호 목적
        계약 종료 시에는 모든 직책에서 사임해야 하며, 복리후생 및 유족 보상 조항도 명시됨.

      분류: 긍정

      뉴스 기사:
      {article}

      결과:
      """
        summary = self._call_llm(prompt)
        print(f'summart : {summary}')
        # 🔑 여기서는 iteration을 절대 쓰지 않음 (초기 state의 0 유지)
        return {"summary": summary, "refined_once": False}

    def generate_feedback_check_eval(self, state: NewsSummaryState) -> NewsSummaryState:
        prompt = f"""
다음 뉴스 기사와 요약을 보고, 아래 4가지 기준에 따라 요약을 평가하세요:

[뉴스 기사]
{state['article']}

[요약]
{state['summary']}

[요약 평가 기준]
1. 정확성(Accuracy): 요약 내용이 원문 기사와 일치하는가?
2. 포괄성(Coverage): 중요한 정보가 모두 포함되었는가?
3. 간결성(Conciseness): 불필요한 표현 없이 간결한가?
4. 문장구성(Clarity): 자연스럽고 명확한가?
5. 일관성(Consistency) : 특정 종목에 대한 내용만 존재하는 가?

각 기준에 대해 다음 형식으로 평가:
- 정확성: 좋음 / 부족함 <reason> [간단한 이유] </reason>
- 포괄성: 좋음 / 부족함 <reason> [간단한 이유] </reason>
- 간결성: 좋음 / 부족함 <reason> [간단한 이유] </reason>
- 문장구성: 좋음 / 부족함 <reason> [간단한 이유] </reason>
- 일관성: 좋음 / 부족함 <reason> [간단한 이유] </reason>

그 다음, 개선이 필요한 항목에 대해 피드백을 작성하세요.
"""
        feedback = self._call_llm(prompt)
        # 🔑 iteration 건드리지 않음
        return {"feedback": feedback}

    def refine_summary(self, state: NewsSummaryState) -> NewsSummaryState:
        article = state["article"]
        current_summary = state["summary"]
        feedback = state["feedback"]

        refine_tmpl = PromptTemplate.from_template(
        """당신은 뉴스 요약 전문가입니다. 아래 기사, 기존 요약, 피드백을 참고하고, 예시 형태를 갖추면서 요약을 개선하세요.
        [예시]
        ✅ 주요 요약
        - 다이아몬드힐인베스트먼트그룹, CEO 고용 계약 2030년까지 연장
            기존 계약을 대체하는 새로운 고용 계약이 체결되었으며, 브릴리언트 CEO의 재임 기간은 2030년 6월까지로 연장됨.

        - CEO 보수 패키지, 기본급 외 최대 175만 달러 인센티브 및 주식 보상 포함
            브릴리언트는 최소 60만 달러 이상의 연간 인센티브와 85만 달러 상당의 장기 주식 보상, 400만 달러 상당의 제한 주식도 수령 예정.

        - 계약에 비경쟁·비유인·비밀유지 조항 포함, 회사 이익 보호 목적
            계약 종료 시에는 모든 직책에서 사임해야 하며, 복리후생 및 유족 보상 조항도 명시됨.
                

        [기사]
        {article}

        [기존 요약]
        {current_summary}

        [피드백]
        {feedback}

        [개선된 요약]
        """
        )

        chain = refine_tmpl | self.llm_strict_output
        result: SummaryOutput = chain.invoke({
            "article": article,
            "current_summary": current_summary,
            "feedback": feedback,
        })
        print(f'====== result : {result}')
        # 🔑 iteration은 오직 여기서만 +1
        return {
            "summary": result.refined_summary,
            "iteration": state['iteration'] + 1,
            "refined_once": True,
        }

    def should_stop(self, state: NewsSummaryState):
        feedback = state.get("feedback", "")
        iteration = state.get("iteration", 0)
        refined_once = state.get("refined_once", False)

        print("[should_stop] Iteration:", iteration)
        print("[should_stop] Feedback:\n", feedback)

        if not refined_once:
            next_step = "no"  # 최소 1회 리파인 보장
        else:
            criteria = ["정확성", "포괄성", "간결성", "문장구성", "일관성"]
            all_good = all(re.search(rf"-?\s*{c}\s*:\s*좋음", feedback) for c in criteria)
            next_step = "yes" if all_good or iteration >= self.max_iters else "no"

        print("[should_stop] next_step =", next_step)
        # 🔑 iteration을 절대 쓰지 않음
        return {"next_step": next_step}

    def final_output(self, state: NewsSummaryState):
        print("final_output")
        # 🔑 iteration을 여기서 다시 쓰지 않음 (읽기만)
        return {
            "final_summary": state.get("summary", ""),
            "last_feedback": state.get("feedback", "")
        }

def build_summary_graph(agent: NewsSummaryAgent) -> Runnable:
    graph = StateGraph(state_schema=NewsSummaryState)

    graph.add_node("generate_initial_summary", agent.generate_initial_summary)
    graph.add_node("generate_feedback", agent.generate_feedback_check_eval)
    graph.add_node("refine_summary", agent.refine_summary)
    graph.add_node("should_stop", agent.should_stop)
    graph.add_node("final_output", agent.final_output)

    # 🔧 동시(fan-out) 제거: 순차 흐름만 유지
    graph.set_entry_point("generate_initial_summary")
    graph.add_edge("generate_initial_summary", "generate_feedback")
    graph.add_edge("generate_feedback", "should_stop")
    graph.add_conditional_edges(
        "should_stop",
        lambda s: s["next_step"],
        {"yes": "final_output", "no": "refine_summary"},
    )
    graph.add_edge("refine_summary", "generate_feedback")
    graph.set_finish_point("final_output")

    return graph.compile()

def summarize_article(article_text: str) -> dict:
    agent = NewsSummaryAgent()
    runnable = build_summary_graph(agent)
    # 🔑 초기 state에서만 iteration 세팅 (0)
    return runnable.invoke({
        "article": article_text,
        "summary": "",
        "feedback": ""
    })
