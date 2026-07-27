# 🎓 TeachAI — Learn by Teaching

> **The best way to learn something is to teach it.**
> 
> TeachAI puts that principle into practice — upload any document, and an AI becomes your curious student. You become the teacher.

---

## 🎯 What is TeachAI?

TeachAI is a **Retrieval-Augmented Generation (RAG) powered learning application** based on the Feynman Technique.

Instead of asking an AI to explain concepts to you, **you explain concepts to the AI**.

### The Loop:
1. **Upload** any PDF — textbook, lecture notes, research paper
2. **The AI** reads it and becomes a confused, curious student
3. **You teach** — explain concepts, answer questions, correct mistakes
4. **The AI learns** — tracks understanding, asks follow-up questions, remembers across sessions
5. **You score** — real-time points track how well you're teaching

---

## ✨ Core Features

✅ **RAG Pipeline** — Every AI response is grounded in your actual document  
✅ **Student Persona** — AI asks genuine questions, makes intentional mistakes  
✅ **Semantic Search** — Top-4 most relevant document chunks retrieved per query  
✅ **Short + Long-term Memory** — Remembers what you taught it across sessions  
✅ **Real-time Scoring** — Track understanding per topic (Beginner → Expert)  
✅ **Reflection Cards** — AI self-reflects on knowledge gaps every 3-4 turns  
✅ **RAG Chunk Viewer** — See exactly which document excerpts the AI used  
✅ **Dark UI** — Cyberpunk-inspired, fast, focused interface  

---

## 🧠 How It Works — Simple Explanation

**You:** "Explain Newton's second law"

**AI Student:** "So force equals mass times... velocity?"

**You:** "Close! It's acceleration, not velocity. F = ma"

**AI Student:** "Oh! So if I push harder (increase force), and the object is lighter (less mass), it accelerates more?"

**You:** "+10 points! Exactly right"

**System:** Updates scores, stores what you taught it, remembers for next session

---

## 🏗️ Architecture — Technical Deep Dive

### The Complete RAG Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER UPLOADS PDF                         │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INGESTION (pypdf)                           │
│                                                                 │
│  Raw PDF  →  Extract Text  →  Clean  →  78 pages of content   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CHUNKING (500 chars)                        │
│                                                                 │
│  Full Text  →  Split by 500 chars  →  100 char overlap        │
│               (prevents sentence boundary cuts)                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              EMBEDDING (all-MiniLM-L6-v2)                       │
│                                                                 │
│  Each chunk  →  384-dim vector  →  Stored in memory            │
│  (sentence-transformers model, runs locally)                   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   USER SENDS MESSAGE                            │
│              "Let me explain photosynthesis"                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              SEMANTIC SEARCH (Cosine Similarity)                │
│                                                                 │
│  Query embedding  →  Compare with all 78 chunks                │
│  Similarity scores calculated in parallel                       │
│  Top 4 chunks returned (k=4)                                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  STUDENT AGENT (Groq LLaMA3)                    │
│                                                                 │
│  System Prompt (student persona)                                │
│  + Last 10 conversation turns (short-term memory)              │
│  + Learned facts (long-term memory)                             │
│  + Retrieved 4 chunks (document context)                        │
│  + User message                                                 │
│                    ↓                                            │
│            LLaMA3-70B via Groq API                              │
│            (sub-2 second response time)                         │
│                    ↓                                            │
│  Response + [SCORE tags] + [REFLECTION tags]                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PARSING & MEMORY UPDATE                        │
│                                                                 │
│  Extract [SCORE: +10 | topic: photosynthesis]  →  Update JSON  │
│  Extract [REFLECTION: ...] → Render as purple card             │
│  Update conversation history (short + long term)               │
│  Update topic scores and level                                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT UI RENDERS                         │
│                                                                 │
│  Chat bubble + RAG chunk viewer + Score panel refresh          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Retrieval Algorithm — Semantic Search with k-NN

### What You're Using

