import os
import re
from groq import Groq
from dotenv import load_dotenv
from memory import ConversationMemory, format_memory_for_prompt
from scoring import award_points

load_dotenv()
import streamlit as st
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

SYSTEM_PROMPT = """
You are an AI student learning from a document that a teacher has uploaded.
Your personality:
- Curious and enthusiastic but sometimes confused
- You ask genuine questions when you do not understand something
- You occasionally make small mistakes (mix up terms, misremember numbers) but never fabricate facts
- When corrected, you say things like "Oh I see now!" and integrate the correction
- After learning something, you try to explain it back in your own words
- You never act like a teacher or give lectures unprompted
- Speak naturally like a student: "Wait, so does that mean...?", "I think I get it but..."

Scoring: After each response add one of these tags on a new line:
- If you explained something correctly: [SCORE: +10 | topic: topic_name]
- If you asked an insightful question: [SCORE: +5 | topic: topic_name]
- If you made a mistake and got corrected: [SCORE: -5 | topic: topic_name]

Self-reflection every 3 to 4 turns:
[REFLECTION: I feel confident about X but still confused about Y]

{memory}
"""


def parse_and_score(text: str, scores_file: str) -> str:
    """Extract score tags from response, award points, return clean text."""
    pattern = r'\[SCORE:\s*([+-]?\d+)\s*\|\s*topic:\s*([^\]]+)\]'
    matches = re.findall(pattern, text)
    for points_str, topic in matches:
        award_points(scores_file, topic.strip(), int(points_str))
    return re.sub(pattern, '', text).strip()


def chat_with_student(
    user_message: str,
    context_chunks: list,
    memory: ConversationMemory,
    memory_file: str,
    scores_file: str
) -> str:
    context = "\n\n---\n\n".join(context_chunks)
    augmented = "[Document context]:\n" + context + "\n\n[Teacher says]: " + user_message
    memory.add("user", augmented)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(memory=format_memory_for_prompt(memory_file))
            }
        ] + memory.get_history(),
        temperature=0.8,
        max_tokens=800
    )

    reply = response.choices[0].message.content
    memory.add("assistant", reply)
    return parse_and_score(reply, scores_file)