import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def parse_resume(resume_text):
    """Extracts important details like the skills,experience and so on"""
    api_key=os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env")
    
    client=OpenAI(api_key=api_key)
    prompt=f"""
You will take a look at this resume and remove :
1)All technical skills
2)How long they have worked
3)Their education
4)Job titles

Resume:
{resume_text}

Then you will produce a JSON for me like this:
{
    {
        "skills":["skill1","skill2"],
        "experience":"x years",
        "education":["degree"],
        "job_titles":["title1"]
    }
}
"""
    try:
        res=client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role":"system","content":"Parse resume,return JSON only"},
                {"role":"user","content":prompt}
    
                
            ],
            temperature=0
        )
        result=res.choices[0].message.content.strip()

        if result.startswith("```") :
            lines=result.split("\n")[1:-1]
            if lines and lines[0].lower().startswith("json"):
                lines=lines[1:]

            result="\n".join(lines).strip()
        data=json.loads(result)
        return data

        
    except json.JSONDecodeError:
        print("Warning:Failed to parse JSON from AI response.Returning raw text")
        return {"raw_text":result}
    except Exception as e:
        print(f"Error:{e}")
        return {"error":(e)}
    
    