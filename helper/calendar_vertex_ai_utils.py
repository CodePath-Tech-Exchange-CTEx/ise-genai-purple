import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import json
from datetime import datetime

vertexai.init(
    project="ikechukwu-mgbemele-fisk",
    location="us-central1"
)

system_instruction = """
You are a smart calendar assistant.

Your job is to extract structured event data from user input.

Rules:
- Return ONLY valid JSON.
- Do not include any explanation.
- Use this exact schema:
{
  "title": string,
  "start_date": "YYYY-MM-DD",
  "start_time": "HH:MM",
  "end_date": "YYYY-MM-DD",
  "end_time": "HH:MM"
}
- If duration is given, compute end time.
- Assume timezone America/Chicago.
- Keep titles short and clean.
"""

calendar_model = GenerativeModel(
    "gemini-2.5-flash-lite",
    system_instruction=system_instruction
)

def parse_event_with_vertex_ai(user_text: str):
    today_str = datetime.now().strftime("%Y-%m-%d (%A)")

    prompt = f"""
You extract calendar event details from user text.

IMPORTANT:
- Today's date is {today_str}.
- Use this to resolve words like "tomorrow", "next Monday", etc.

Rules:
- Return ONLY valid JSON.
- Use this exact schema:
{{
  "title": string,
  "start_date": "YYYY-MM-DD",
  "start_time": "HH:MM",
  "end_date": "YYYY-MM-DD",
  "end_time": "HH:MM"
}}
- Times must be 24-hour format.
- If duration is given, compute end time.
- Keep title short.

User text:
{user_text}
"""

    response = calendar_model.generate_content(
        prompt,
        generation_config=GenerationConfig(
            response_mime_type="application/json",
            temperature=0
        )
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]

    return json.loads(text)