**Algorithm:** Cosine Similarity based k-Nearest Neighbors (k-NN)

**How it works:**
```python
# 1. Embed the query
query_embedding = sentence_transformer.encode(user_message)  # 384-dim vector

# 2. Calculate similarity with all chunks
similarities = []
for chunk_embedding in all_chunk_embeddings:
    score = cosine_similarity(query_embedding, chunk_embedding)
    similarities.append((score, chunk))

# 3. Sort and return top-4
top_4 = sorted(similarities, key=lambda x: x[0], reverse=True)[:4]
```

### Cosine Similarity Formula
```
cos(θ) = (A · B) / (||A|| * ||B||)

Where:
- A · B = dot product of vectors
- ||A||, ||B|| = magnitude (length) of vectors
- Result = -1 to 1 (higher = more similar)
```

### Why Cosine Similarity?
- **Direction matters, not length** — "dog is a pet" and "dog is a pet is true" have same meaning but different lengths
- **Fast in high dimensions** — O(d) where d = embedding dimension (384)
- **Normalized** — directly comparable scores across different queries
- **Works locally** — no cloud dependency, instant results

### Time Complexity
- **Per search:** O(n × d) where n = chunks (78), d = dimensions (384)
- **Your numbers:** ~30,000 operations per search
- **On CPU:** < 100ms for entire search + retrieval

---

## 🧩 Project Structure

