import json
import os

from dotenv import load_dotenv
from groq import Groq

from src.models import CompanyIntelligence
from src.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_company_intelligence(
    domain: str,
    website_content: str,
) -> CompanyIntelligence:
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": USER_PROMPT_TEMPLATE.format(
                    domain=domain,
                    website_content=website_content,
                ),
            },
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("LLM returned an empty response.")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"LLM returned invalid JSON for {domain}: {error}"
        ) from error

    return CompanyIntelligence.model_validate(data)