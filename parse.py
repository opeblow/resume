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
    prompt=f"""Extract the following information from this resume and return ONLY a JSON object with these exact keys: 
    {{
       "skills":["list of technical skills"],
       "experience":["number of years as a string,e.g. '5 years'"],
       "education":["list of degrees or education"],
       "job_titles":["list of job titles"]
    
    

    }}
    if any field is not found,use an empty list [] for lists or "Not specified" for experience
    Resume:
    {resume_text}
Return ONLY the JSON object,nothing else.
"""
    try:
        response=client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role":"system","content":"Return only valid JSON"},
                {"role":"user","content":prompt}

            ],
            temperature=0,
            
        )
        raw=response.choices[0].message.content.strip()
        json_str=re.sub(r"^```(?:json)?\s*|```$","",raw,flags=re.MULTILINE).strip()
        parsed=json.loads(json_str)

        result={
            "skills":parsed.get("skills",[]),
            "experience":parsed.get("experience","Not specified"),
            "education":parsed.get("education",[]),
            "job_titles":parsed.get("job_titles",[])

        }
        if not isinstance (result["skills"],list):
            result["skills"]=[result["skills"]] if result["skills"] else []
        if not isinstance (result["education"],list):
            result["education"]=[result["education"]] if result["education"] else []
        if not isinstance (result["job_titles"],list):
            result ["job_titles"]=[result["job_titles"]] if result["job_titles"] else []

        return result
    except json.JSONDecodeError as e:
        print(f"JSON decode error:{e}")
        print(f"Raw responsee:{raw}")
        return {
            "skills":[],
            "experience":"Not specified",
            "education":[],
            "job_titles":[],
            "error":"Failed to parse JSON"
        }
    except Exception as e :
        print(f"Error:{e}")
        return {
            "skills":[],
            "experience":"Not specified",
            "education":[],
            "job_titles":[],
            "error":str(e)
        }



    

    
    