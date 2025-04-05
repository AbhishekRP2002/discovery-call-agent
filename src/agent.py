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
from prompts import VOICE_AGENT_SYSTEM_PROMPT_2

load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")


azure_llm = LLM.with_azure(
    model="gpt-4o",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment="gpt-4o",
    api_version="2024-12-01-preview",
)


class DiscoveryCallAgent(Agent):
    def __init__(self):
        super().__init__(instructions=VOICE_AGENT_SYSTEM_PROMPT_2)


async def entrypoint(ctx: agents.JobContext):
    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        # stt=assemblyai.STT(),
        llm=azure_llm,
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
        agent=DiscoveryCallAgent(),
        room_input_options=room_io.RoomInputOptions(
            # enable background voice & noise cancellation, powered by Krisp
            # included at no additional cost with LiveKit Cloud
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Instruct the agent to speak first
    await session.generate_reply()


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
