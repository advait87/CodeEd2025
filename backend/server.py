from flask import Flask, request
import json
from google import genai
from flask_cors import CORS
from python_prompts import (
    first_question_query,
    next_question_query,
    create_report_query,
    create_coding_challenge_query,
    analyze_code_query,
    explain_module_query,
    syllabus
)
app = Flask(__name__)
CORS(app)

# Store user diagnostic journey
question_data = []


api_keys = [
    "AIzaSyByNmRtdxOJkCJXnyYQstkrhFL7sNyUT7w",
    "AIzaSyD5bnJfrrdFZ3jywcRehPVKM9iauRxU_qU",
    "AIzaSyCS7wULK5N2pMAK9Iu6a9kBDt0y_b1TEzw",
]


progress = {}


module_name = ""
# Helper function to cycle through API keys
def call_gemini_model(prompt, model="gemini-2.5-flash-lite"):
    last_error = None
    for key in api_keys:
        try:
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            if hasattr(response, 'text') and response.text:
                return response.text
        except Exception as e:
            last_error = e
            print(f"[ERROR] API key {key} failed with error: {e}")
            continue
    return f"[ERROR] All API keys failed. Last error: {str(last_error)}"


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

# question_data: [
# {
        # "question"
#         "options"
#         "student_answer"
# }
# ]

@app.route("/api/getQuestion", methods=["POST"])
def getQuestion():
    request_body = request.get_json()
    query = ""
    if len(question_data) == 0:
        query = first_question_query
    elif len(question_data) > 2:
        print("[INFO] Quiz is complete")
        return {"message": "quiz_complete"}
    else:
        formatted_data = ""
        for q in question_data:
            formatted_data += f"Question: {q['question']}\nOptions: {q['options']}\nStudent Answer: {q['student_answer']}\n\n"
        query = next_question_query.replace("{question_data}", formatted_data)


    result = call_gemini_model(query, model="gemini-2.5-flash-lite")
    return result


@app.route("/api/evaulateCode", methods=["POST"])
def evaulateCode():
    request_body = request.get_json()
    code = request_body["code"]

    result = call_gemini_model(code, model="gemini-2.5-flash-lite")
    return result


@app.route("/api/createUserReport", methods=["POST"])
def createUserReport():
    prompt = create_report_query.replace("{syllabus}", str(syllabus)).replace("{question_data}", str(question_data))
    result = call_gemini_model(prompt, model="gemini-2.5-flash-lite").replace("```json", "").replace("```python", "").replace("```", "")
    print(result)
    result = json.loads(result)
    print(result["summary"])
    global progress
    progress = result
    print(progress)
    return result["summary"]


@app.route("/api/createCodingChallenge", methods=["POST"])
def createCodingChallenge():
    prompt = create_coding_challenge_query.replace("{progress}", str(progress))
    result = call_gemini_model(prompt, model="gemini-2.5-flash-lite").replace("```json", "").replace("```python", "").replace("```", "")
    return result

code = ""
question = ""

@app.route("/api/submitCodingChallenge", methods=["POST"])
def submitCodingChallenge():
    request_body = request.get_json()
    print(request_body)
    code = request_body["code"]
    question = request_body["question"]
    print(code)
    prompt = analyze_code_query.replace("{code}", code).replace("{question}", question)
    result = call_gemini_model(prompt, model="gemini-2.5-flash-lite").replace("```json", "").replace("```python", "").replace("```", "")
    result = json.loads(result)
    if result["correct"]:
        if len(progress["remaining"]) == 0:
            result["next"] = "complete"
            return result
        progress["remaining"][0]["topics"].remove(progress["remaining"][0]["topics"][0])
        if len(progress["remaining"][0]["topics"]) == 0:
            progress["remaining"].remove(progress["remaining"][0])
            result["next"] = "module"
        else:
            result["next"] = "question"
            
    print(result)

    return result

# Get the first module from the syllabus and return the explanation
@app.route("/api/getModuleExplanation", methods=["POST"])
def getModuleExplanation():
    global module_name
    global explain_module_query
    global progress
    module_name = progress["remaining"][0]["module"]
    current_explain_module_query = explain_module_query.replace("{module_name}", module_name)
    result = call_gemini_model(current_explain_module_query, model="gemini-2.5-flash-lite").replace("```json", "").replace("```python", "").replace("```", "")
    return result



@app.route("/api/reset", methods=["POST"])
def reset():
    global question_data
    global progress
    question_data = []
    progress = ""
    return "OK"

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True)

