from app.core.config import settings

def tailor_stub(resume_bullets: list[str], job_description: str) -> dict:
    tailored = []
    for b in resume_bullets:
        b = b.strip().rstrip(".")
        if not b:
            continue
        tailored.append(f"{b} (tailored to match the role keywords)")
    missing = ["Kubernetes", "CI/CD", "Model monitoring"]
    return {"tailored_bullets": tailored, "missing_skills": missing}

def tailor_openai(resume_bullets: list[str], job_description: str) -> dict:
    # We will implement this when you have a key
    raise RuntimeError("LLM provider set to openai but OPENAI_API_KEY is not configured")

def tailor_resume(resume_bullets: list[str], job_description: str) -> dict:
    if settings.llm_provider == "openai":
        return tailor_openai(resume_bullets, job_description)
    return tailor_stub(resume_bullets, job_description)
