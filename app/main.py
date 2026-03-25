import streamlit as st
import tempfile
import os
import sys
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from ingestion import load_pdf, chunk_text
from embeddings import get_chroma_client, get_or_create_collection, embed_and_store, embed_query
from retrieval import retrieve_relevant_chunks
from student_agent import chat_with_student
from memory import ConversationMemory
from scoring import get_score_summary, load_scores
from styles import get_css, reflection_card, chunk_viewer, topic_rings

BASE_DIR    = _HERE
DATA_DIR    = os.path.join(BASE_DIR, "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
SCORES_FILE = os.path.join(DATA_DIR, "scores.json")
MEMORY_FILE = os.path.join(DATA_DIR, "long_term_memory.json")
CHROMA_DIR  = os.path.join(DATA_DIR, "chroma_db")

st.set_page_config(page_title="Neural Student", page_icon="🤖", layout="wide")

# Inject cyberpunk CSS
st.markdown(get_css(), unsafe_allow_html=True)

st.title("AI Student — Learn by Teaching")
st.caption("// upload a document · ai becomes a curious student · you become the teacher")

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory(max_turns=10)
if "collection" not in st.session_state:
    st.session_state.collection = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chunk_history" not in st.session_state:
    st.session_state.chunk_history = []
if "doc_loaded" not in st.session_state:
    st.session_state.doc_loaded = False
if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = 0

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")

    if uploaded_file and not st.session_state.doc_loaded:
        with st.spinner("Indexing neural memory..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            text = load_pdf(tmp_path)
            chunks = chunk_text(text)
            chroma = get_chroma_client(CHROMA_DIR)
            collection = get_or_create_collection(chroma)
            embed_and_store(chunks, collection)
            st.session_state.collection = collection
            st.session_state.doc_loaded = True
            st.session_state.chunk_count = len(chunks)
            os.unlink(tmp_path)

        st.success("// " + str(len(chunks)) + " chunks indexed")

        intro_chunks = retrieve_relevant_chunks(
            "introduction overview main topic",
            st.session_state.collection,
            embed_fn=embed_query
        )
        reply = chat_with_student(
            "Hi! I just got this document. What is it about?",
            intro_chunks,
            st.session_state.memory,
            MEMORY_FILE,
            SCORES_FILE
        )
        st.session_state.chat_history.append(("assistant", reply))
        st.session_state.chunk_history.append(intro_chunks)

    if st.session_state.doc_loaded:
        scores = load_scores(SCORES_FILE)
        total = scores.get("total_points", 0)
        level = scores.get("level", "Beginner")

        st.markdown(f"""
<div style="margin-bottom:8px;">
    <div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#00b4ff;letter-spacing:3px;text-transform:uppercase;margin-bottom:6px;">// Understanding Matrix</div>
    <div style="display:inline-flex;align-items:center;gap:6px;padding:4px 12px;background:rgba(0,180,255,0.1);border:1px solid rgba(0,180,255,0.3);border-radius:20px;font-size:11px;color:#00b4ff;font-family:'Share Tech Mono',monospace;margin-bottom:10px;">
        <div style="width:6px;height:6px;border-radius:50%;background:#00b4ff;"></div> {level.upper()}
    </div>
    <div style="font-size:28px;font-weight:600;color:#00b4ff;font-family:'Share Tech Mono',monospace;margin-bottom:4px;">
        {total} <span style="font-size:12px;color:#4a7a9b;">total pts</span>
    </div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#2a5a7a;margin-bottom:14px;">
        {st.session_state.chunk_count} chunks · {len(st.session_state.chat_history)} messages
    </div>
</div>
""", unsafe_allow_html=True)

        st.markdown(topic_rings(scores), unsafe_allow_html=True)

    st.divider()
    if st.button("⟳  Reset Session"):
        st.session_state.memory.clear()
        st.session_state.chat_history = []
        st.session_state.chunk_history = []
        st.session_state.doc_loaded = False
        st.session_state.collection = None
        st.rerun()

# ── CHAT ─────────────────────────────────────────────────────────────────────
for i, (role, msg) in enumerate(st.session_state.chat_history):
    with st.chat_message(role):
        # Separate reflection from main text
        reflection_match = re.search(r'\[REFLECTION:(.*?)\]', msg, re.DOTALL)
        clean_msg = re.sub(r'\[REFLECTION:.*?\]', '', msg, flags=re.DOTALL).strip()

        st.markdown(clean_msg)

        # Show reflection card if present
        if reflection_match:
            st.markdown(reflection_card(reflection_match.group(1).strip()), unsafe_allow_html=True)

        # Show chunk viewer for assistant messages
        if role == "assistant" and i < len(st.session_state.chunk_history):
            chunks = st.session_state.chunk_history[i]
            if chunks:
                st.markdown(chunk_viewer(chunks), unsafe_allow_html=True)

# ── INPUT ─────────────────────────────────────────────────────────────────────
user_input = st.chat_input("// teach the student something...")

if user_input:
    if not st.session_state.doc_loaded:
        st.warning("// upload a document first")
    else:
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chunk_history.append([])

        chunks = retrieve_relevant_chunks(
            user_input,
            st.session_state.collection,
            embed_fn=embed_query
        )
        with st.spinner("// processing neural context..."):
            reply = chat_with_student(
                user_input,
                chunks,
                st.session_state.memory,
                MEMORY_FILE,
                SCORES_FILE
            )

        st.session_state.chat_history.append(("assistant", reply))
        st.session_state.chunk_history.append(chunks)
        st.rerun()