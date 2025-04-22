conversational voice agent:

- handling context for throughout the conversation
- think about adding fallback in STT and TTS models, if fallback is used then how to ensure consistency in voice
- personalized intro message:
  - use the form input to craft a personalized welcome message

pass the prospect information, prospect company info,

seller company info.


Issues / improvement scope:

- TTS model reading the markdown representation characters in middle of conversation like (**Regeneration** as `asterisks asterisks regeneration asterisks asterisks`  )
- voice is robotic, taking pauses in between, flow is not smooth
- greetings, redirecting to seller company information.

`< migrate from work email to personal email >`

Notes from other blog posts on building effective voice agents:
- voice-voice native llms abstract the 3 step process, leading to sacrifice in observability and control, although the response may come out more naturally
- stream LLM outputs to the TTS engine as they're generated.
  - cons with this approach:
    - implementation of guardrails is challenging, can only implement before or during the generation not after
    - no scope for post-processing of the llm response
  - pros:
    - less latency
    - more natural sounding voice
- Avoid unnecessary token bloat with intelligent tool arguments (for example, not passing data in prompts if it can be fetched via backend)
- consider voice cloning if planning to use fallback across different TTS service providers, single voice to be used for consistency
- design-time optimization:
  - Reduced the number of tool-invoking steps in prompts
- implement dynamic prompt injection and real-time data integration support

- ** coming the response . TTS conversation
- company registered name is used, directly like "broadcom Inc" instead of "broadcom", have to apply some filtering / input account name
  sanitization
  - close the room after the end of the conversation.

TODO:

- close the session after the conversation ends
- feature:
  - implement post processing analytics
- sanitize the account name, do not use official account name suffixes like inc, pvt. ltd etc