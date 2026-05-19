import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

# ----PDF-----

def create_pdf(text: str) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    width, height = letter
    y = height - 40

    for line in text.split("\n"):
        pdf.drawString(40, y, line[:100])  # prevent overflow
        y -= 15

        if y < 40:
            pdf.showPage()
            y = height - 40

    pdf.save()
    buffer.seek(0)
    return buffer.read()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NeuroSearch AI. AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ---------- Global ---------- */

html, body, [class*="css"]{
    font-family: 'Outfit', sans-serif;
    color: #ffffff;
}

.stApp{
    background:
        radial-gradient(circle at top left, rgba(0,255,200,0.15), transparent 25%),
        radial-gradient(circle at bottom right, rgba(140,82,255,0.18), transparent 25%),
        linear-gradient(135deg,#050816 0%,#0b1023 40%,#050816 100%);
    min-height: 100vh;
}

#MainMenu, footer, header{
    visibility:hidden;
}

.block-container{
    padding-top:2rem;
    max-width:1300px;
}

/* ---------- Hero ---------- */

.hero{
    text-align:center;
    padding:3rem 1rem 2rem 1rem;
}

.hero-tag{
    display:inline-block;
    padding:0.45rem 1rem;
    border:1px solid rgba(255,255,255,0.1);
    border-radius:999px;
    background:rgba(255,255,255,0.04);
    color:#00ffd5;
    font-size:0.75rem;
    letter-spacing:0.12em;
    margin-bottom:1.5rem;
    backdrop-filter:blur(10px);
}

.hero h1{
    font-size:5rem;
    font-weight:800;
    margin:0;
    line-height:1;
    letter-spacing:-3px;
    background: linear-gradient(90deg,#ffffff,#00ffd5,#8c52ff);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.hero p{
    max-width:700px;
    margin:1.5rem auto;
    color:#a7b0c0;
    font-size:1.08rem;
    line-height:1.8;
}

/* ---------- Glass cards ---------- */

.glass{
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.08);
    backdrop-filter:blur(16px);
    border-radius:24px;
    box-shadow:
        0 10px 30px rgba(0,0,0,0.35),
        inset 0 1px 1px rgba(255,255,255,0.05);
}

/* ---------- Input section ---------- */

.input-card{
    padding:2rem;
    margin-bottom:2rem;
}

/* ---------- Input ---------- */

.stTextInput input{
    background:rgba(255,255,255,0.05)!important;
    border:1px solid rgba(255,255,255,0.08)!important;
    border-radius:18px!important;
    padding:1rem!important;
    color:white!important;
    font-size:1rem!important;
}

.stTextInput input:focus{
    border:1px solid #00ffd5!important;
    box-shadow:0 0 0 1px #00ffd5!important;
}

/* ---------- Button ---------- */

.stButton button{
    width:100%;
    border:none!important;
    border-radius:18px!important;
    padding:0.95rem!important;
    font-size:1rem!important;
    font-weight:700!important;
    background:linear-gradient(90deg,#00ffd5,#8c52ff)!important;
    color:#04111d!important;
    transition:0.25s ease!important;
    box-shadow:0 10px 30px rgba(0,255,213,0.2)!important;
}

.stButton button:hover{
    transform:translateY(-3px);
    box-shadow:0 18px 40px rgba(140,82,255,0.35)!important;
}

/* ---------- Pipeline cards ---------- */

.step-card{
    position:relative;
    overflow:hidden;
    padding:1.3rem 1.5rem;
    border-radius:22px;
    margin-bottom:1rem;
    background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.07);
    transition:0.3s ease;
}

.step-card:hover{
    transform:translateY(-3px);
    border-color:rgba(0,255,213,0.4);
}

.step-card.active{
    border-color:#00ffd5;
    box-shadow:0 0 25px rgba(0,255,213,0.18);
}

.step-card.done{
    border-color:#8c52ff;
    box-shadow:0 0 25px rgba(140,82,255,0.18);
}

.step-header{
    display:flex;
    align-items:center;
    gap:0.8rem;
}

