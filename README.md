 Resume-to-Interview-Questions AIAI-powered resume parser that generates custom technical & behavioral interview questions

Built with raw Python + OpenAI API — no frameworks, no LangChain, no agents. FeaturesUpload a PDF or text resume

Extract skills, experience, and role

Generate 5 hard technical questions tailored to the candidate

Generate 4 behavioral questions focused on leadership, teamwork, and problem-solving

Return clean JSON in under 3 seconds

Perfect for:Mock interviews

Recruiters scaling screening

Self-assessment & prep

Tech StackComponent

Tech Used

PDF Parsing

PyPDF2

Text Processing

Python regex + string logic
AI Engine

openai (gpt-4o)

Output
JSON



     
[Enter resume] → [Extract text from resume] →[parse resume]->[Extract Skills/Exp] [GPT-4o: Tech Qs] → [GPT-4o: Behav Qs] → [Format JSON] 
                   
                


git clone https://github.com/opeblow/resume


pip install -r requirements.txt
 OPENAI_API_KEY="sk-..."
 
 python main.py

├── main.py              
├── parse.py             
├── extraction.py            
├── requirements.txt
├── question _generator.py        
├── sample_resume.pdf
└── README.md
|__.env
|__.gitignore

