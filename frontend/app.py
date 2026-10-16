
import httpx
import streamlit as st

API_BASE_URL = "http://localhost:8001/api/v1"

st.set_page_config(
    page_title="RAG Enterprise Engine",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for Hackathon Polish
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 RAG Enterprise Engine")
st.markdown("### *Production-Ready Local-First RAG with DeepSeek & pgvector*")

# Sidebar - System Status & Document Ingestion
with st.sidebar:
    st.header("⚙️ System Control")
    
    # Health Check
    try:
        health_res = httpx.get(f"{API_BASE_URL}/health", timeout=3.0)
        if health_res.status_code == 200:
            st.success("🟢 Backend & Database Online")
        else:
            st.error("🔴 Backend Degraded")
    except Exception:  # noqa: BLE001
        st.error("🔴 Backend Offline (Start FastAPI)")

    st.divider()
    st.header("📥 Knowledge Ingestion")
    
    with st.form("ingest_form"):
        doc_title = st.text_input("Document Title", placeholder="e.g. Architecture Guide")
        doc_source = st.text_input("Source / URL", placeholder="e.g. internal-wiki")
        doc_content = st.text_area("Document Content", placeholder="Paste markdown, notes, or code here...")
        submitted = st.form_submit_button("Ingest & Embed")
        
        if submitted:
            if not doc_title or not doc_content:
                st.warning("Please provide both title and content.")
            else:
                try:
                    payload = {
                        "title": doc_title,
                        "source": doc_source if doc_source else "user-upload",
                        "content": doc_content,
                    }
                    res = httpx.post(f"{API_BASE_URL}/ingest", json=payload, timeout=30.0)
                    if res.status_code == 201:
                        data = res.json()
                        st.success(f"✅ Ingested! Created {data['chunks_created']} chunks (ID: {data['document_id']})")
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:  # noqa: BLE001
                    st.error(f"Connection error: {e}")

# Main Chat Interface
st.header("💬 Enterprise AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("📚 Sources & Citations"):
                for src in message["sources"]:
                    st.markdown(f"- **{src['title']}** ({src.get('source', 'N/A')}) — Score: `{src.get('score', 0):.3f}`")

if prompt := st.chat_input("Ask a question about your ingested documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Query request with streaming
            query_payload = {
                "query": prompt,
                "top_k": 5,
                "rerank_top_k": 3,
                "stream": True,
            }
            
            with httpx.stream("POST", f"{API_BASE_URL}/query", json=query_payload, timeout=60.0) as response:
                for chunk in response.iter_text():
                    if chunk:
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:  # noqa: BLE001
            error_msg = f"Error communicating with RAG engine: {e}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
