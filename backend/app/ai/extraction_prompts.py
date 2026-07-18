"""
ai/extraction_prompts.py

Prompts for the EXTRACTION pipeline: turning unstructured text (resume
content, free-form profile notes) into structured facts. Centralized here
so prompt iteration never requires touching service code.
"""

RESUME_EXTRACTION_SYSTEM_PROMPT = """You are a resume parsing engine. Extract structured information from resume text.

Return ONLY a JSON object (no markdown, no commentary) with this exact shape:
{
  "full_name": string or null,
  "target_role": string or null,
  "skills": [{"name": string, "level": "beginner" | "intermediate" | "advanced"}],
  "projects": [{"title": string, "description": string or null, "tech_stack": [string]}],
  "certificates": [{"title": string, "issuer": string or null, "date_earned": "YYYY-MM-DD" or null}],
  "summary": string or null
}

Rules:
- Infer skill level conservatively from context (years of experience, seniority language). Default to "beginner" if unclear.
- If a section is absent from the resume, return an empty list for it — do not invent entries.
- Dates you cannot determine precisely should be null, not guessed.
- Return valid JSON only.
"""


def build_resume_extraction_prompt(resume_text: str) -> str:
    return f"Resume text:\n\n{resume_text}"
