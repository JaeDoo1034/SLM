from typing import TypedDict
from langgraph.graph import StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig, SafetySetting
from langchain_core.runnables import Runnable
from google import genai
import vertexai
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

class NewsSummaryState(TypedDict):
  article: str
  summary: str
  feedback: str
  iteration: int


class NewsSummaryAgent:
  def __init__(self,
               location:str = "us-central1",
               model_name = "gemini-2.5-flash-preview-05-20",
               **config_kwargs
               ):
    load_dotenv() # .env 파일에서 환경변수 로딩
    self.project_id = os.getenv("PROJECT_ID")

    if not self.project_id:
      raise ValueError("PROJECT_ID가 .env에 설정되어있지 않습니다.")
    

    vertexai.init(project="nimble-gate-464210-t4", location="us-central1")
    self.model_name = model_name
    self.model = GenerativeModel(model_name)

    # GenerationConfig 객체를 직접 생성하여 전달합니다.
    self.gen_config = GenerationConfig(
          temperature = config_kwargs.get("temperature", 0.3),
          top_p = config_kwargs.get("top_p", 0.95),
          max_output_tokens = config_kwargs.get("max_output_tokens", 10000),
          candidate_count = config_kwargs.get("candidate_count", 1),
    )

    # # SafetySetting 객체 리스트를 직접 생성하여 전달합니다.
    # self.safety_settings = config_kwargs.get("safety_settings",[
    #     SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=SafetySetting.SafetyThreshold.BLOCK_LOW_AND_ABOVE),
    #     SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=SafetySetting.SafetyThreshold.BLOCK_LOW_AND_ABOVE),
    # ])


  def _call_llm_stand_alone(self, prompt:str, **kwargs) -> str:
    """
    llm 모델을 호출합니다.
    Generator보다는 Verifier의 성능이 중요합니다.(IAD)
    - Gemini는 model_candidate 변수가 있어 후보문장 수로 역할을 분배할 수 있을 것 같습니다.
    - Generator
    - Verifier
    """

    contents = [prompt]
    response = self.model.generate_content(
        contents = contents,
        generation_config= self.gen_config, # config는 generation_config로 전달
    )
    return response.text


  def call_llm(self,model_name:str,prompt:str):
    return self._call_llm_stand_alone(prompt)


  def generate_initial_summary(self, state):
    """
    최초의 뉴스기사 요약을 진행하는 함수입니다.
    llm을 호출합니다.
    """
    news_article = state['article']
    brief_prompt = f"""

      당신은 금융 시장 관련 전문 뉴스 편집자입니다.
      다음 뉴스 기사의 가장 중요한 내용 세 가지를 불릿 포인트 형식으로 요약해주세요.
      각 불릿 포인트는 하나의 핵심 아이디어를 담고 간결해야 합니다.
      각 불릿 포인트 아래에는 해당 불릿 포인트를 설명해주세요.
      요약 후에 해당 뉴스기사의 키워드를 추출하여 사용자에게 제공해주세요.

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

      🔑 키워드
      - 다이아몬드힐인베스트먼트그룹 (Diamond Hill Investment Group, DHIL)
      - Heather E. Brilliant
      - CEO 고용 계약
      - 인센티브 보상
      - 제한 주식
      - 비경쟁 조항
      - 미국 증권거래위원회 (SEC)

      분류: 긍정

      뉴스 기사:
      {news_article}

      결과:
      """

    summary_output = self._call_llm_stand_alone(brief_prompt)
    state['summary'] = summary_output
    state['iteration'] = 1
    return state

  def generate_feedback_check_eval(self,state):
    """
    check-eval을 활용해서 feedback을 생성합니다.
    """
    article = state['article']
    summary = state['summary']

    feedback_prompt = f"""
    다음 뉴스 기사와 요약을 보고, 아래 4가지 기준에 따라 요약을 평가하세요:

    [뉴스 기사]
    {article}

    [요약]
    {summary}

    [요약 평가 기준]

    1. 정확성(Accuracy): 요약 내용이 원문 기사와 일치하는가?
    2. 포괄성(Coverage): 중요한 정보가 모두 포함되었는가?
    3. 간결성 (Conciseness): 불필요한 표현 없이 간결하게 작성되었는가?
    4. 문장구성(Clarity): 자연스럽고 명확한 문장 구조인가?

    각 기준에 대해 다음 형식으로 평가해주세요:
    - 정확성: 좋음 / 부족함 <reason> [간단한 이유] </reason>
    - 포괄성: 좋음 / 부족함 <reason> [간단한 이유] </reason>
    - 간결성: 좋음 / 부족함 <reason> [간단한 이유] </reason>
    - 문장구성: 좋음 / 부족함 <reason> [간단한 이유] </reason>

    그 다음, 개선이 필요한 항목에 대하여 평가에서 생성한 간단한 이유를 활용하여 다음 형식으로 구체적인 피드백을 작성하세요:

    [피드백]
    - (예시) 포괄성: 기사에 언급된 삼성전자의 주가 내용이 누락되어 있습니다.
    - (예시) 문장구성: 문장 간 연결이 자연스럽지 않으니 순서를 다듬어주세요.
    """

    feedback_output = self._call_llm_stand_alone(feedback_prompt)
    state['feedback'] = feedback_output
    return state


  def refine_summary(self,state):
      """
      이전 best 요약을 conditioning으로 받아 새 요약 후보들을 생성합니다.
      """
      article = state['article']
      current_summary = state['summary']
      feedback = state['feedback']

      refine_prompt = f"""
      다음 뉴스 기사, 기존 요약, 피드백을 참고하여 요약을 개선하세요.

      [기사]
      {article}

      [기존 요약]
      {current_summary}

      [피드백]
      {feedback}

      [개선된 요약]

      """
      refine_output = self._call_llm_stand_alone(refine_prompt)
      state['summary'] = refine_output
      state['iteration'] += 1
      return state


  def should_stop(self, state):
      feedback = state['feedback']
      iteration = state.get('iteration', 1)

      print("[should_stop] Iteration:", iteration)
      print("[should_stop] Feedback:\n", feedback)

      criteria = ["정확성","포괄성","간결성","문장구성"]
      all_good = all(
          f"{criterion}: 좋음" in feedback for criterion in criteria
      )

      if all_good or iteration >= 3:
        return {"next_step":"yes",**state}
      else:
        return {"next_step":"no",**state}

  def final_output(self,state):

    return {
        "final_summary":state["summary"],
        "last_feedback":state["feedback"],
        "iteration":state.get("iteration",1)
    }

  

  def run_batch_parallel(self, df: pd.DataFrame, max_workers: int = 5):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(lambda article: self.runnable.invoke({
                "article": article,
                "summary": "",
                "feedback": "",
                "iteration": 0
            }), row["article"]): idx
            for idx, row in df.iterrows()
        }
        for future in as_completed(futures):
            idx = futures[future]
            try:
                results.append(future.result())
            except Exception as e:
                print(f"[에러] 인덱스 {idx}: {e}")
                results.append(None)
    return results

def build_summary_graph(agent: NewsSummaryAgent) -> Runnable:
    agent = NewsSummaryAgent()
    graph = StateGraph(state_schema=NewsSummaryState)
    graph.add_node("generate_initial_summary", agent.generate_initial_summary)
    graph.add_node("generate_feedback",agent.generate_feedback_check_eval)
    graph.add_node("refine_summary",agent.refine_summary)
    graph.add_node("should_stop",agent.should_stop)
    graph.add_node("final_output",agent.final_output)
    graph.set_entry_point("generate_initial_summary")
    graph.add_edge("generate_initial_summary","generate_feedback")
    graph.add_edge("generate_feedback","should_stop")
    graph.add_edge("refine_summary","generate_feedback")
    graph.add_conditional_edges(
        "should_stop",
        lambda x: x['next_step'],
        {
            "yes":"final_output",
            "no":"refine_summary"
        }
        )

    graph.set_finish_point("final_output")
    return graph.compile()

def summarize_article(article_text:str) -> dict:
   agent = NewsSummaryAgent()
   runnable = build_summary_graph(agent)
   return runnable.invoke({
      "article":article_text,
      "summary":"",
      "feedback":"",
      "iteration":0
   })