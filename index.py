import json
import os
import re
from dotenv import load_dotenv
from openai import OpenAI
import prompt_parts.system_prompt_parts

load_dotenv()

client = OpenAI(
    organization=os.environ.get("OPENAI_ORGANIZATION"),
    project=os.environ.get("OPENAI_PROJECT"),
)


def sum(args):
    return args["x"] + args["y"]


tools = [
    {
        "name": "sum",
        "purpose": "Receives two numbers and returns the sum of the numbers",
        "arguments": [
            {"name": "x", "purpose": "the first of the two numbers to be summed"},
            {"name": "y", "purpose": "the second of the two numbers to be summed"},
        ],
    }
]

tool_implementations = {
    "sum": sum,
}


def parse_tool_call(response):
    pattern = r"\bAction \d+:\b"
    tool_call = re.split(pattern, response)[-1]
    # search for the boundaries of the returned JSON
    k = tool_call.find("{")
    l = tool_call.rfind("}")
    tool_call = tool_call[k : l + 1]
    return json.loads(tool_call)

prompt = input("Enter a prompt: ")

messages = [
    {"role": "system", "content": prompt_parts.system_prompt_parts.prompt_intro},
    {
        "role": "system",
        "content": prompt_parts.system_prompt_parts.sample_react_thought_chain,
    },
    {
        "role": "system",
        "content": prompt_parts.system_prompt_parts.tool_setup_intro,
    },
    {"role": "system", "content": str(tools)},
    {"role": "system", "content": prompt_parts.system_prompt_parts.react_nudge},
    {"role": "user", "content": "Question: " + prompt},
]

iteration = 1
while True:
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages
    )

    response = completion.choices[0].message.content
    ## add the response to context
    messages.append(
        {"role": "assistant", "content": response}
    )

    tool_call = parse_tool_call(response)
    if tool_call["tool"] == "finish":
        print(tool_call["args"]["response"])
        break

    tool_name = tool_call["tool"]
    tool_args = tool_call["args"]
    tool_response = str(tool_implementations[tool_name](tool_args))
    messages.append(
        {
            "role": "assistant",
            "content": "Observation " + str(iteration) + ": " + tool_response,
        }
    )

    iteration += 1
    if iteration == 5:
        break