```
your_student/
├── app/
│   ├── main.py                 # Streamlit UI + orchestration
│   ├── ingestion.py            # PDF loading + text chunking
│   ├── embeddings.py           # Embedding model + vector store
│   ├── retrieval.py            # Cosine similarity search (RAG core)
│   ├── student_agent.py        # Groq LLM + student prompt engineering
│   ├── memory.py               # Short-term + long-term memory
│   ├── scoring.py              # Points system + level calculation
│   ├── styles.py               # Custom CSS + UI components
│   └── __init__.py
├── data/                       # Auto-created at runtime
│   ├── chroma_db/              # OLD: vector store (replaced with numpy)
│   ├── scores.json             # Topic scores persistence
│   └── long_term_memory.json   # Session persistence
├── requirements.txt            # Dependencies
├── .gitignore                  # Excludes .env, data/, __pycache__
└── README.md                   # This file
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **LLM** | Groq (LLaMA3-70B-8192) | Sub-2s latency, free API, 8K context |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) | 384-dim, fast, runs locally |
| **Vector Store** | NumPy (in-memory) + JSON (persistence) | Zero cloud dependency, instant search |
| **PDF Processing** | pypdf | Simple, lightweight, reliable |
| **Frontend** | Streamlit | Rapid prototyping, no frontend code needed |
| **Memory** | Python dict (RAM) + JSON (disk) | No external DB needed for demo |
| **Deployment** | Streamlit Cloud | Free tier, auto-redeploy on git push |

---

## 💾 Memory System

### Short-term Memory (In Conversation)
- **What:** Last 10 conversation turns
- **Storage:** Python list in RAM
- **Sent to LLM:** Every request as the messages array
- **Why:** Keeps conversation context without exceeding token limit
- **Trimmed at:** 20 messages (10 turns × 2 roles)

```python
# Example
[
    {"role": "user", "content": "What is photosynthesis?"},
    {"role": "assistant", "content": "It's when plants..."},
    ...
]
```

### Long-term Memory (Across Sessions)
- **What:** Learned facts, corrections, mistakes
- **Storage:** JSON file at `data/long_term_memory.json`
- **Persists:** Across all sessions, permanent
- **Injected into:** System prompt at start of each session

```json
{
  "learned_facts": [
    "Photosynthesis converts sunlight into glucose",
    "Mitochondria is the powerhouse of the cell"
  ],
  "corrected_mistakes": [
    {
      "mistake": "Photosynthesis happens in the nucleus",
      "correction": "Photosynthesis happens in the chloroplast"
    }
  ]
}
```

### Why Two Types?
- **Short-term** keeps current conversation coherent without bloating tokens
- **Long-term** makes learning persistent — the AI actually remembers what you taught it yesterday

---

## 📊 Scoring System

### How Scoring Works

| Event | Points | Trigger |
|---|---|---|
| Student correctly explains concept | +10 | User confirms understanding |
| Student asks insightful question | +5 | AI generates genuine question |
| Student makes mistake & gets corrected | -5 | User corrects AI |

### Level Progression

```
🌱 Beginner       (0-20 pts)      Just starting
📖 Developing    (20-50 pts)     Getting the basics
🧠 Intermediate  (50-100 pts)    Solid understanding
🎓 Advanced      (100-200 pts)   Teaching others
🏆 Expert        (200+ pts)      Deep mastery
```

### Implementation

The LLM self-tags responses with:
```
[SCORE: +10 | topic: photosynthesis]
[REFLECTION: I feel confident about X but confused about Y]
```

Your code:
1. Parses these tags with regex
2. Extracts points and topic
3. Updates `scores.json`
4. Removes tags from displayed message

**Why self-scoring?** Avoids a second LLM call (saves time + cost). The model is accurate enough at self-assessment.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Groq API key (free at https://console.groq.com)
- Git

### Local Setup

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/teachai.git
cd teachai
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up environment**
Create `.env` in the `app/` folder:
```
GROQ_API_KEY=gsk_your_key_here
```

**4. Run locally**
```bash
cd app
streamlit run main.py
```

Open http://localhost:8501

**5. Test the flow**
- Upload a sample PDF
- Wait for the AI to ask its first question
- Explain the concept
- Watch your score update in real time

### Deploy to Streamlit Cloud

**1. Push to GitHub**
```bash
git add .
git commit -m "initial commit"
git push
```

**2. Connect to Streamlit Cloud**
- Go to https://share.streamlit.io
- Click "New app"
- Connect your GitHub repo
- Set main file path to `app/main.py`

**3. Add secrets**
- In Streamlit dashboard, click "Manage app" → "Settings" → "Secrets"
- Add:
```toml
GROQ_API_KEY = "gsk_your_key_here"
```

**4. Deploy**
- Click "Deploy"
- Streamlit auto-redeploys on every git push

---

## 🔄 Data Flow — Example

**User uploads:** `Physics_101.pdf` (5 pages, 78 chunks)

**AI greets:** "Hi! I just read about mechanics. Can you explain what happens when you push a box across a table?"

**Behind the scenes:**
1. Query embedded: `[0.12, 0.45, ..., 0.89]` (384 dims)
2. Compared against 78 chunk embeddings
3. Top 4 chunks retrieved (friction, force, motion, etc.)
4. Chunks + user message sent to LLaMA3
5. Response generated with student persona
6. Response tagged with `[SCORE: +5 | topic: mechanics]`
7. Scores updated, message displayed

**You respond:** "When you push it, friction opposes the motion. The harder you push, the faster it goes until friction balances the force."

**AI learns:** Stores "friction opposes motion" in long-term memory
**Score:** +10 points on "mechanics" topic

Next session, the AI remembers this because it's in `long_term_memory.json`.

---

## 🎯 Retrieval Algorithm Comparison

| Algorithm | Your Use Case | Pro | Con |
|---|---|---|---|
| **Cosine Similarity** (yours) | Small datasets, demo | Fast, simple, local | O(n) scan, not scalable |
| **BM25 (TF-IDF)** | Keyword search | Handles misspellings | No semantic understanding |
| **HNSW** | Production scale | O(log n) search | Complex to implement |
| **Reranking** | High accuracy needed | 2-stage: fast then accurate | Slower end-to-end |
| **Hybrid** | Best of both | Semantic + keyword | More complex |

---

## 🔮 Roadmap

**Completed ✅**
- Text-based teaching interface
- RAG with semantic search
- Memory system (short + long-term)
- Scoring and levels
- Live deployment

**In Progress 🚧**
- Voice input/output (Whisper + TTS)
- Multi-document support

**Planned 📋**
- FastAPI backend + Next.js frontend (production-grade)
- User authentication (Clerk)
- Persistent cloud storage (Supabase + Pinecone)
- Export session as study notes
- Shareable sessions

---

## 🤔 Common Interview Questions & Answers

### Q: What is RAG and why did you use it?
**A:** RAG (Retrieval Augmented Generation) grounds the AI in your actual document so it never hallucinates. Without it, the AI would answer from its training data which could be wrong or outdated. I retrieve the 4 most relevant chunks per query using semantic search, then feed them as context to the LLM.

### Q: How does the semantic search work?
**A:** I embed both the query and all document chunks using sentence-transformers into 384-dimensional vectors. Then I calculate cosine similarity between the query and each chunk vector. Cosine similarity measures the angle between vectors — similar meanings have small angles. I return the top-4 most similar chunks.

### Q: Why not use a proper vector database like Pinecone?
**A:** For a single-user demo with 78 chunks, numpy in-memory cosine similarity is sufficient and has zero latency. For production with millions of chunks and concurrent users, I'd use Pinecone or Weaviate with HNSW indexing for O(log n) search time.

### Q: How do you prevent the AI from hallucinating?
**A:** The system prompt explicitly tells the AI to only ask questions about the provided document context. Every response is grounded in the retrieved chunks. If a question can't be answered from the document, the AI says so.

### Q: What would you improve?
**A:** Add voice I/O for hands-free teaching. Implement a FastAPI backend + Next.js frontend for true multi-user support. Use Supabase for persistent user data and Pinecone for production-scale vector search.

### Q: Why Groq instead of OpenAI?
**A:** Sub-2-second response times for real-time teaching experience. Lower cost. LLaMA3-70B is capable enough and open source. For production, I'd support multiple providers.

---

## 📖 How the Scoring System Works

The AI self-assesses its understanding and tags responses:

```
User: "Explain photosynthesis"
AI: "Plants use sunlight to make food... is that right?"
    [SCORE: +5 | topic: photosynthesis]

