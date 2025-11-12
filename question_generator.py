import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

def generate_questions(parsed_data):
    """Collects parsed data and generates the interview questions"""
    api_key=os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("Please set api key in the .env")
    client=OpenAI(api_key=api_key)
    skills=parsed_data.get("skills",[])
    experience=parsed_data.get("experience","")
    education=parsed_data.get("education",[])
    job_titles=parsed_data.get("job_titles",[])

    prompt=f"""
Generate interview questions for  a candidate with:
1)Skills:{",".join(skills)}
2)Experience:{experience}
3)Education:{",".join(education)}
4)Job Titles:{",".join(job_titles)}

Create 5 technical questions and 5 behavioral questions from what you collected as the parsed_data.
Return it as json:
{
    {
        "technical":["question1","question2","question3","question4","question5"],
        "behavioral":["question1","question2","question3","question4","question5"]
    }
}

"""
    try:

        res=client.chat.completions.create(
           model="gpt-4o",
           messages=[
               {"role":"system","content":"You are an AI that generates interview questions based on parsed data. Return only JSON"},
               {"role":"user","content":prompt}
          ],
          temperature=0.7

       )

        result=res.choices[0].message.content.strip()
        if result.startswith("```"):
            lines=result.split("\n")[1:-1]
            if lines and "json" in lines[0].lower():
                lines="\n".join(lines).strip()
            result=json.loads(result)

        questions=json.loads(result)

        return questions
    except Exception as e:
        return{"error":str(e)}

