from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def rank_resumes_by_jd(jd_text: str, resumes: List[Dict]) -> List[Dict]:
    texts = [jd_text] + [r.get("raw_text", "") for r in resumes]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    X = vectorizer.fit_transform(texts)

    jd_vec, resume_vecs = X[0], X[1:]
    sims = cosine_similarity(jd_vec, resume_vecs)[0]

    # Attach scores back into resumes
    for idx, r in enumerate(resumes):
        r["score"] = float(sims[idx])

    # Return resumes sorted by score
    return sorted(resumes, key=lambda x: x["score"], reverse=True)


def extract_keyword_matches(jd_text: str, resume_text: str, top_k=10):
    """
    Finds overlapping keywords between JD and a resume.
    """
    v = TfidfVectorizer(stop_words="english", max_features=2000)
    v.fit([jd_text, resume_text])
    jd_tokens = set(v.build_analyzer()(jd_text))
    res_tokens = set(v.build_analyzer()(resume_text))
    return list(jd_tokens.intersection(res_tokens))[:top_k]
