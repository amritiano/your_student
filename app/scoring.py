import json
import os


def load_scores(scores_file: str) -> dict:
    if os.path.exists(scores_file):
        with open(scores_file, "r") as f:
            return json.load(f)
    return {"total_points": 0, "topics": {}, "level": "Beginner"}


def save_scores(scores_file: str, scores: dict):
    with open(scores_file, "w") as f:
        json.dump(scores, f, indent=2)


def award_points(scores_file: str, topic: str, points: int) -> dict:
    scores = load_scores(scores_file)
    if topic not in scores["topics"]:
        scores["topics"][topic] = {"points": 0, "interactions": 0}
    scores["topics"][topic]["points"] = max(0, scores["topics"][topic]["points"] + points)
    scores["topics"][topic]["interactions"] += 1
    scores["total_points"] = sum(t["points"] for t in scores["topics"].values())
    total = scores["total_points"]
    if total < 20:
        scores["level"] = "Beginner"
    elif total < 50:
        scores["level"] = "Developing"
    elif total < 100:
        scores["level"] = "Intermediate"
    elif total < 200:
        scores["level"] = "Advanced"
    else:
        scores["level"] = "Expert"
    save_scores(scores_file, scores)
    return scores


def get_score_summary(scores_file: str) -> str:
    scores = load_scores(scores_file)
    lines = ["**Level:** " + scores["level"] + "  |  **Total Points:** " + str(scores["total_points"])]
    for topic, data in scores["topics"].items():
        bar = "█" * min(data["points"] // 5, 20)
        lines.append("- " + topic + ": " + str(data["points"]) + " pts  " + bar)
    if len(lines) == 1:
        lines.append("No topics scored yet. Start teaching!")
    return "\n".join(lines)