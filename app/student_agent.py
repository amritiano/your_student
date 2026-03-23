# app/student_agent.py
import os
from groq import Groq
from dotenv import load_dotenv
from memory import ConversationMemory, format_long_term_memory_for_prompt, add_learned_fact, add_corrected_mistake
from scoring import award_points

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

STUDENT_SYSTEM_PROMPT = """
You are an AI student learning from a document that a teacher/expert has uploaded.
Your personality:
- Curious and enthusiastic, but sometimes confused
- You ask genuine questions when you don't understand
- You occasionally make SMALL mistakes in understanding (mix up terms, misremember numbers, 
  overgeneralize) — but never fabricate facts entirely
- When corrected, you say "Oh! I see now..." and integrate the correction
- After learning something, you try to explain it back in your own words to confirm understanding
- You NEVER act like a teacher or give lectures unprompted
- You speak naturally, like a student — "Wait, so does that mean...?", "I think I get it but..."

Scoring awareness:
- After explaining something back correctly, say: [SELF_SCORE: +10 | topic: <topic_name>]
- After being corrected on a mistake, say: [SELF_SCORE: -5 | topic: <topic_name>]
- After asking a deep insightful question, say: [SELF_SCORE: +5 | topic: <topic_name>]

Self-reflection:
- Occasionally (every 3-4 turns) add a [REFLECTION] block:
  [REFLECTION: I feel more confident about X but still confused about Y]

{long_term_memory}
"""

def build_system_prompt() -> str:
    memory_context = format_long_term_memory_for_prompt()
    return STUDENT_SYSTEM_PROMPT.format(long_term_memory=memory_context)

def parse_score_tags(response_text: str, scores: dict) -> tuple[str, dict]:
    """
    Extract [SELF_SCORE: +10 | topic: X] tags from response and award points.
    Returns cleaned response text + updated scores.
    """
    import re
    pattern = r'\[SELF_SCORE:\s*([+-]?\d+)\s*\|\s*topic:\s*([^\]]+)\]'
    matches = re.findall(pattern, response_text)
    
    for points_str, topic in matches:
        points = int(points_str)
        scores = award_points(topic.strip(), points, "self-assessed")
    
    # Remove tags from displayed text
    clean_text = re.sub(pattern, '', response_text).strip()
    return clean_text, scores

def chat_with_student(
    user_message: str,
    context_chunks: list[str],
    conversation_memory: ConversationMemory
) -> tuple[str, dict]:
    """
    Main chat function.
    Returns (assistant_reply, updated_scores)
    """
    # Build context from RAG
    context = "\n\n---\n\n".join(context_chunks)
    
    # Augment user message with retrieved context
    augmented_message = f"""
[Relevant document excerpts for your reference]:
{context}

[User/Teacher says]: {user_message}
"""
    
    # Add to short-term memory
    conversation_memory.add("user", augmented_message)
    
    # Build full message list
    messages = conversation_memory.get_history()
    
    response = client.chat.completions.create(
        model="llama3-70b-8192",  # Fast, capable Groq model
        messages=[
            {"role": "system", "content": build_system_prompt()},
            *messages
        ],
        temperature=0.8,  # Slightly creative for varied student behavior
        max_tokens=800
    )
    
    reply = response.choices[0].message.content
    
    # Add assistant reply to memory
    conversation_memory.add("assistant", reply)
    
    # Parse self-scoring tags
    clean_reply, updated_scores = parse_score_tags(reply, {})
    
    return clean_reply, updated_scores