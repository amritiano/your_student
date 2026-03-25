import streamlit as st
import tempfile
import os
import sys

# Tell Python: "look in this folder for modules"
# Must be FIRST before any local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now all local imports work cleanly
from ingestion import load_pdf, chunk_text
from  embeddings import get_chroma_client, get_or_create_collection, embed_and_store, embed_query
from retrieval import retrieve_relevant_chunks
from student_agent import chat_with_student
from memory import ConversationMemory
from scoring import get_score_summary

# Absolute paths so the app works from any launch directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

SCORES_FILE = os.path.join(DATA_DIR, "scores.json")
MEMORY_FILE = os.path.join(DATA_DIR, "long_term_memory.json")
CHROMA_DIR  = os.path.join(DATA_DIR, "chroma_db")

# ── UI ────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Student", page_icon="🎓", layout="wide")
st.title("AI Student - Learn by Teaching")
st.caption("Upload a document. The AI becomes a curious student. You become the teacher.")

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory(max_turns=10)
if "collection" not in st.session_state:
    st.session_state.collection = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "doc_loaded" not in st.session_state:
    st.session_state.doc_loaded = False

with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file and not st.session_state.doc_loaded:
        with st.spinner("Reading and indexing document..."):
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
            os.unlink(tmp_path)

        st.success("Indexed " + str(len(chunks)) + " chunks!")

        # Pass embed_query as a function so retrieval.py needs no imports
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

    st.divider()
    st.header("Understanding Score")
    st.markdown(get_score_summary(SCORES_FILE))

    if st.button("Reset Session"):
        st.session_state.memory.clear()
        st.session_state.chat_history = []
        st.session_state.doc_loaded = False
        st.session_state.collection = None
        st.rerun()

for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(msg)

user_input = st.chat_input("Explain something to the student, or answer their question...")

if user_input:
    if not st.session_state.doc_loaded:
        st.warning("Please upload a PDF first!")
    else:
        st.session_state.chat_history.append(("user", user_input))
        with st.chat_message("user"):
            st.markdown(user_input)

        # embed_query passed as a function, retrieval.py imports nothing local
        chunks = retrieve_relevant_chunks(
            user_input,
            st.session_state.collection,
            embed_fn=embed_query
        )
        with st.spinner("Student is thinking..."):
            reply = chat_with_student(
                user_input,
                chunks,
                st.session_state.memory,
                MEMORY_FILE,
                SCORES_FILE
            )
        st.session_state.chat_history.append(("assistant", reply))
        with st.chat_message("assistant"):
            st.markdown(reply)
        st.rerun()