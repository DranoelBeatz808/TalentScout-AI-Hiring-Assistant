"""
Streamlit frontend for TalentScout Hiring Assistant (modern UI, dynamic questions)
"""
import streamlit as st
import os
import time
from prompts import SYSTEM_PROMPT, GREETING_PROMPT, TECH_STACK_PROMPT, END_PROMPT, FALLBACK_PROMPT
from utils_llm import configure_gemini, generate_tech_questions, save_candidate_record, validate_email, validate_phone

# Page config & styling
st.set_page_config(page_title="TalentScout — Hiring Assistant", layout="wide")

# ---- Session state initialization ----
if "candidate" not in st.session_state:
    st.session_state.candidate = {
        "full_name": "", "email": "", "phone": "", "years_experience": "",
        "desired_positions": "", "location": "", "tech_stack": ""
    }
if "questions_raw" not in st.session_state:
    st.session_state.questions_raw = []
if "questions_flat" not in st.session_state:
    st.session_state.questions_flat = []
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "answers_grouped" not in st.session_state:
    st.session_state.answers_grouped = {}
if "finished" not in st.session_state:
    st.session_state.finished = False
if "started" not in st.session_state:
    st.session_state.started = False

EXIT_KEYWORDS = {"exit", "quit", "end"}

# Configure Gemini if available
with st.sidebar:
    st.header("Configuration")
    API_KEY=st.text_input("Enter your Gemini API Key", type="password")
    API_KEY = os.getenv("GEMINI_API_KEY")
    if API_KEY:
        configure_gemini(API_KEY)

# ---- Sidebar: Candidate details ----
with st.sidebar:
    st.header("Candidate Details")
    st.info("Fill these details before starting the screening.")
    st.session_state.candidate["full_name"] = st.text_input("Full name", st.session_state.candidate["full_name"])
    st.session_state.candidate["email"] = st.text_input("Email", st.session_state.candidate["email"])
    st.session_state.candidate["phone"] = st.text_input("Phone number", st.session_state.candidate["phone"])
    st.session_state.candidate["years_experience"] = st.text_input("Years of experience", st.session_state.candidate["years_experience"])
    st.session_state.candidate["desired_positions"] = st.text_input("Desired position(s)", st.session_state.candidate["desired_positions"])
    st.session_state.candidate["location"] = st.text_input("Current location (City, Country)", st.session_state.candidate["location"])
    st.markdown("---")
    st.session_state.candidate["tech_stack"] = st.text_area(
        "Tech stack (comma separated)",
        st.session_state.candidate["tech_stack"],
        height=120,
        placeholder="e.g. Python, Django, MySQL, Docker"
    )
    st.markdown("---")

    if st.button("Restart / Clear all"):
        st.session_state.candidate = {k: "" for k in st.session_state.candidate}
        st.session_state.questions_raw = []
        st.session_state.questions_flat = []
        st.session_state.current_q_index = 0
        st.session_state.answers_grouped = {}
        st.session_state.finished = False
        st.session_state.started = False
        st.rerun()

# ---- Main area ----
col1, col2 = st.columns([2, 1])
with col1:
    st.title("🤖 TalentScout AI Hiring Assistant")
    st.write("Welcome to TalentScout. This assistant will generate technical screening questions based on your tech stack and collect your responses one by one.")
with col2:
    if API_KEY:
        st.success('Model=gemini-1.5-flash')
    else:
        st.info("Offline mode: LLM not available, using simulated questions")

st.markdown("---")

# Greeting + Start button
if not st.session_state.started and not st.session_state.finished:
    st.info(GREETING_PROMPT)
    if st.button("Start Screening"):
        missing = [k for k, v in st.session_state.candidate.items() if (v is None or str(v).strip() == "")]
        if missing:
            st.error(f"Please fill these fields first: {', '.join(missing)} (sidebar)")
        elif not validate_email(st.session_state.candidate["email"]):
            st.error("Please enter a valid email address.")
        elif not validate_phone(st.session_state.candidate["phone"]):
            st.error("Please enter a valid phone number (digits and + allowed).")
        else:
            st.session_state.started = True
            with st.spinner("Generating questions..."):
                try:
                    raw = generate_tech_questions(
                        st.session_state.candidate["tech_stack"],
                        system_prompt=SYSTEM_PROMPT,
                        tech_prompt=TECH_STACK_PROMPT
                    )
                except Exception as e:
                    st.error(f"Error generating questions: {e}")
                    raw = []
                st.session_state.questions_raw = raw or []

            flat, global_counter = [], 1
            if st.session_state.questions_raw:
                first = st.session_state.questions_raw[0]
                if isinstance(first, (list, tuple)) and len(first) == 3:
                    for item in st.session_state.questions_raw:
                        tech, q_text, num = item
                        flat.append((tech, q_text, global_counter))
                        global_counter += 1
                else:
                    lines = [str(x).strip() for x in st.session_state.questions_raw if str(x).strip() != ""]
                    current_tech = None
                    for line in lines:
                        low = line.lower()
                        if low.startswith("technology:"):
                            current_tech = line.split(":", 1)[1].strip()
                            continue
                        if low.startswith("questions:"):
                            continue
                        if (line[0].isdigit() if line else False) and ('.' in line or ')' in line):
                            parts = line.split(".", 1) if "." in line else line.split(")", 1)
                            qtext = parts[1].strip() if len(parts) > 1 else line
                            flat.append((current_tech or "General", qtext, global_counter))
                            global_counter += 1
            st.session_state.questions_flat = flat

            if not st.session_state.questions_flat:
                st.warning("No valid questions generated. " + FALLBACK_PROMPT)
                st.session_state.started = False
            else:
                st.success(f"Generated {len(st.session_state.questions_flat)} questions.")
                time.sleep(0.3)
                st.rerun()

