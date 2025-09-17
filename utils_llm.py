# utils.py
import re
import os
import json
import random
import google.generativeai as genai


def configure_gemini(api_key):
    if not api_key:
        return
    genai.configure(api_key=api_key)


def generate_tech_questions(tech_stack, system_prompt, tech_prompt):
    """Generate technical questions using Gemini API dynamically based on tech stack and experience."""
    tech_stack_clean = tech_stack.strip()
    if not tech_stack_clean:
        return []

    instructions = tech_prompt.format(tech_stack=tech_stack_clean)

    if genai:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"{system_prompt}\n\nUser: {instructions}"

        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1024
                )
            )
            # Extract text
            text = getattr(response, "text", None) or \
                   (response.candidates[0].content if hasattr(response, 'candidates') else None)
            if text:
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                return lines
        except Exception as e:
            print("Error generating questions via Gemini:", e)
            return []

    # Fallback empty list if API fails
    return _simulate_questions(tech_stack_clean)


def _simulate_questions(tech_stack):
    """
    Generate more realistic screening questions for each technology.
    Instead of repeating same patterns, pick from a pool of conceptual, coding, and scenario-based templates.
    """
    techs = [t.strip() for t in re.split(r'[;,\n]', tech_stack) if t.strip()]
    results = []
    q_counter = 1

    question_bank = {
        "python": [
            "Write a Python function to check if a number is prime.",
            "What is the difference between a list, tuple, and set in Python?",
            "How would you handle a very large dataset (e.g., 10GB CSV) in Python?",
            "Explain list comprehension with an example.",
            "What is the difference between deep copy and shallow copy?"
        ],
        "mysql": [
            "Write a SQL query to fetch the second highest salary from an employees table.",
            "Explain the difference between INNER JOIN and LEFT JOIN with an example.",
            "What are indexes in MySQL? When should you avoid them?",
            "How would you design a schema for storing chatbot candidate data?",
            "Write a query to count how many candidates have more than 3 years of experience."
        ],
        "machine learning": [
            "What is the difference between supervised and unsupervised learning?",
            "What is overfitting, and how do you prevent it?",
            "Explain bias vs variance with an example.",
            "What’s the difference between classification and regression problems?",
            "Name three common evaluation metrics for ML models."
        ],
        "langchain": [
            "What is LangChain and why is it useful?",
            "How would you use LangChain to build a chatbot with memory?",
            "What are PromptTemplates in LangChain, and why are they important?",
            "Explain the difference between RAG (retrieval-augmented generation) and fine-tuning.",
            "Give an example use case where LangChain would be better than using OpenAI API directly."
        ]
    }

    for tech in techs:
        key = tech.lower()
        pool = question_bank.get(key, [
            f"What is {tech}?",
            f"Explain a real-world use case of {tech}.",
            f"How would you apply {tech} in a project?"
        ])

        # Pick 3–5 unique random questions
        selected = random.sample(pool, min(len(pool), random.randint(3, 5)))

        for q in selected:
            results.append((tech, q, q_counter))
            q_counter += 1

    return results



def save_candidate_record(candidate, answers, storage_path = "simulated_db.json"):
    """Save candidate details and Q&A to JSON file."""
    record = candidate.copy()
    record["screening_answers"] = answers

    if os.path.exists(storage_path):
        with open(storage_path, "r") as f:
            try:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
            except Exception:
                data = []
    else:
        data = []

    data.append(record)
    with open(storage_path, "w") as f:
        json.dump(data, f, indent=2)


def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    pattern = r'^[\d\+\-\s]+$'
    return re.match(pattern, phone) is not None
