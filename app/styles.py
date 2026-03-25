def get_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600&display=swap');

/* ── GLOBAL ── */
html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif !important;
    background-color: #050a12 !important;
    color: #c8e0f4 !important;
}

/* Scanline overlay */
body::before {
    content: '';
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,180,255,0.012) 2px, rgba(0,180,255,0.012) 4px);
    pointer-events: none; z-index: 9999;
}

/* Grid background */
body::after {
    content: '';
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background-image: linear-gradient(rgba(0,150,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,150,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none; z-index: 0;
}

/* ── APP HEADER ── */
.stApp header { background: rgba(5,12,22,0.95) !important; border-bottom: 1px solid rgba(0,180,255,0.2) !important; }

/* ── MAIN TITLE ── */
h1 {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 28px !important; font-weight: 600 !important;
    color: #e8f4ff !important; letter-spacing: 2px !important;
}
h1::before { content: '// '; color: #00b4ff; font-family: 'Share Tech Mono', monospace; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: rgba(5,15,28,0.98) !important;
    border-right: 1px solid rgba(0,180,255,0.2) !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 11px !important; color: #00b4ff !important;
    letter-spacing: 3px !important; text-transform: uppercase !important;
}
section[data-testid="stSidebar"] h2::before { content: '// '; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: rgba(0,100,180,0.06) !important;
    border: 1px dashed rgba(0,180,255,0.3) !important;
    border-radius: 6px !important;
    transition: all 0.2s;
}
[data-testid="stFileUploader"]:hover { border-color: rgba(0,180,255,0.6) !important; }

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    animation: fadeUp 0.3s ease;
}
@keyframes fadeUp { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }

/* AI messages */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
    background: rgba(0,40,80,0.6) !important;
    border: 1px solid rgba(0,180,255,0.2) !important;
    border-radius: 8px 8px 8px 2px !important;
    padding: 12px 16px !important;
    color: #c8e0f4 !important;
    font-size: 15px !important;
    line-height: 1.65 !important;
}

