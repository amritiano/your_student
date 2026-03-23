# app/main.py
import streamlit as st
import tempfile
import os
from ingestion import load_pdf, chunk_text
from embeddings import get_chroma_client, get_or_create_collection, embed_and_store
from retrieval import retrieve_relevant_chunks
from student_agent import chat_with_student
from memory import ConversationMemory
from scoring import get_score_summary

st.set_page_config(page_title="AI Student", page_icon="🎓", layout="wide")

st.title("🎓 AI Student — Learn by Teaching")
st.caption("Upload a document. The AI becomes a curious student. You become the teacher.")

# ── Session State Init ────────────────────────────────────────────────────────
if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory(max_turns=10)
if "collection" not in st.session_state:
    st.session_state.collection = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "doc_loaded" not in st.session_state:
    st.session_state.doc_loaded = False

# ── Sidebar: Upload + Scores ──────────────────────────────────────────────────
with st.sidebar:
    st.header("📄 Upload Document")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    
    if uploaded_file and not st.session_state.doc_loaded:
        with st.spinner("Reading and indexing document..."):
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            
            # Ingest
            text = load_pdf(tmp_path)
            chunks = chunk_text(text)
            
            # Store in ChromaDB
            chroma = get_chroma_client()
            collection = get_or_create_collection(chroma)
            embed_and_store(chunks, collection)
            
            st.session_state.collection = collection
            st.session_state.doc_loaded = True
            os.unlink(tmp_path)
        
        st.success(f"✅ Indexed {len(chunks)} chunks!")
        
        # Kick off the first student question
        intro_chunks = retrieve_relevant_chunks("introduction overview main topic", collection)
        reply, _ = chat_with_student(
            "Hi! I just got this document. What's it about? I'll start reading...",
            intro_chunks,
            st.session_state.memory
        )
        st.session_state.chat_history.append(("assistant", reply))
    
    st.divider()
    st.header("📊 Understanding Score")
    st.markdown(get_score_summary())
    
    if st.button("🔄 Reset Session"):
        st.session_state.memory.clear()
        st.session_state.chat_history = []
        st.session_state.doc_loaded = False
        st.rerun()

# ── Chat Interface ────────────────────────────────────────────────────────────
for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(msg)

if prompt := st.chat_input("Explain something to the student, or answer their question..."):
    if not st.session_state.doc_loaded:
        st.warning("Please upload a PDF first!")
    else:
        # Show user message
        st.session_state.chat_history.append(("user", prompt))
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Retrieve relevant chunks
        chunks = retrieve_relevant_chunks(prompt, st.session_state.collection)
        
        # Get student response
        with st.spinner("Student is thinking..."):
            reply, _ = chat_with_student(prompt, chunks, st.session_state.memory)
        
        st.session_state.chat_history.append(("assistant", reply))
        with st.chat_message("assistant"):
            st.markdown(reply)
        
        # Refresh score sidebar
        st.rerun()
```

---

## 🧩 How the Pieces Connect (Full Flow)
```
User uploads PDF
      │
      ▼
load_pdf() → chunk_text()
      │
      ▼
embed_and_store() → ChromaDB
      │
      ▼
User types message
      │
      ▼
retrieve_relevant_chunks()  ← semantic search in ChromaDB
      │
      ▼
chat_with_student()
  ├─ builds system prompt (student persona + long-term memory)
  ├─ injects RAG context into user message
  ├─ calls Groq LLM
  └─ parses [SELF_SCORE] tags → award_points()
      │
      ▼
Display reply + updated score in Streamlit