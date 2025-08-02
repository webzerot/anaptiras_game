from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import json
import os

app = FastAPI()

# CORS για να συνδέεται με frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Όνομα αρχείου αποθήκευσης ερωτήσεων
QUESTIONS_FILE = "questions.json"

# Φορτώνει τις ερωτήσεις από το αρχείο
def load_questions():
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Αποθηκεύει τις ερωτήσεις στο αρχείο
def save_questions(data):
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Αρχικό φορτίο ερωτήσεων
questions = load_questions()

# Μοντέλο ερώτησης
class Question(BaseModel):
    question: str
    nsfw: bool

# GET – Τυχαία ερώτηση
@app.get("/random-question")
def get_random_question():
    if not questions:
        raise HTTPException(status_code=404, detail="Δεν υπάρχουν ερωτήσεις.")
    return random.choice(questions)

# POST – Προσθήκη νέας ερώτησης
@app.post("/add-question")
def add_question(q: Question):
    new_id = max([item["id"] for item in questions], default=0) + 1
    new_q = {
        "id": new_id,
        "question": q.question,
        "nsfw": q.nsfw
    }
    questions.append(new_q)
    save_questions(questions)
    return {"message": "Η ερώτηση προστέθηκε!", "question": new_q}

# DELETE – Διαγραφή ερώτησης με βάση το ID
@app.delete("/delete-question/{question_id}")
def delete_question(question_id: int):
    global questions
    original_length = len(questions)
    questions = [q for q in questions if q["id"] != question_id]
    
    if len(questions) == original_length:
        raise HTTPException(status_code=404, detail="Η ερώτηση δεν βρέθηκε.")
    
    save_questions(questions)
    return {"message": f"Η ερώτηση με id {question_id} διαγράφηκε."}
