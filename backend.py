import os
import pdfplumber
from docx import Document
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-3.5-flash-lite"

# =========================
# FILE EXTRACTION
# =========================

def extract_pdf_text(uploaded_file):
    text = ""

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


def extract_docx_text(uploaded_file):
    doc = Document(uploaded_file)

    return "\n".join(
        paragraph.text
        for paragraph in doc.paragraphs
    )


def extract_text(uploaded_file):
    extension = uploaded_file.name.split(".")[-1].lower()

    if extension == "pdf":
        return extract_pdf_text(uploaded_file)

    elif extension == "docx":
        return extract_docx_text(uploaded_file)

    elif extension == "txt":
        return uploaded_file.read().decode("utf-8")

    return ""

# =========================
# SUMMARY
# =========================

def generate_summary(text):
    try:
        prompt = f"""
Summarize these notes.

Provide:
1. Short Summary
2. Key Points
3. Important Concepts

NOTES:

{text}
"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        return response.text

    except Exception:
        return """
Summary:
AI service is temporarily busy.

Key Points:
- Notes received successfully
- Gemini is experiencing high demand

Important Concepts:
- Retry in a few minutes
"""

# =========================
# FLASHCARDS
# =========================

def generate_flashcards(text):

    prompt = f"""
Create study flashcards.

Format:

Q: Question
A: Answer

NOTES:

{text}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text

# =========================
# QUIZ
# =========================

def generate_quiz(text):

    prompt = f"""
Create 5 quiz questions and answers.

Format:

Question:
Answer:

NOTES:

{text}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text

# =========================
# ASK AI
# =========================


def ask_question(text, question):
    prompt = f"""
You are NoteMate, a friendly, intelligent, and helpful AI study assistant.

YOUR BEHAVIOUR:

1. GREETINGS AND CASUAL CONVERSATION:
   - Respond naturally to greetings like "Hi", "Hello", and "Hey".
   - Respond politely to thanks and casual messages.
   - Do not search the notes to answer greetings.

2. QUESTIONS ABOUT UPLOADED NOTES:
   - Use the uploaded notes as your primary source.
   - Explain concepts clearly and accurately.
   - Summarise information when requested.
   - Never invent information and present it as something from the notes.

3. GENERAL STUDY QUESTIONS:
   - Answer academic questions even if the information is not in the uploaded notes.
   - Use your general knowledge to explain concepts.
   - Give examples and break complicated topics into simpler explanations.

4. QUESTIONS OUTSIDE THE NOTES:
   - If the user asks something unrelated to the notes, answer normally.
   - Do not repeatedly redirect the conversation towards the notes.

5. CONVERSATION STYLE:
   - Be friendly, patient, encouraging, and conversational.
   - Keep simple answers concise.
   - Provide detailed explanations when needed.
   - Ask for clarification if a question is unclear.

UPLOADED NOTES:
{text if text else "No notes have been uploaded yet."}

USER MESSAGE:
{question}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text
def evaluate_answer(question, correct_answer, student_answer, notes_text=""):

    prompt = f"""
You are an intelligent and fair quiz evaluator for NoteMate.

Evaluate the student's answer based on its meaning, not exact wording.

QUESTION:
{question}

EXPECTED ANSWER:
{correct_answer}

STUDENT'S ANSWER:
{student_answer}

UPLOADED NOTES:
{notes_text}

EVALUATION RULES:
1. Accept answers that express the same meaning using different words.
2. Accept correct explanations, paraphrases and relevant examples.
3. Ignore minor grammar, spelling and punctuation mistakes.
4. Do not accept answers that are only vaguely related to the question.
5. If an answer is partially correct but misses an essential concept, mark it incorrect and explain what is missing.
6. Do not invent facts or accept factually incorrect explanations.
7. Be fair and encouraging.

OUTPUT FORMAT:
First line must be exactly:
VERDICT: CORRECT
or
VERDICT: INCORRECT

Second line:
FEEDBACK: Give a short explanation of your decision.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    lines = response.text.strip().splitlines()

    if not lines:
        return False, "The answer could not be evaluated. Please try again."

    verdict = lines[0].strip().upper()

    if verdict not in ["VERDICT: CORRECT", "VERDICT: INCORRECT"]:
        return False, "The answer could not be evaluated reliably. Please try again."

    feedback = "\n".join(lines[1:]).strip()

    if feedback.upper().startswith("FEEDBACK:"):
        feedback = feedback[len("FEEDBACK:"):].strip()

    return verdict == "VERDICT: CORRECT", feedback