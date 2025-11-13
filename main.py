
import sys
import os
from dotenv import load_dotenv
import json
from pathlib import Path
from extraction import extract_text_from_resume, clean_text
from parse import parse_resume
from question_generator import generate_questions

load_dotenv()

def main():
    print("Resume Parser Tool")
    print("=" * 40)

    
    user = input("Please enter a resume file path (.pdf, .docx, ): ").strip()
    file_path = Path(user)

    if not file_path.is_file():
        print(f"File not found: {file_path}")
        sys.exit(1)

    print(f"Found file: {file_path}")

    
    print("Extracting text from file")
    try:
        raw_text = extract_text_from_resume(str(file_path))
        print(f"Extracted {len(raw_text)} characters.")
    except Exception as e:
        print(f"Extraction failed: {e}")
        sys.exit(1)

    
    print("Cleaning text")
    cleaned_text = clean_text(raw_text)
    print(f"Cleaned text length: {len(cleaned_text)}")

    
    print("Parsing resume with AI ")
    try:
        
        
        if not os.getenv("OPENAI_API_KEY"):
            print("OPENAI_API_KEY not set in .env")
            sys.exit(1)

        parsed_data = parse_resume(cleaned_text)
        print("Parsing successful!")
    except Exception as e:
        print(f"Parsing failed: {e}")
        sys.exit(1)

    print("\nParsed Data:")
    print(json.dumps(parsed_data, indent=2))

    
    print("\nGenerating interview questions")
    try:
        questions = generate_questions(parsed_data)
        print("\nInterview Questions:")
        print("- " + "\n- ".join(questions) if isinstance(questions, list) else questions)
    except Exception as e:
        print(f"Question generation failed: {e}")

if __name__ == "__main__":
    main()
    

    