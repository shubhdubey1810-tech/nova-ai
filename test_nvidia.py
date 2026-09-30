import os

from dotenv import load_dotenv
from openai import OpenAI


# Load .env
load_dotenv(
    override=True
)


api_key = os.getenv(
    "NVIDIA_API_KEY"
)

base_url = os.getenv(
    "NVIDIA_BASE_URL",
    "https://integrate.api.nvidia.com/v1"
)

model = os.getenv(
    "NVIDIA_MODEL"
)


print(
    "NVIDIA API key loaded:",
    bool(api_key)
)

print(
    "NVIDIA model:",
    model
)

print(
    "NVIDIA endpoint:",
    base_url
)


if not api_key:
    raise RuntimeError(
        "NVIDIA_API_KEY is missing from .env"
    )


if not model:
    raise RuntimeError(
        "NVIDIA_MODEL is missing from .env"
    )


client = OpenAI(
    base_url=base_url,
    api_key=api_key
)


try:

    response = client.chat.completions.create(

        model=model,

        messages=[
            {
                "role": "user",
                "content": (
                    "Hello NØVA. "
                    "Reply with one short sentence."
                )
            }
        ],

        temperature=0.7,

        max_tokens=100,
    )


    answer = (
        response
        .choices[0]
        .message
        .content
    )

    print()
    print("NVIDIA response:")
    print(answer)


except Exception as error:

    print()
    print("NVIDIA request failed:")
    print(error)