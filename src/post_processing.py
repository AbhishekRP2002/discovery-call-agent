import json
import logging
import os
from typing import Optional
from dotenv import load_dotenv
import asyncio
from pprint import pprint
import httpx
import litellm

load_dotenv(dotenv_path=".env.local")
logging.basicConfig(level=logging.INFO)

litellm.aclient_session = httpx.AsyncClient(verify=False)


def clean_raw_transcript(raw_transcript):
    role_map = {"assistant": "Discovery Call AI Agent", "user": "Prospect"}
    conv_ctx = []
    for item in raw_transcript["items"]:
        role = role_map[item["role"]]
        content = item["content"]
        conv_ctx.append(f"{role}: {content}")
    context_str = "\n".join(conv_ctx)
    return context_str


async def get_call_summary(context_str):
    response = await litellm.acompletion(
        model="openai/gpt-4.1",
        api_key=os.getenv("OPENAI_API_KEY"),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert sales assistant. Summarize the following product discovery call "
                    "transcript in descriptive sentences, focusing on the main topics, needs or prospect pain points, and outcomes."
                ),
            },
            {
                "role": "user",
                "content": f"Conversation: {context_str}",
            },
        ],
    )
    pprint(response)
    return response["choices"][0]["message"]["content"]


async def get_call_insights(context_str):
    response = await litellm.acompletion(
        model="openai/gpt-4.1",
        api_key=os.getenv("OPENAI_API_KEY"),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert sales analyst. Extract key insights, objections, action items, "
                    "and any unique requirements from the following product discovery call transcript. "
                ),
            },
            {
                "role": "user",
                "content": f"Conversation:\n{context_str}",
            },
        ],
    )
    pprint(response)
    return response["choices"][0]["message"]["content"]


async def get_buying_intent(context_str):
    response = await litellm.acompletion(
        model="openai/gpt-4.1",
        api_key=os.getenv("OPENAI_API_KEY"),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a sales strategist. Analyze the following product discovery call transcript "
                    "and rate the buying intent of the lead as High, Medium, or Low. Justify your rating "
                    "with specific evidence from the conversation."
                ),
            },
            {
                "role": "user",
                "content": f"Conversation:\n{context_str}",
            },
        ],
    )
    pprint(response)
    return response["choices"][0]["message"]["content"]


async def process_call_transcript(
    transcript_file_path: str,
    prospect_data: Optional[dict] = None,
    seller_data: Optional[dict] = None,
):
    with open(transcript_file_path, "r") as f:
        raw_transcript = json.load(f)

    cleaned_conv_ctx = clean_raw_transcript(raw_transcript)

    conv_summary, conv_insights, buying_intent = await asyncio.gather(
        get_call_summary(cleaned_conv_ctx),
        get_call_insights(cleaned_conv_ctx),
        get_buying_intent(cleaned_conv_ctx),
    )

    final_call_analysis_response = {
        "conv_summary": conv_summary,
        "conv_insights": conv_insights,
        "buying_intent": buying_intent,
    }

    transcript_filename = os.path.basename(transcript_file_path)
    analysis_filename = transcript_filename.replace(".json", "_call_analysis.json")
    analysis_file_path = os.path.join("data/post_call_analysis", analysis_filename)

    with open(analysis_file_path, "w") as f:
        json.dump(final_call_analysis_response, f, indent=4)

    logging.info(f"Call analysis saved to {analysis_file_path}")


async def main():
    transcript_file_path = (
        "data/conv_history/transcript_discovery-call-test-room_2025-04-26_23-26-39.json"
    )
    await process_call_transcript(transcript_file_path)
    await litellm.aclient_session.aclose()


if __name__ == "__main__":
    asyncio.run(main())