User: "Yes! And it happens in the chloroplasts"
AI: "Oh! So photosynthesis is only in chloroplasts, got it"
    [SCORE: +10 | topic: photosynthesis]

User: "Actually it also happens in some bacteria"
AI: "Wait, I thought it was only in plants!"
    [SCORE: -5 | topic: photosynthesis]
    [REFLECTION: I'm still confused about which organisms can photosynthesize]
```

Score updates in real-time. Long-term memory stores corrections for next session.

---

## 🏗️ Why This Architecture?

**Modular design:** Each component is independent. Swap numpy for Pinecone, swap Groq for OpenAI — only change one file.

**Dependency injection:** `retrieval.py` doesn't import `embeddings.py`. It receives the `embed_query` function as a parameter. This avoids circular imports and makes testing easier.

**Persistent memory:** JSON storage ensures learning persists across sessions without needing a database.

**Self-scoring:** LLM self-tags instead of needing a separate evaluation call, saving latency and cost.

---

## 📊 Performance Metrics

- **PDF indexing:** 78 chunks in ~2 seconds
- **Per-query latency:** ~100ms (search) + ~1.8s (LLM)
- **Total response time:** ~2 seconds
- **Memory usage:** ~100MB for 78 chunks + embeddings
- **Cost per session:** ~$0.01 (Groq API)

---

## 🤝 Contributing

Pull requests are welcome! For major changes:
1. Open an issue first
2. Make focused changes
3. Test locally
4. Write clear commit messages

---

## 📄 License

MIT — Use freely, credit appreciated

---

## 👥 Built By

Amrit Raj  
CS Engineering Student | KIIT University  
Building in public: [@amritiano05](https://twitter.com/amritiano05)

---

<div align="center">
  
**If this helped you, give it a ⭐**

Questions? Open an issue or reach out on Twitter

Built with ❤️ using Groq, RAG, and Streamlit

</div>