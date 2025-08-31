# 라이브러리 불러오기
import smtplib
import requests
import json
import markdown

# 개인 정보 입력(email, 앱 비밀번호)
my_email = "wj.jang.wooriib@gmail.com"
password = "vvsh cvxa xjuw dqqd"

import smtplib
from email.message import EmailMessage
from email.headerregistry import Address


def send_mail(mail_addr: str, content: str):
    msg = EmailMessage()
    msg["Subject"] = "MY 퇴직연금관리 - 퇴직연금리포트"
    msg["From"] = Address(display_name="MY 퇴직연금관리", username="am.woojin", domain="gmail.com")
    msg["To"] = Address(display_name="장우진", username=mail_addr.split("@")[0], domain=mail_addr.split("@")[1])

    # 본문을 UTF-8로 지정
    msg.set_content(content, subtype="plain", charset="utf-8")
    html_content = markdown.markdown(content)
    msg.add_alternative(html_content, subtype="html")

    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(user=my_email, password=password)
        s.send_message(msg)  # <-- 문자열 인코딩 신경 X

    # 방법 2(with 사용)
    #with smtplib.SMTP("smtp.gmail.com") as connection:
    #    connection.starttls() #Transport Layer Security : 메시지 암호화
    #    connection.login(user=my_email, password=password)
    #    connection.sendmail(
    #        from_addr=my_email,
    #        to_addrs=mail_addr,
    #        msg=msg
    #    )

def send_kakao():

    params = {
        'REST_API_key': '1d34c857df2280b64048ec88b9689a84',
        'Redirect_URI': 'https://example.com/oauth&response_type=code',
        'code': '3b2h5Q7EeTcjSpeklN_qSmLPG-0pe_JlYJFMtRRXCQi4zfZJbKf9QAAAAQKFyIgAAABmNWPyAf_A_o_BVb6-Q'
    }

    url = 'https://kauth.kakao.com/oauth/token'
    client_id = params['REST_API_key']
    redirect_uri = params['Redirect_URI']
    code = params['code']

    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'code': code,
    }

    response = requests.post(url, data=data)
    tokens = response.json()

    access_token = tokens['access_token']

    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    headers = {
        "Authorization": "Bearer " + tokens["access_token"]
    }

    data = {
        'object_type': 'text',
        'text': '테스트입니다',
        'link': {
            'web_url': 'https://developers.kakao.com',
            'mobile_web_url': 'https://developers.kakao.com'
        },
        'button_title': '바로 확인'
    }

    data = {'template_object': json.dumps(data)}
    response = requests.post(url, headers=headers, data=data)
    response.status_code

