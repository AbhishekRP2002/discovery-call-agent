import logging
import os
from livekit import agents
from dotenv import load_dotenv
from livekit.agents.voice import AgentSession, Agent, room_io
from livekit.agents.job import AutoSubscribe
from livekit.plugins import (
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.english import EnglishModel
from livekit.plugins.openai import LLM
from typing import Literal

from livekit.plugins.google import LLM as GeminiLLM
from prompts import VOICE_AGENT_SYSTEM_PROMPT_2
from pydantic import BaseModel, Field
from datetime import datetime
import json
import pandas as pd

load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("marklinea-voice-agent")


azure_llm = LLM.with_azure(
    model="gpt-4o",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment="gpt-4o",
    api_version="2024-12-01-preview",
)

gemini_llm = GeminiLLM(
    model="gemini-2.0-flash-001",
    api_key=os.getenv("GEMINI_API_KEY"),
    # base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    temperature=0.2,
    tool_choice="auto",
)


class UserInfo(BaseModel):
    user_first_name: str = Field(
        ...,
        description="The user's first name",
    )
    user_last_name: str = Field(
        ...,
        description="The user's last name",
    )
    user_email: str = Field(
        ...,
        description="The user's email",
    )


def get_prospect_data(user_info: UserInfo):
    # TODO: add error handling
    user_email = user_info.user_email
    df = pd.read_csv("data/contacts_dump.csv")
    prospect = df[df["Email"] == user_email].to_dict(orient="records")
    if not prospect:
        raise ValueError(f"No prospect found with email {user_email}")
    return prospect[0]


def get_seller_data():
    return {
        "seller_company_name": "Apollo.io",
        "seller_domain_knowledge": """
        1. Lead Generation & Prospecting – Finding and attracting potential customers who might be interested in your SaaS product.
        2. Creating an Ideal Customer Profile (ICP) – Defining the characteristics of the perfect customer to target marketing efforts efficiently.
        3. Content Marketing & SEO – Creating valuable content and optimizing for search engines to attract inbound leads.
        4. Paid Advertising & Demand Generation – Running targeted ads and campaigns to generate awareness and demand for the product.
        5. Email & Outreach Campaigns – Engaging potential customers with personalized emails, social outreach, and automated messaging.
        6. Lead Scoring & Nurturing – Ranking and engaging leads based on their likelihood to convert into paying customers.
        7. Sales & Marketing Alignment – Ensuring marketing efforts support sales teams with the right leads and messaging.
        8. Analytics & Performance Tracking – Measuring marketing efforts to optimize strategies and improve ROI.
        """,
        "seller_product_knowledge": """
        - Comprehensive B2B Database: Access to over 210 million contacts across 35 million companies, enabling precise targeting of potential customers. 
        - Sales Engagement Tools: Features like automated email sequencing, integrated calling, and task management streamline outreach efforts. 
        - AI-Powered Insights: Utilizes artificial intelligence to provide lead scoring, buyer intent data, and predictive analytics, helping prioritize high-potential prospects.
        - CRM Integrations: Seamlessly connects with popular CRM platforms, ensuring data consistency and enhancing workflow efficiency.
        """,
        "seller_success_stories": """
        - Cyera: By implementing Apollo.io, Cyera's BDR Leader, Andrew Froning, revamped their sales process, achieving a 75% increase in booked meetings with 50% less effort.
        - Paraform: Co-founder John Kim leveraged Apollo.io to scale outbound efforts, securing the company's first 100 customers and facilitating their seed funding round.
        - Predictable Revenue: CEO Collin Stewart transitioned to Apollo.io as an all-in-one platform, resulting in a 50% reduction in costs, doubled email open rates, and halved time to meetings.
        """,
    }


def format_sys_prompt_template(
    system_prompt, prospect_data, seller_data, scheduled_duration=30
):
    current_date_time = datetime.now().strftime("%Y-%m-%d")

    updated_system_prompt = system_prompt.format(
        seller_company_name=seller_data["seller_company_name"],
        seller_domain_knowledge=seller_data["seller_domain_knowledge"],
        seller_product_knowledge=seller_data["seller_product_knowledge"],
        seller_success_stories=seller_data["seller_success_stories"],
        scheduled_duration=scheduled_duration,
        current_date_time=current_date_time,
        prospect_name=prospect_data["Full Name"],
        prospect_company_name=prospect_data["Account Name"],
        prospect_role=prospect_data["Job Title"],
        prospect_linkedin_url=prospect_data["Contact LinkedIn URL"],
        prospect_company_description=prospect_data["Company Description"],
        prospect_recent_news=prospect_data["Company News"],
    )
    return updated_system_prompt


class DiscoveryCallAgent(Agent):
    def __init__(self, system_prompt: str = None):
        super().__init__(instructions=system_prompt)


async def entrypoint(
    ctx: agents.JobContext,
    prospect_data: dict,
    seller_data: dict,
    llm_service: Literal["azure-openai", "gemini"],
):
    logger.info(f"connecting to room {ctx.room.name}")

    # TODO: update this later to store in a db from where i can fetch later for post processing analysis
    async def write_transcript():
        curr_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"data/conv_history/transcript_{ctx.room.name}_{curr_date}.json"
        with open(file_name, "w") as f:
            json.dump(session.history.to_dict(), f, indent=4)

        logger.info(f"Transcript for room {ctx.room.name} saved to {file_name}")

    ctx.add_shutdown_callback(write_transcript)

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    system_prompt = format_sys_prompt_template(
        VOICE_AGENT_SYSTEM_PROMPT_2,
        prospect_data=prospect_data,
        seller_data=seller_data,
    )

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        # stt=assemblyai.STT(),
        llm=azure_llm if llm_service == "azure-openai" else gemini_llm,
        tts=cartesia.TTS(),
        # use LiveKit's transformer-based turn detector
        turn_detection=EnglishModel(),
        # minimum delay for endpointing, used when turn detector believes the user is done with their turn
        min_endpointing_delay=0.5,
        # maximum delay for endpointing, used when turn detector does not believe the user is done with their turn
        max_endpointing_delay=5.0,
    )

    await session.start(
        room=ctx.room,
        agent=DiscoveryCallAgent(system_prompt=system_prompt),
        room_input_options=room_io.RoomInputOptions(
            # enable background voice & noise cancellation, powered by Krisp
            # included at no additional cost with LiveKit Cloud
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Instruct the agent to speak first
    await session.generate_reply(
        instructions="greet the user with his/her first name : {}".format(
            prospect_data["Full Name"]
        )
    )


if __name__ == "__main__":
    print("Enter your first name:")
    user_first_name = input()
    print("Enter your last name:")
    user_last_name = input()
    print("Enter your email:")
    user_email = input()
    user_info = UserInfo(
        user_first_name=user_first_name,
        user_last_name=user_last_name,
        user_email=user_email,
    )
    prospect_data = get_prospect_data(user_info)
    seller_data = get_seller_data()
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=lambda ctx: entrypoint(
                ctx, prospect_data, seller_data, llm_service="gemini"
            ),
        )
    )
