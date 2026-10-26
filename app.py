from __future__ import annotations
import streamlit as st
from app.sources import load_sources, SourceDataError
from app.retrieval import retrieve, make_answer, seminar_results, CONTACT_URL
from app.llm_client import get_config, generate, MAX_CALLS_PER_SESSION

st.set_page_config(page_title="SVG Baden | Seminar & Services Assistant", page_icon="🧭", layout="wide")
st.markdown("""
<style>
.block-container{max-width:1100px;padding-top:2.2rem;padding-bottom:4rem}
.hero{padding:2.2rem 2.4rem;border-radius:22px;background:linear-gradient(125deg,#142c29,#254e46);color:white;margin:0 0 1.4rem}
.hero h1{font-size:2.35rem;line-height:1.12;margin:.35rem 0;color:white}.hero p{color:#d6e6df;font-size:1.05rem;max-width:740px}
.eyebrow{letter-spacing:.13em;text-transform:uppercase;font-size:.78rem;font-weight:700;color:#f4a27f}
.source{background:white;border:1px solid #e7e8e2;border-radius:14px;padding:1rem 1.2rem;margin:.6rem 0}
.muted{font-size:.86rem;color:#66736e}
div[data-testid="stAlert"]{border-radius:12px}
</style>
<div class="hero"><div class="eyebrow">Independent portfolio demonstration</div><h1>SVG Baden<br>Seminar & Services Assistant</h1><p>Ask questions about publicly described services and the digital occupational safety management offering. Answers are grounded in a small, attributed sample corpus.</p></div>
""", unsafe_allow_html=True)
st.warning("Demo uses public information only. Do not enter customer, employee, health, insurance, or other personal data.")
st.info("Independent portfolio demo. This is not an official SVG Baden product or service.")

try:
    sources = load_sources()
except SourceDataError as exc:
    st.error(str(exc)); st.stop()

st.subheader("Ask about services")
examples = ["What services does SVG-Baden describe?", "What does the digital work-safety management system include?", "Who can I contact in Freiburg?", "What seminars are listed?"]
cols = st.columns(len(examples))
for col, example in zip(cols, examples):
    if col.button(example, use_container_width=True):
        st.session_state["question_input"] = example
question = st.text_input("Your question", key="question_input", max_chars=500, placeholder="For example: What can the digital management system do?")

if st.button("Find an answer", type="primary", disabled=not question.strip()):
    matches = retrieve(question, sources)
    answer, no_answer = make_answer(question, matches)
    api_key, model = get_config(st.secrets if hasattr(st, "secrets") else {})
    if no_answer:
        st.session_state["answer"] = answer
        st.session_state["matches"] = []
        st.session_state["answer_mode"] = "retrieval"
    elif api_key:
        calls = st.session_state.get("llm_calls", 0)
        if calls >= MAX_CALLS_PER_SESSION:
            st.session_state["answer"] = answer + "\n\nLLM session call limit reached; showing source summaries instead."
            st.session_state["answer_mode"] = "retrieval"
        else:
            try:
                context = "\n\n".join(f"[{s['title']}] {s['text']}" for s in matches)
                st.session_state["answer"] = generate(question, context, api_key, model)
                st.session_state["llm_calls"] = calls + 1
                st.session_state["answer_mode"] = f"Grounded summary · {model}"
            except Exception as exc:
                st.session_state["answer"] = answer + f"\n\nHosted model unavailable ({exc}); showing source summaries instead."
                st.session_state["answer_mode"] = "retrieval fallback"
    else:
        st.session_state["answer"] = answer + "\n\nLLM is not configured; this answer uses retrieval-only source excerpts."
        st.session_state["answer_mode"] = "retrieval-only"
    st.session_state["matches"] = matches

if st.session_state.get("answer"):
    st.markdown("### Answer")
    st.caption(st.session_state.get("answer_mode", "Source-grounded"))
    st.markdown(st.session_state["answer"])
    for source in st.session_state.get("matches", []):
        st.markdown(f"[↗ {source['title']}]({source['url']})")

st.divider()
st.subheader("Seminars")
st.write("The official portal can show courses from several regional SVG organizations. Each course’s organizer must be checked on its own listing. The supplied portal capture contains titles, dates, and locations but does not expose provider, price, or individual course links in the saved capture, so this demo does not reproduce individual course cards.")
provider_filter = st.selectbox("Provider", ["SVG-Baden", "All providers"], index=0)
seminars = seminar_results(sources, provider_filter)
if seminars:
    for course in seminars:
        st.markdown(f"**{course['course_title']}** · {course.get('date','date not listed')} · {course.get('location','location not listed')} · {course['provider']} · {course.get('price','price not published')} · [Original listing]({course['url']})")
else:
    st.info("No individually verified course records are included in this sample corpus. Open the official portal to check current title, date, location, actual provider, price, and course link.")
st.link_button("Open the SVG Baden seminar portal", "https://www.svg-baden.de/seminar-portal")

st.divider()
st.subheader("Sources")
for source in sources:
    with st.container(border=True):
        st.markdown(f"**[{source['title']}]({source['url']})**")
        st.caption(f"Provider: {source['provider']} · Retrieved: {source['retrieved_at']}")
        st.write(source["text"][:450] + ("…" if len(source["text"]) > 450 else ""))
st.caption("Questions and answers are held only in the active app session to render this page. This demo does not write them to a database, file, or analytics service.")
