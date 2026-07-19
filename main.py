import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import argparse
from prompts import *
from call_function import *

#loading API key from .env
load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")

if api_key == None:
    raise RuntimeError("API key not found")

#connecting
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

#handling command-line args
parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()
#Now we can access `args.user_prompt`

#it's better to write a function to get the response
#talking to API
def generate_content(client, messages):

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        tools=available_functions
    )

    if response.usage == None:
        raise RuntimeError("Response usage property is None")
    
    if args.verbose:
        print(f"User prompt: {messages[0]['content']}")
        print(f"Prompt tokens: {response.usage.prompt_tokens}")
        print(f"Response tokens: {response.usage.completion_tokens}")

    message = response.choices[0].message

    if message.tool_calls:
        for tool_call in message.tool_calls:
            result_message = call_function(tool_call=tool_call, verbose=args.verbose)
            if result_message["content"] == None:
                raise Exception()
            if args.verbose:
                print(f"-> {result_message['content']}")
    
    print(f"Response: {response.choices[0].message.content}")


def main():
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]
    generate_content(client, messages)

if __name__ == "__main__":
    main()
