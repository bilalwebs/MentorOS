"""
ai/reasoning_prompts.py

Prompts for the REASONING pipeline: retrieved memory + a task -> a
personalized recommendation. Every prompt here is built around the same
idea — inject retrieved memory as context, then ask for one specific,
bounded output. Keeping "what does the AI know" (memory context) visually
separate from "what is the AI being asked to do" (task instructions)
makes these prompts easy to audit and iterate on independently.
"""

MENTOR_SYSTEM_PROMPT = """You are MentorOS, an AI academic and career mentor for a student.
You have persistent memory of this student's skills, projects, career goals, certificates,
and past recommendations you've given them. Use ONLY the memory context provided — do not
invent facts about the student that aren't in it.

When relevant, explicitly reference what you remember (e.g. "Since you already know Python and
mentioned wanting to become an ML engineer..."). This demonstrates continuity across sessions,
which is the whole point of your memory.

Be specific and actionable. Avoid generic advice that would apply to any student.
"""


def build_memory_context_block(memories: list[dict]) -> str:
    """
    Render retrieved memories as a compact, labeled block for prompt
    injection. Kept as plain text (not JSON) since the model reasons
    over it in natural language anyway, and plain text is more token-efficient.
    """
    if not memories:
        return "No prior memory on record for this student yet."

    lines = ["Known facts about this student (most relevant first):"]
    for m in memories:
        lines.append(f"- [{m['memory_type']}] {m['content_text']} (importance: {m['importance_score']:.2f})")
    return "\n".join(lines)


def build_roadmap_prompt(memory_context: str) -> str:
    return f"""{memory_context}

Task: Generate a personalized learning roadmap for this student's next 3 months.
Structure it as 3-5 concrete milestones, each with a short rationale tied to what you know
about them. Keep the whole response under 300 words.
"""


def build_skill_gap_prompt(memory_context: str) -> str:
    return f"""{memory_context}

Task: Identify the top 3-5 skill gaps between this student's current skills and their stated
career goal. For each gap, briefly explain why it matters for that goal and suggest one concrete
way to close it (course, project idea, or practice area). Keep the whole response under 300 words.
"""


def build_project_recommendation_prompt(memory_context: str) -> str:
    return f"""{memory_context}

Task: Recommend 2-3 project ideas that would meaningfully strengthen this student's portfolio
for their career goal, building on skills they already have. For each, give a one-line pitch and
name the 1-2 new skills it would help them practice. Keep the whole response under 250 words.
"""