.step-num{
    background:linear-gradient(135deg,#00ffd5,#8c52ff);
    color:#04111d;
    width:34px;
    height:34px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:12px;
    font-weight:700;
    font-size:0.8rem;
}

.step-title{
    font-size:1rem;
    font-weight:600;
}

.step-status{
    margin-left:auto;
    font-size:0.75rem;
    font-weight:600;
    letter-spacing:0.08em;
}

.status-running{
    color:#00ffd5;
}

.status-done{
    color:#8c52ff;
}

.status-waiting{
    color:#667085;
}

/* ---------- Results ---------- */

.report-panel,
.feedback-panel,
.result-panel{
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:24px;
    padding:2rem;
    backdrop-filter:blur(18px);
    margin-top:1.5rem;
}

.panel-label{
    font-size:0.8rem;
    font-weight:700;
    letter-spacing:0.15em;
    margin-bottom:1rem;
    color:#00ffd5;
}

.result-content{
    color:#cfd8e3;
    line-height:1.8;
}

/* ---------- Expanders ---------- */

details{
    background:rgba(255,255,255,0.03);
    border-radius:18px;
    padding:0.6rem 1rem;
    border:1px solid rgba(255,255,255,0.06);
}

details summary{
    color:#cfd8e3!important;
    font-weight:500!important;
}

/* ---------- Footer ---------- */

.notice{
    text-align:center;
    margin-top:4rem;
    color:#6f7c91;
    font-size:0.85rem;
}

/* ---------- Scrollbar ---------- */

::-webkit-scrollbar{
    width:8px;
}

::-webkit-scrollbar-thumb{
    background:#8c52ff;
    border-radius:10px;
}

::-webkit-scrollbar-track{
    background:transparent;
}

</style>
""", unsafe_allow_html=True)


# ── Helper: render a step card ────────────────────────────────────────────────
def step_card(num: str, title: str, state: str, desc: str = ""):
    status_map = {
        "waiting": ("WAITING", "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE",   "status-done"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {"<div style='font-size:0.82rem;color:#706860;margin-top:0.3rem;'>"+desc+"</div>" if desc else ""}
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
"""
<style>
.hero-wrap {
    text-align:center;
    padding:3.5rem 2rem;
    margin-top:1rem;
    border-radius:24px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(16px);
}
.hero-title {
    font-size:4.5rem;
    font-weight:800;
    margin:1rem 0;
    line-height:1;
    letter-spacing:-2px;
    background: linear-gradient(90deg,#ffffff,#00ffd5,#8c52ff);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.hero-text {
    max-width:750px;
    margin:0 auto;
    color:#a7b0c0;
    font-size:1.1rem;
    line-height:1.8;
}
.hero-tag {
    display:inline-block;
    padding:0.4rem 1rem;
    border-radius:999px;
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.1);
    color:#00ffd5;
    font-size:0.75rem;
    letter-spacing:0.12em;
}
</style>

<div class="hero-wrap">
    <div class="hero-tag">MULTI AGENT AI SYSTEM</div>
    <div class="hero-title">NeuroResearch AI</div>
    <div class="hero-text">
        Autonomous AI agents collaborate in real-time to search, scrape, analyze, write and critique research reports.
    </div>
</div>
""",
unsafe_allow_html=True
)

# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    st.markdown("""
    <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1.5rem;">
        <span style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#605850;letter-spacing:0.1em;">TRY →</span>
    """, unsafe_allow_html=True)
    examples = ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress"]
    for ex in examples:
        st.markdown(f"""
        <span style="
            background:rgba(255,255,255,0.04);
            border:1px solid rgba(255,255,255,0.08);
            border-radius:6px;
            padding:0.25rem 0.7rem;
            font-size:0.75rem;
            color:#a09890;
            font-family:'DM Sans',sans-serif;
            cursor:default;
        ">{ex}</span>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)

    r = st.session_state.results
    done = st.session_state.done

    def s(step):
        if not r:
            return "waiting"
        steps = ["search", "reader", "writer", "critic"]
        idx = steps.index(step)
        completed = list(r.keys())
        # figure out which steps are done
        if step in r:
            return "done"
        # which step is running now (first not in r)
        if st.session_state.running:
            for i, k in enumerate(steps):
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    step_card("01", "Search Agent",  s("search"), "Gathers recent web information")
    step_card("02", "Reader Agent",  s("reader"), "Scrapes & extracts deep content")
    step_card("03", "Writer Chain",  s("writer"), "Drafts the full research report")
    step_card("04", "Critic Chain",  s("critic"), "Reviews & scores the report")


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input

    # ── Step 1: Search ──
    with st.spinner("🔍  Search Agent is working…"):
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
        })
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)
    st.rerun() if False else None   # keep inline for now

    # ── Step 2: Reader ──
    with st.spinner("📄  Reader Agent is scraping top resources…"):
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic_val}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{results['search'][:800]}"
            )]
        })
        results["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(results)

    # ── Step 3: Writer ──
    with st.spinner("✍️  Writer is drafting the report…"):
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined
        })
        st.session_state.results = dict(results)

    # ── Step 4: Critic ──
    with st.spinner("🧐  Critic is reviewing the report…"):
        results["critic"] = critic_chain.invoke({
            "report": results["writer"]
        })
        st.session_state.results = dict(results)

    st.session_state.running = False
    st.session_state.done = True
    st.rerun()


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    # Raw outputs in expanders
    if "search" in r:
        with st.expander("🔍 Search Results (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Search Agent Output</div>'
                        f'<div class="result-content">{r["search"]}</div></div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("📄 Scraped Content (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Reader Agent Output</div>'
                        f'<div class="result-content">{r["reader"]}</div></div>', unsafe_allow_html=True)

    # Final report
    if "writer" in r:
        st.markdown("""
        <div class="report-panel">
            <div class="panel-label orange">📝 Final Research Report</div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])   # render markdown natively
        st.markdown("</div>", unsafe_allow_html=True)

        # Download
        pdf_data = create_pdf(r["writer"])
        st.download_button(
            label="⬇ Download Report (PDF)",
            data=pdf_data,
            file_name=f"neurosearch_report_{int(time.time())}.pdf",
            mime="application/pdf",
        )

    # Critic feedback
    if "critic" in r:
        st.markdown("""
        <div class="feedback-panel">
            <div class="panel-label green">🧐 Critic Feedback</div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    ResearchMind · Powered by LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)