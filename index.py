import os
from dotenv import load_dotenv
from openai import OpenAI
import prompt_parts.system_prompt_parts

load_dotenv()

client = OpenAI(
    organization=os.environ.get("OPENAI_ORGANIZATION"),
    project=os.environ.get("OPENAI_PROJECT"),
)


def sum(args):
    return args.x + args.y


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

prompt = input("Enter a prompt: ")

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
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
    ],
)

print(completion.choices[0].message.content)
