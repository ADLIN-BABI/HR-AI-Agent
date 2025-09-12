


import os
from dotenv import load_dotenv

# ✅ Load environment variables first
load_dotenv()

import streamlit as st

# ✅ Now import backend modules (after env is loaded)
from backend import (
    parse_resume_file,
    rank_resumes_by_jd,
    extract_keyword_matches,
    generate_candidate_summary,
    get_calendar_service,
    create_event,
    list_events,
    update_event,
    delete_event,
    send_interview_email
)

# Debugging check
print("SMTP_USER:", os.getenv("SMTP_USER"))
print("SMTP_PASS:", os.getenv("SMTP_PASS"))

st.set_page_config(page_title="HR AI Agent", layout="wide")
st.title("🤖 HR AI Agent – Resume Screening & Interview Scheduler")

# --- Step 1: Input JD
jd_text = st.text_area("📌 Paste Job Description", height=200)

# --- Step 2: Upload resumes
uploaded_files = st.file_uploader(
    "📂 Upload Resumes (PDF/DOCX/TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

resumes = []
if uploaded_files and jd_text:
    for file in uploaded_files:
        path = f"temp_{file.name}"
        with open(path, "wb") as f:
            f.write(file.read())
        resumes.append(parse_resume_file(path))

    ranked = rank_resumes_by_jd(jd_text, resumes)

    st.subheader("📊 Ranked Candidates")
    for r in ranked:
        st.markdown(f"**{r['name']}** – Score: {r['score']:.2f}")
        keywords = extract_keyword_matches(jd_text, r["raw_text"])
        st.write("🔑 Matched Keywords:", ", ".join(keywords))
        with st.expander("📄 Summary"):
            summary = generate_candidate_summary(r["raw_text"], jd_text, r["name"])
            st.write(summary)

    # --- Step 3: Select candidates
    selected_names = st.multiselect(
        "✅ Select candidates for interview",
        [r["name"] for r in ranked]
    )

    # --- Step 4: Schedule interview
    if st.button("📅 Schedule Interviews"):
        if not selected_names:
            st.warning("Please select candidates first.")
        else:
            service = get_calendar_service(auth_type="oauth")
            for r in ranked:
                if r["name"] in selected_names and r["email"]:
                    event = create_event(
                        service,
                        summary="Interview",
                        description=f"Interview with {r['name']}",
                        attendees_emails=[r["email"]],
                    )
                    send_interview_email(
                        to_email=r["email"],
                        subject="Interview Invitation",
                        body=f"Dear {r['name']},\n\nWe are pleased to invite you for an interview.\nEvent Link: {event.get('htmlLink')}\n\nBest regards,\nHR Team"
                    )
            st.success("✅ Interviews scheduled and emails sent!")
