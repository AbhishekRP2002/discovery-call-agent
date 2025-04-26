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
- sanitize the account name, do not use official account name suffixes like inc, pvt. ltd etc - DONE
- https://docs.livekit.io/agents/build/events/ : add fallbacks for stt, tts, llm service providers
- vertex-ai anthropic not working , anthropic native - Not working --> need to take a look at this



post processing / post call analysis:

1. Summary of the Call
What it is:
- A concise, objective recap of the main topics, questions, and outcomes discussed during the call.

Why it matters:

- Helps both seller and prospect quickly recall what was covered.
- Useful for sharing with team members or for CRM notes.
- Ensures alignment on next steps and what was learned.

What it typically includes:

- The prospect’s needs and pain points.
- Key product features discussed.
- Any commitments or follow-ups.
- The overall tone and outcome of the call.


2. Insights from the Call
What it is:
- Actionable observations, learnings, or patterns identified from the conversation.

Why it matters:

- Surfaces hidden opportunities or risks.
- Helps sales/CS/product teams refine their approach.
- Can inform product development or marketing.

What it typically includes:

- New pain points or requirements discovered.
- Objections or hesitations raised by the prospect.
- Unique use cases or integration needs.
- Competitive intelligence (mentions of other vendors).
- Suggestions for product improvement.


3. Buying Intent of the Lead
What it is:
- An assessment of how likely the prospect is to purchase, based on their words, questions, and behavior during the call.

Why it matters:

- Helps prioritize follow-up actions and resources.
- Informs sales forecasting and pipeline management.

What it typically includes:

- Signals of high intent: asking about pricing, implementation, timelines, or next steps.
- Signals of low intent: vague answers, lack of urgency, or focus on obstacles.
- A rating (e.g., High/Medium/Low) with supporting evidence from the transcript.


In summary:

- Summary = What happened.
- Insights = What we learned.
- Buying Intent = How likely they are to buy (and why).



**post processing tasks**
- add post processing component as part of shutdown callback
- store the sample results under data/ dir
- think about decomposition of tasks or to cater in a single task
  - need to test this
- task specific model choice?
  - summarization of call: cheaper model maybe?
  - insights: strong model
  - buying intent: strong model