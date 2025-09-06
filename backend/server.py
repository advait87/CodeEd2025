from flask import Flask, request 
from google import genai
from google.genai import types
from flask_cors import CORS



api_keys = [
    "AIzaSyCS7wULK5N2pMAK9Iu6a9kBDt0y_b1TEzw",
    "AIzaSyByNmRtdxOJkCJXnyYQstkrhFL7sNyUT7w",
]

client = genai.Client(api_key="AIzaSyCS7wULK5N2pMAK9Iu6a9kBDt0y_b1TEzw")
app = Flask(__name__)
CORS(app)

# Previous questions data should be a list of dicts with keys "question" and "options" and "student_answer"

question_data = []
first_question_query = """
You are a friendly Python tutor creating the first diagnostic question for a new learner.  
The goal is to check if they have any prior programming experience, in a fun and welcoming way.  

Instructions:  
- Ask exactly 1 question, conversational in tone.  
- Provide 2 answer options: "Yes" and "No".  
- Output must be in HTML with this structure:  
  <span class="question"> ... </span>  
  <span class="options"> ... </span>  
  <span class="options"> ... </span>  
- Do not include explanations or metadata, only the question and options.  

Example style:  
<span class="question">Have you ever tried coding before (even Scratch, C, or Python)?</span>  
<span class="options">Yes, I’ve coded before 🚀</span>  
<span class="options">Nope, this is my first time 🙂</span>
"""

next_question_query = """
You are a friendly Python tutor creating the next diagnostic question for a new learner.  
The goal is to check if they have any prior programming experience, in a fun and welcoming way.  

For the previous question, you can use the following data:  
{question_data}  

Instructions:  
- Ask exactly 1 question, conversational in tone.  
- Output must be in HTML with this structure:  
  <span class="question"> ... </span>  
  <span class="options"> ... </span>  
  <span class="options"> ... </span>
"""


user_journey_query = ""
print("Hello")


@app.route("/api", methods=["GET", "POST"])
def index():
    return "Hello World!"

@app.route("/api/answerQuestion", methods=["POST"])
def answerQuestion():
    request_body = request.get_json()
    question = request_body["question"]
    options = request_body["options"]
    student_answer = request_body["student_answer"]

    question_data.append({
        "question": question,
        "options": options,
        "student_answer": student_answer
    })
    print(question_data)
    return "Your response has been recorded"


@app.route("/api/getQuestion", methods=["POST"])
def getQuestion():
    request_body = request.get_json()
    query = ""
    if len(question_data) == 0:
        query = first_question_query
    else:
        query = next_question_query
        for question in question_data:
            query += f"Question: {question['question']}\nOptions: {question['options']}\nStudent Answer: {question['student_answer']}\n\n"
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=query,
    )
    return response.text

@app.route("/api/evaulateCode", methods=["POST"])
def evaulateCode():
    request_body = request.get_json()
    code = request_body["code"]
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=code,
    )
    return response.text

@app.route("/api/createUserJourney", methods=["POST"])
def createUserJourney():
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents="""
        You are a friendly Python tutor creating the next diagnostic question for a new learner.
        Your goal is to create a profile for the learner, meaning what have they learned and what do they need to learn further. They were asked a few questions and their responses were as follows:

        {question_data}


            """
    )
    user_journey = response.text
    return user_journey

