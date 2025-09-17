# 🤖 TalentScout – Intelligent Hiring Assistant  

An AI-powered hiring assistant for **TalentScout**, a fictional recruitment agency specializing in technology placements.  
The assistant collects **candidate information**, dynamically generates **screening questions** (based on tech stack & role), and records the **conversation logs** in a JSON database for review.  

---

## 🎯 Features
-  **Interactive Chatbot**: Greets candidates and guides them through the initial screening process.
-  **Candidate Information Collection**: Gathers full name, email, phone, years of experience, desired position, location, and   tech stack.
-  **Technical Question Generation**: Automatically generates 3–5 questions per technology listed in the candidate's tech stack.
-  **Context-Aware Flow**: One question at a time with individual answer submission, preserving conversation context.
-  **Fallback Mechanism**: Provides simulated questions when API access is unavailable.
-  **Data Storage**: Stores candidate responses and questions in a JSON file (simulated_db.json) for later review.
- **Streamlit UI**: simple user interface and expandable section as Conservation logs.

---
##  🎬 Demo Video 
https://drive.google.com/file/d/1hJWwFMnttqWmTgMapfsegaZRuH22N8r8/view?usp=sharing


---
## 🛠️ Technical Details
-  Frontend: Streamlit 
-  Backend: Python utilities (python 3.10+)
-  LLM Integration: Google Gemini AI (optional)
-  Fallback: Simulated technical questions for offline mode
-  Data Storage: Simulated JSON database (simulated_db.json)  

---

## 📂 Project Structure  

```bash
TalentScout-AI-Hiring-Assistant/
│
├── app.py # Main Streamlit app
├── utils.py # Helper functions (Gemini integration, Q&A handling)
├── prompts.py # Prompts design
├── simulated_db.json # Local JSON database (auto-created)
├── requirements.txt # Python dependencies
└── README.md # Project documentation
```
---

## 🚀 Get Strated

1. Clone the repo:
```bash
   git clone https://github.com/narayana36/TalentScout-AI-Hiring-Assistant.git
   cd TalentScout-AI-Hiring-Assistant
   ```
2. Create a virtual environment & activate:
```bash
   python -m venv venv
   source venv/bin/activate   # On Mac/Linux
   venv\Scripts\activate      # On Windows
   ```
3. Install dependencies:
```bash
   pip install -r requirements.txt
   ```
4. Set up your Gemini API Key:
   Create a .env file:
```bash 
   GEMINI_API_KEY=your_api_key_here
   ```
5. Running the App:
```bash
   streamlit run app.py
   ```

Open the local URL shown in the terminal (default: http://localhost:8501).

Enter candidate details → Answer generated screening questions → View conservation logs.

## 👨 Author 
Developed by **Narayana Reddy**
