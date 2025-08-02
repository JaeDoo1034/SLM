from openai import OpenAI
import json

from function.stock_data import get_today_yield

client = OpenAI(api_key='')

messages = [{"role": "user", "content": "삼성전자 수익률 알려줘"}]

tools = [
    {
        "type": "function",
        "name": "get_today_yield",
        "description": "주어진 종목의 현재 수익률을 가져온다.",
        "parameters": {
            "type": "object",
            "properties": {
                "stock_code": {
                    "type": "string",
                    "description": "종목코드, e.g. A005930, A69500",
                }
            },
            "required": ["stock_code"],
            "additionalProperties": False
        },
    }
]


def function_calling_gpt(input_message):
    response = client.responses.create(
        model="gpt-4o-mini",
        input=input_messages,
        tools=tools
    )

    print("첫번재 응답")
    print(response.output)

    tool_call = response.output[0]
    args = json.loads(tool_call.arguments)

    result = get_today_yield(*args)

    input_messages.append(tool_call)  # append model's function call message
    input_messages.append({  # append result message
        "type": "function_call_output",
        "call_id": tool_call.call_id,
        "output": str(result)
    })

    response_2 = client.responses.create(
        model="gpt-4o-mini",
        input=input_messages,
        tools=tools,
    )


    print(response_2.output_text)
    return response_2.output_text

if __name__ == "__main__":
    print("test function calling~")

    input_messages = [{"role": "user", "content": "삼성전자 수익률 알려줘"}]

    result = function_calling_gpt(input_messages)

    print(result)
