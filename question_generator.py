
import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def generate_questions(parsed_data: dict) -> dict:
    """
    Generates 5 technical + 5 behavioral interview questions.
    Returns:
        {
            "technical": ["Q1", ...],
            "behavioral": ["Q1", ...]
        }
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env")

    client = OpenAI(api_key=api_key)
    skills = parsed_data.get("skills", [])
    experience = parsed_data.get("experience", "")
    education = parsed_data.get("education", [])
    job_titles = parsed_data.get("job_titles", [])
    summary_lines = []
    if skills:
        summary_lines.append(f"Skills: {', '.join(skills)}")
    if experience:
        summary_lines.append(f"Experience: {experience}")
    if education:
        summary_lines.append(f"Education: {', '.join(education)}")
    if job_titles:
        summary_lines.append(f"Job Titles: {', '.join(job_titles)}")
    if not summary_lines:
        return {"error": "No parsed data to generate questions from"}
    summary = "\n".join(summary_lines)
    prompt = f"""Generate interview questions for a candidate with the following profile:
{summary}
Create:
- 5 technical questions (focus on skills, tools, problem-solving)
- 5 behavioral questions (focus on experience, teamwork, challenges)
Return *only* this JSON structure:
{{
  "technical": ["question1", "question2", "question3", "question4", "question5"],
  "behavioral": ["question1", "question2", "question3", "question4", "question5"]
}}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON. No explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}  
        )
        raw = response.choices[0].message.content.strip()
        json_str = re.sub(r"^(?:json)?\s*|$", "", raw, flags=re.MULTILINE).strip()
        questions = json.loads(json_str)
        if not isinstance(questions, dict):
            raise ValueError("Root is not a dict")
        if "technical" not in questions or "behavioral" not in questions:
            raise ValueError("Missing 'technical' or 'behavioral' key")
        if not (isinstance(questions["technical"], list) and isinstance(questions["behavioral"], list)):
            raise ValueError("Questions must be lists")
        return questions
    except json.JSONDecodeError as e:
        return {"error": "Failed to parse JSON", "raw": raw, "exception": str(e)}
    except Exception as e:
        return {"error": str(e), "raw": getattr(e, "response", "no response")}

