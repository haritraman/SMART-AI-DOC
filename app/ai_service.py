import os
from google import genai

from app.models import ProjectSection, Project  # only if you need types, optional

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY is not set")

client = genai.Client(api_key=api_key)


def generate_section_content(project, section):
    doc_kind = "Word report" if project.doc_type == "docx" else "PowerPoint slide (bullet points)"

    prompt = f"""
You are helping to write a professional business {doc_kind}.

Main topic: {project.main_topic}
Section/Slide title: {section.title}

Write clear, concise content suitable for this {doc_kind}.
"""
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt.strip()
    )
    return resp.text.strip()


def refine_section_content(project, section, user_prompt: str):
    doc_kind = "Word report" if project.doc_type == "docx" else "PowerPoint slide (bullet points)"

    prompt = f"""
You are refining a specific section of a business {doc_kind}.

Main topic: {project.main_topic}
Section/Slide title: {section.title}

Current content:
\"\"\"{section.current_content or ""}\"\"\"

User refinement request:
\"\"\"{user_prompt}\"\"\"

Return ONLY the revised content.
"""
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt.strip()
    )
    return resp.text.strip()
