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
    turn_detector,
)
from livekit.plugins.openai import LLM
from typing import Literal

from livekit.plugins.google import LLM as GeminiLLM
from prompts import VOICE_AGENT_SYSTEM_PROMPT_2
from pydantic import BaseModel, Field

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


def get_prospect_data(user_email: str):
    pass


def get_seller_data():
    pass


def format_sys_prompt_template(system_prompt, prospect_data, seller_data):
    pass


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
        turn_detection=turn_detector.EOUModel(),
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
        "greet the user with his first name (if available) and use the ACE method for kicking off the discovery call"
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
    prospect_data = get_prospect_data(user_email)
    seller_data = get_seller_data()
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=lambda ctx: entrypoint(
                ctx, prospect_data, seller_data, llm_service="azure-openai"
            ),
        )
    )
