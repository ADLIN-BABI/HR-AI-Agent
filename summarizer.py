import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_candidate_summary(resume_text: str, jd_text: str, candidate_name: str = "Candidate"):
    safe_resume_text = resume_text[:3000]

    prompt = f"""
    Summarize the resume of '{candidate_name}' in relation to the job description.

    Job Description:
    {jd_text}

    Resume:
    {safe_resume_text}

    Format:
    - 4–6 sentence professional summary
    - 3 bullet points of relevant skills/experience
    - A one-line recommendation (e.g., "Strong fit", "Moderate fit", "Not a fit")
    """

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=400
        )
        return resp.choices[0].message["content"].strip()
    except Exception as e:
        return f"Summary error: {e}"