/* User messages */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
    background: rgba(0,60,20,0.5) !important;
    border: 1px solid rgba(0,255,120,0.15) !important;
    border-radius: 8px 8px 2px 8px !important;
    padding: 12px 16px !important;
    color: #c8f4d8 !important;
    font-size: 15px !important;
}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] {
    background: rgba(0,30,60,0.5) !important;
    border: 1px solid rgba(0,180,255,0.25) !important;
    border-radius: 8px !important;
    color: #c8e0f4 !important;
    font-family: 'Rajdhani', sans-serif !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(0,180,255,0.6) !important;
    box-shadow: 0 0 12px rgba(0,180,255,0.1) !important;
}
[data-testid="stChatInput"] textarea { color: #c8e0f4 !important; }

/* ── BUTTONS ── */
.stButton > button {
    background: rgba(0,180,255,0.1) !important;
    border: 1px solid rgba(0,180,255,0.3) !important;
    color: #00b4ff !important;
    border-radius: 6px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 11px !important; letter-spacing: 1px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(0,180,255,0.25) !important;
    border-color: rgba(0,180,255,0.6) !important;
    box-shadow: 0 0 10px rgba(0,180,255,0.2) !important;
}

/* ── SPINNER ── */
.stSpinner { color: #00b4ff !important; }

/* ── SUCCESS / INFO ── */
.stSuccess {
    background: rgba(0,60,20,0.4) !important;
    border: 1px solid rgba(0,255,120,0.2) !important;
    color: #00ff88 !important;
    border-radius: 6px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 12px !important;
}

/* ── DIVIDER ── */
hr { border-color: rgba(0,180,255,0.15) !important; }

/* ── MARKDOWN IN SIDEBAR (scores) ── */
section[data-testid="stSidebar"] .stMarkdown p {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 12px !important; color: #a0c8e8 !important;
    line-height: 1.8 !important;
}

/* ── CAPTION ── */
.stCaption { color: #2a5a7a !important; font-family: 'Share Tech Mono', monospace !important; font-size: 11px !important; }

/* ── WARNING ── */
.stWarning {
    background: rgba(80,40,0,0.4) !important;
    border: 1px solid rgba(255,160,0,0.2) !important;
    border-radius: 6px !important;
}
</style>
"""


def reflection_card(text: str) -> str:
    """Render a [REFLECTION] block as a styled card."""
    return f"""
<div style="
    margin-top: 10px; padding: 10px 14px;
    background: rgba(80,0,120,0.2);
    border: 1px solid rgba(160,80,255,0.3);
    border-left: 3px solid #a050ff;
    border-radius: 6px;
    font-size: 13px; color: #c8a8f0;
    font-family: 'Share Tech Mono', monospace;
    line-height: 1.6;
">
    <div style="font-size:9px; letter-spacing:2px; color:#a050ff; text-transform:uppercase; margin-bottom:6px;">
        ⬡ neural reflection
    </div>
    {text}
</div>
"""


def chunk_viewer(chunks: list) -> str:
    """Render retrieved RAG chunks as a collapsible viewer."""
    ids = ", ".join([f"chunk_{i*13+12}" for i in range(len(chunks))])
    preview = chunks[0][:180] + "..." if chunks else "No chunks retrieved."
    return f"""
<details style="
    margin-top: 8px;
    border: 1px solid rgba(0,180,255,0.15);
    border-radius: 6px; overflow: hidden;
">
    <summary style="
        padding: 6px 12px;
        background: rgba(0,30,60,0.6);
        font-family: 'Share Tech Mono', monospace;
        font-size: 10px; color: #00b4ff; letter-spacing: 1px;
        cursor: pointer; list-style: none;
    ">
        <span style="background:rgba(0,180,255,0.1);border-radius:3px;padding:1px 6px;font-size:9px;margin-right:6px;">RAG</span>
        {len(chunks)} chunks retrieved · {ids}
    </summary>
    <div style="
        padding: 10px 12px;
        background: rgba(0,15,30,0.5);
        font-size: 11px; color: #6a9cbf;
        font-family: 'Share Tech Mono', monospace;
        line-height: 1.6;
    ">
        {preview}
    </div>
</details>
"""


def topic_rings(scores: dict) -> str:
    """Render topic progress rings as HTML."""
    import math
    topics = scores.get("topics", {})
    if not topics:
        return '<p style="font-family:Share Tech Mono,monospace;font-size:11px;color:#2a5a7a;">No topics scored yet.</p>'

    rings_html = ""
    for topic, data in list(topics.items())[-4:]:
        pts = data["points"]
        pct = min(int((pts / 100) * 100), 100)
        circumference = 2 * math.pi * 18
        offset = circumference * (1 - pct / 100)
        rings_html += f"""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
    <div style="position:relative;width:44px;height:44px;flex-shrink:0;">
        <svg width="44" height="44" viewBox="0 0 44 44" style="transform:rotate(-90deg);">
            <circle cx="22" cy="22" r="18" fill="none" stroke="rgba(0,180,255,0.1)" stroke-width="4"/>
            <circle cx="22" cy="22" r="18" fill="none" stroke="#00b4ff" stroke-width="4"
                stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{offset:.1f}"
                stroke-linecap="round"/>
        </svg>
        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
            font-size:9px;font-weight:600;color:#00b4ff;font-family:'Share Tech Mono',monospace;">
            {pct}%
        </div>
    </div>
    <div style="flex:1;min-width:0;">
        <div style="font-size:12px;color:#a0c8e8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{topic}</div>
        <div style="font-size:10px;color:#4a7a9b;font-family:'Share Tech Mono',monospace;">{pts} pts · {data['interactions']} interactions</div>
    </div>
</div>
"""
    return rings_html