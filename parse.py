import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def parse_resume(resume_text:str)->dict:
    """Sends the resume to OprnAI and returns a dict with:
    - skills(list)
    - experience(str,e.g "5 years")
    - education (list)
    - job_titles(list)
    """
    api_key=os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError('OPENAI_API_KEY not found in ,env')
    
    client=OpenAI(api_key=api_key)
    prompt=f"""You  are a resume parsing assistant.Extract only the following fields from the resume below and return pure JSON(no markdown,no extra text)
    Fields to extract:
    - All technical skills
    - Total years of professional experience (as a string,e.g "5 years")
    - All degrees/education entries
    - All job titles
    Resume:
    {resume_text}
"""
    try:
        response=client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role":"system","content":"Return only valid JSON"},
                {"role":"user","content":prompt}

            ],
            temperature=0,
            response_format={"type":"json_object"}
        )
        raw=response.choices[0].message.content.strip()
        json_str=re.sub(r"^```(?:json)?\s*|```$","",raw,flags=re.MULTILINE).strip()
        parsed=json.loads(json_str)
        expected={"skills","experience","education","job_titles"}
        missing=expected - parsed.keys()


        if missing:
            raise ValueError(f"Missing keys in AI output:{missing}")

        return parsed
    except json.JSONDecodeError as e:
        return {"error":"JSON decode failed","raw":raw,"exception":str(e)}
    
    except Exception as e:
        return {"error":str(e),"raw":getattr(e,"response","no response")}

    

    
    