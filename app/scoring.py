# app/scoring.py
import json
import os

SCORES_FILE = "./data/scores.json"

def load_scores() -> dict:
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    return {"total_points": 0, "topics": {}, "level": "Beginner"}

def save_scores(scores: dict):
    os.makedirs("./data", exist_ok=True)
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent=2)

def award_points(topic: str, points: int, reason: str):
    """
    Award or deduct points for a topic.
    points > 0: student explained correctly
    points < 0: student made a mistake
    """
    scores = load_scores()
    
    if topic not in scores["topics"]:
        scores["topics"][topic] = {"points": 0, "interactions": 0}
    
    scores["topics"][topic]["points"] += points
    scores["topics"][topic]["points"] = max(0, scores["topics"][topic]["points"])  # floor at 0
    scores["topics"][topic]["interactions"] += 1
    scores["total_points"] = sum(t["points"] for t in scores["topics"].values())
    scores["level"] = calculate_level(scores["total_points"])
    
    save_scores(scores)
    return scores

def calculate_level(total_points: int) -> str:
    if total_points < 20:
        return "🌱 Beginner"
    elif total_points < 50:
        return "📖 Developing"
    elif total_points < 100:
        return "🧠 Intermediate"
    elif total_points < 200:
        return "🎓 Advanced"
    else:
        return "🏆 Expert"

def get_score_summary() -> str:
    scores = load_scores()
    lines = [f"**Level:** {scores['level']}  |  **Total Points:** {scores['total_points']}"]
    for topic, data in scores["topics"].items():
        bar = "█" * min(data["points"] // 5, 20)  # Visual bar
        lines.append(f"• {topic}: {data['points']} pts  {bar}")
    return "\n".join(lines)