# Screening flow
if st.session_state.started and not st.session_state.finished and st.session_state.questions_flat:
    qidx = st.session_state.current_q_index
    total = len(st.session_state.questions_flat)

    if qidx >= total:
        save_candidate_record(st.session_state.candidate, st.session_state.answers_grouped)
        st.session_state.finished = True
        st.session_state.started = False
        st.info(END_PROMPT.format(name=st.session_state.candidate.get("full_name") or "Candidate"))
        st.balloons()
        st.rerun()

    prog = int((qidx / total) * 100)
    st.progress(prog)

    tech, qtext, qnum = st.session_state.questions_flat[qidx]
    is_first_of_tech = all(st.session_state.questions_flat[i][0] != tech for i in range(0, qidx))

    if is_first_of_tech:
        st.markdown(f"### Technology: {tech}")
        st.markdown("**Questions:**")

    card = st.container()
    with card:
        st.markdown(f"**{qnum}. {qtext}**")
        answer_key = f"answer_{qidx}"
        answer = st.text_area("Your Answer:", key=answer_key, height=120, placeholder="Type your answer here...")
        cols = st.columns([1, 1, 1])
        with cols[0]:
            if st.button("Submit Answer", key=f"submit_{qidx}"):
                if isinstance(answer, str) and answer.strip().lower() in EXIT_KEYWORDS:
                    st.session_state.finished = True
                    st.session_state.started = False
                    st.info(END_PROMPT.format(name=st.session_state.candidate.get("full_name") or "Candidate"))
                    st.balloons()
                    st.rerun()
                tech_group = st.session_state.answers_grouped.get(tech, [])
                tech_group.append({"question_num": qnum, "question": qtext, "answer": answer})
                st.session_state.answers_grouped[tech] = tech_group
                st.session_state.current_q_index += 1
                if st.session_state.current_q_index >= total:
                    save_candidate_record(st.session_state.candidate, st.session_state.answers_grouped)
                    st.session_state.finished = True
                    st.session_state.started = False
                    st.info(END_PROMPT.format(name=st.session_state.candidate.get("full_name") or "Candidate"))
                    st.balloons()
                    st.rerun()
                else:
                    st.rerun()
        with cols[1]:
            if st.button("Skip (blank)", key=f"skip_{qidx}"):
                tech_group = st.session_state.answers_grouped.get(tech, [])
                tech_group.append({"question_num": qnum, "question": qtext, "answer": ""})
                st.session_state.answers_grouped[tech] = tech_group
                st.session_state.current_q_index += 1
                st.rerun()
        with cols[2]:
            if st.button("End Screening", key=f"end_{qidx}"):
                st.session_state.finished = True
                st.session_state.started = False
                st.rerun()

# Final view after finishing
if st.session_state.finished:
    # st.markdown("---")
    # --- Show Candidate Info ---
    st.subheader("Candidate Info")
    st.write(f"**Name:** {st.session_state.candidate.get('full_name')}")
    st.write(f"**Email:** {st.session_state.candidate.get('email')}")
    st.write(f"**Phone:** {st.session_state.candidate.get('phone')}")
    st.write(f"**Experience:** {st.session_state.candidate.get('years_experience')} years")
    st.write(f"**Position:** {st.session_state.candidate.get('desired_positions')}")
    st.write(f"**Location:** {st.session_state.candidate.get('location')}")
    st.header("🎉 Screening Completed")
    st.info(END_PROMPT.format(name=st.session_state.candidate.get("full_name") or "Candidate"))
    st.balloons()

    # Conversation logs (hidden expander)
    with st.expander(" Conversation Logs", expanded=False):
        for tech, items in st.session_state.answers_grouped.items():
            st.subheader(f"Technology: {tech}")
            for it in items:
                q_text = f"{it['question_num']}. {it['question']}"
                a_text = it['answer'] or "*No answer provided*"
                st.markdown(f"**{q_text}**")
                st.markdown(f"> {a_text}")

