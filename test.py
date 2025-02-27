## The Smart Study Assistant

from langchain_groq import ChatGroq
import os
import json
import random
import datetime
from kokoro.pipeline import KPipeline
import sounddevice as sd
import warnings 
import time as t
from datetime import datetime, time
from dotenv import load_dotenv
load_dotenv()

warnings.filterwarnings('ignore')

pipeline = KPipeline(lang_code='a')

def say_it(text):
    generator = pipeline(
        text=text, voice='af_heart',
        speed=1
    )
    for gs, fs, audio in generator:
        sd.play(audio, samplerate=26000)
        sd.wait()


api_key = os.getenv("CHARGOR_API")
llm = ChatGroq(model='llama-3.3-70b-versatile', api_key=api_key)

QUESTION_TYPES = ["trivia", "space", "technology", "physics", "statistics", "machine learning", "ai", 'deep learning', "computer vision"]
PREVIOUS_QUESTIONS = []

history_file = "concepts.json"

def load_history():
    global PREVIOUS_QUESTIONS
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as file:
                content = file.read().strip()
                if content:
                    data = json.loads(content)
                    PREVIOUS_QUESTIONS = [item["question"] for item in data]
                    return data
                return []
        except json.JSONDecodeError:
            print("Warning: Invalid JSON in concepts.json. Starting fresh.")
            return []
    return []

def save_history(history):
    with open(history_file, "w") as file:
        json.dump(history, file, indent=4)


def generate_question(question_type):
    previous = ", ".join(PREVIOUS_QUESTIONS) if PREVIOUS_QUESTIONS else "none yet"
    prompt = f"Hey, toss me a fun {question_type} question to learn something new today. Make it fresh and different from these: {previous}. Just the question, keep it short and chill, no hints or repeats!"
    response = llm.invoke(prompt)
    return response.content.strip()

def run_bytescolar():
    print("Hey there, welcome to ByteScolar—let's learn something cool!\n")
    history = load_history()

    question_type = random.choice(QUESTION_TYPES)
    question = generate_question(question_type)
    PREVIOUS_QUESTIONS.append(question)  # Add before using, prevents in-session repeats
    print(f"[{question_type.capitalize()}] {question}")
    say_it(f"Here's a quick one: {question}")

    user_answer = input("Your answer: ").strip()

    correct_answer_prompt = f"Check if '{user_answer}' fits '{question}'. If it's right, say 'Sweet, you nailed it!' If user say don't know the answer, give the answer"
    correct_answer = llm.invoke(correct_answer_prompt).content.strip()

    print(f"\n{correct_answer}")
    say_it(correct_answer)

    feedback = input("\nDid you like this one? (y/n): ").strip().lower()

    integration = {
        "question_type": question_type,
        "question": question,
        "answer": user_answer,
        "feedback": feedback,
        "timestamp": datetime.now().isoformat()
    }
    history.append(integration)
    save_history(history)

    if feedback == "y":
        print(f"Cool, I'll stick with {question_type} vibes next time!\n")
    else:
        print(f"No worries, I'll switch it up next time!\n")

if __name__ == "__main__":
    while datetime.now().time() < time(17, 30):
        run_bytescolar()
        t.sleep(30 * 60)