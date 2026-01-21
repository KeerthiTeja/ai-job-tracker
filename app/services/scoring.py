import re

STOPWORDS = {
    "the","and","or","to","of","in","a","for","with","on","as","is","are","be","an","at","by",
    "from","this","that","it","we","you","your","our"
}

def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9\-\+\.]{1,}", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) >= 3}

def score_match(job_description: str, bullets: list[str]) -> dict:
    jd_terms = tokenize(job_description)
    bullet_terms = tokenize(" ".join(bullets))

    if not jd_terms:
        return {"score": 0, "missing_keywords": []}

    covered = jd_terms.intersection(bullet_terms)
    missing = sorted(list(jd_terms - bullet_terms))[:30]

    score = int(round(100 * len(covered) / len(jd_terms)))
    return {"score": score, "missing_keywords": missing}