if __name__ == "__main__":
    mail_addr = "fanxy0730@gmail.com"
    mail_msg = """
### 종합 투자 리포트: 주요 보유 종목 분석 및 전략

**1. 종목별 핵심 뉴스 및 가격 영향 경로 비교**

📌 각 종목은 고유의 모멘텀과 리스크를 보유하고 있으며, 이를 종합적으로 판단하는 것이 중요합니다.

*   **삼성전자**
    📈 **실적 턴어라운드 가시화 (긍정, 단기/중기)**: `3분기` 잠정 영업이익 `2조 4000억원`은 시장 컨센서스를 상회하며 **반도체 업황 회복의 신호탄**으로 해석됩니다. 메모리 감산 효과가 본격화되고 수요가 회복되면서 단기 및 중기적 주가에 긍정적 영향을 미칠 핵심 동력입니다.
    📈 **미래 성장 동력 투자 (긍정, 장기)**: '미래로봇추진단' 신설 및 레인보우로보틱스 지분 확보 등 **로봇 사업에 대한 본격적인 투자**는 장기적 관점에서 기업 가치를 제고할 핵심 모멘텀입니다. 이는 단순한 반도체 사이클을 넘어 새로운 성장 스토리에 대한 기대감을 형성합니다.

*   **현대차**
    📈 **미국 하이브리드 시장 공략 (긍정, 중기)**: 연간 `40~50%` 성장하는 미국 하이브리드 시장에 **팰리세이드 하이브리드 모델을 출시**하는 것은 매우 시의적절한 전략입니다. 이는 전기차 보조금 축소 리스크를 헤지(Hedge)하고, 높은 관세 부담 속에서도 판매 모멘텀을 이어갈 핵심 동력입니다.
    📈 **가격 경쟁력 기반 점유율 확대 (긍정, 단기)**: `15%` 관세 부과에도 불구하고 가격 인상을 지연하며 **경쟁사 대비 가격 우위를 확보**한 전략이 `7월` 판매량 `53%` 증가로 증명되었습니다. 단기적으로 시장 점유율을 확대하는 데 매우 효과적인 전략입니다.

*   **카카오**
    📈 **스테이블코인 사업 진출 검토 (긍정, 장기)**: 카카오, 카카오페이, 카카오뱅크가 공동으로 **스테이블코인 TF를 구성**한 것은 강력한 플랫폼을 활용한 미래 금융 시장 진출 가능성을 시사합니다. 성공 시 파괴적인 신성장 동력이 될 수 있으나, 아직은 초기 검토 단계입니다.
    ⚠️ **높은 불확실성 (중립/부정, 단기/중기)**: 해당 사업은 **구체적인 실행 계획이 부재**하며, 국내외 규제 확립까지 상당한 시간이 소요될 것입니다. 단기적인 기업가치 기여는 제한적이며, 규제 리스크가 부각될 경우 오히려 투자 심리에 부정적일 수 있습니다.

*   **네이버**
    관련된 정보를 찾을 수 없습니다.

*   **LG에너지솔루션**
    📈 **기관 중심의 수급 개선 (긍정, 단기)**: 기관 투자자의 `5927억원` 순매수는 **2차전지 섹터에 대한 투자 심리 회복**을 의미합니다. 낙폭 과대에 따른 저가 매수세와 순환매 장세가 단기 주가 반등을 이끌고 있습니다.
    ⚠️ **정책 및 경쟁 리스크 상존 (부정, 중기)**: `9월 30일`로 예정된 **미국 전기차 보조금 폐지 가능성**은 배터리 수요 둔화 우려를 낳는 가장 큰 리스크입니다. 또한, 유럽 시장에서 중국 기업의 공격적인 증설은 중기적인 시장 점유율 및 수익성 압박 요인으로 작용할 것입니다.

**2. 공통 테마 식별 및 교차 영향 설명**

📌 개별 종목의 펀더멘털 외에도 거시 경제 변수와 정책이 포트폴리오 전반에 영향을 미치고 있습니다.

*   **미국 정책 변화 (규제 및 보조금)**
    미국 정부의 정책은 현대차와 LG에너지솔루션에 직접적인 교차 영향을 미칩니다. **전기차 보조금 폐지**는 전기차 수요를 위축시켜 LG에너지솔루션의 배터리 판매에 부정적이며, 동시에 현대차의 전기차 판매에도 부담을 줍니다. 반면, 이는 현대차의 **하이브리드 전략이 더욱 부각되는 계기**가 될 수 있어, LG에너지솔루션에게는 위협인 요인이 현대차에게는 기회로 작용하는 상반된 결과를 낳을 수 있습니다.

*   **신성장 동력 확보 경쟁**
    삼성전자(로봇)와 카카오(디지털 자산)는 각자의 핵심 역량을 기반으로 미래 먹거리 발굴에 나서고 있습니다. 이는 국내 대형 기술주들이 **기존 사업의 성숙기를 맞아 새로운 성장 스토리를 찾아야 하는 공통된 과제**를 안고 있음을 보여줍니다. 다만, 삼성전자의 투자는 하드웨어 제조 역량과 연계되어 비교적 구체적인 반면, 카카오의 구상은 규제 산업 내에서의 도전이라는 점에서 불확실성이 더 높습니다.

*   **글로벌 공급망 및 경쟁 구도**
    LG에너지솔루션은 **중국 기업과의 글로벌 경쟁**이라는 직접적인 위협에 노출되어 있습니다. 반면, 삼성전자는 **반도체 공급망의 회복 사이클**에 진입하며 수혜를 보고 있습니다. 이처럼 동일한 글로벌 공급망 이슈가 산업별 사이클 위치와 경쟁 구도에 따라 한쪽에는 기회로, 다른 쪽에는 위협으로 작용하고 있습니다.

*   **금리 및 환율**
    고금리 환경은 전반적인 소비 심리를 위축시켜 내구재인 자동차(현대차)와 IT기기(삼성전자) 수요에 부담을 줄 수 있습니다. 반면, 현재의 높은 원/달러 환율은 삼성전자와 현대차 같은 수출 기업의 **가격 경쟁력 및 원화 환산 이익을 증대시키는 긍정적 요인**으로 작용합니다.

**3. 종목별 리스크/촉발요인 및 모니터링 지표**

*   **삼성전자**
    ⚠️ **리스크**: 메모리 반도체 수요 회복 지연, 미-중 갈등 심화에 따른 지정학적 리스크
    📈 **촉발요인**: HBM 등 AI 반도체 시장 점유율 확대, 로봇 사업의 가시적 성과 발표
    **모니터링 지표**: DRAM/NAND 현물 가격, 글로벌 스마트폰 출하량 데이터

*   **현대차**
    ⚠️ **리스크**: 미국 시장 내 가격 경쟁 심화, 고금리로 인한 자동차 할부 금융 부담 증가
    📈 **촉발요인**: 미국 팰리세이드 하이브리드 판매 호조, 인도 등 신흥시장 점유율 확대
    **모니터링 지표**: 미국 월별 자동차 판매 데이터(특히 하이브리드 비중), 인센티브 증감률

*   **카카오**
    ⚠️ **리스크**: 스테이블코인 관련 정부의 부정적 규제 도입, 플랫폼 관련 규제 강화
    📈 **촉발요인**: 스테이블코인 사업 관련 구체적인 로드맵 및 파트너십 발표
    **모니터링 지표**: 금융당국의 디지털 자산 관련 정책 발표, 카카오톡 MAU(월간 활성 이용자 수) 추이

*   **LG에너지솔루션**
    ⚠️ **리스크**: 미국 IRA 보조금 축소 또는 폐지, 주요 고객사의 전기차 판매 목표 하향
    📈 **촉발요인**: 북미 지역 대규모 ESS 수주 계약, 리튬 등 주요 원자재 가격 안정화
    **모니터링 지표**: 미국/유럽 전기차 판매량, 배터리 핵심 광물 가격 동향, 수주 잔고 변화

**4. 결론: 포트폴리오 관점 제언**

현재 시장은 거시 경제의 불확실성과 개별 기업의 펀더멘털이 혼재된 복합적인 국면입니다. 이러한 환경을 고려하여 다음과 같은 포트폴리오 전략을 제언합니다.

*   **삼성전자 (Overweight / 비중확대)**
    반도체 업황 턴어라운드라는 명확한 단기 모멘텀과 로봇이라는 장기 성장 스토리를 겸비했습니다. **포트폴리오의 핵심 자산**으로 비중을 확대할 것을 추천합니다.

*   **현대차 (Overweight / 비중확대)**
    전기차 시장의 변동성을 헤지할 수 있는 하이브리드 라인업과 현명한 가격 정책으로 **안정적인 실적 성장이 기대**됩니다. 방어주와 성장주의 성격을 동시에 갖추고 있어 매력적입니다.

*   **LG에너지솔루션 (Neutral / 중립)**
    단기 수급 개선은 긍정적이나, 미국 정책 리스크라는 중대한 변수가 남아있습니다. **긍정 요인과 부정 요인이 팽팽히 맞서고 있어** 현재로서는 추세적인 상승을 예단하기 어렵습니다. 기존 보유 비중을 유지하며 향후 정책 방향성을 확인할 필요가 있습니다.

*   **카카오 (Underweight / 비중축소)**
    신사업에 대한 기대감은 유효하나, **가시적인 성과가 나오기까지 상당한 시간이 필요하며 규제 리스크가 큽니다.** 현재의 매크로 환경에서는 단기 실적 가시성이 높은 종목에 집중하는 것이 유리하므로, 비중 축소를 고려할 수 있습니다.
    """
    mail_msg = markdown.markdown(mail_msg)
    send_mail(mail_addr, mail_msg)
    print("finish to send email!")

    # send_kakao()
    # print("finish to send kakao")
