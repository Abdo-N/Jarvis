import os
from dotenv import load_dotenv
from openai import OpenAI
import argparse

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
args = parser.parse_args()
#Now we can access `args.user_prompt`

def main():
    response = client.chat.completions.create(
    model="openrouter/free",
    messages=[
        {
            "role": "user",
            "content": args.user_prompt
        }
    ])

    if response.usage == None:
        raise RuntimeError("Response usage property is None")
    else:
        print(f"Prompt tokens: {response.usage.prompt_tokens}")
        print(f"Response tokens: {response.usage.completion_tokens}")
        print(f"Response: {response.choices[0].message.content}")


if __name__ == "__main__":
    main()
