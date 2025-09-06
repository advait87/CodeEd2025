from flask import Flask, request
import json
from google import genai
from flask_cors import CORS

# List of API keys to cycle through
api_keys = [
    "AIzaSyByNmRtdxOJkCJXnyYQstkrhFL7sNyUT7w",
    "AIzaSyD5bnJfrrdFZ3jywcRehPVKM9iauRxU_qU",
    "AIzaSyCS7wULK5N2pMAK9Iu6a9kBDt0y_b1TEzw",
]

app = Flask(__name__)
CORS(app)

# Store user diagnostic journey
question_data = []

# Static prompt templates
first_question_query = """
You are a friendly Python tutor creating the first diagnostic question for a new learner. 

The goal is to check if they have any prior programming experience, in a fun and welcoming way. 



Instructions: 

Ask exactly 1 question, conversational in tone. 

Provide 2 answer options: "Yes" and "No" (strictly "Yes" or "No") . 

Output must be in HTML with this structure: 

 <span class="question"> ... </span> 

 <span class="options"> ... </span> 

 <span class="options"> ... </span> 

Do not include explanations or metadata, only the question and options. 



Example style: 

<span class="question">Have you ever tried coding before (even Scratch, C, or Python)?</span> 

<span class="options">Yes</span> 

<span class="options">No</span>

"""

next_question_query = """
You are a Python tutor running an adaptive diagnostic quiz.
Your goal is to find the learner’s programming level as quickly and accurately as possible.

# Context of the quiz so far:
{question_data}


# Instructions:
- The next question should be adaptive:
  - If the answer to the first question was "Yes" then the nature of the questions should be highly technical, difficulty level should be moderate; AND if the answer to the first question was "No" then the nature of the questions should be beginner friendly, difficulty level should be easy.
  - If previous answers were correct → ask a slightly harder one.  
  - If previous answers were wrong → ask a simpler one to check basics again.  
- Keep the language *plain, simple, and friendly*.  
- Only ask *one question at a time*.  


# Output Format:
If asking a new question, output strictly in HTML spans:
<span class="question">Your question here</span>  
<span class="options">Option A</span>  
<span class="options">Option B</span>  
<span class="options">Option C</span>  
<span class="options">Option D</span>  

"""

syllabus = {
    "Introduction": [
        "What is Programming?",
        "What is Python?",
        "Features of Python"
    ],
    "Comments": [
        "Comments",
        "Types of Comments",
        "Using Python as a Calculator"
    ],
    "Variables and Datatypes": [
        "Data Types",
        "Rules for Choosing an Identifier",
        "Operators in Python",
        "type() function and Typecasting",
        "input() Function"
    ],
    "Strings": [
        "String Slicing",
        "Slicing with Skip Value",
        "String Functions",
        "Escape Sequence Characters"
    ],
    "Lists and Tuples": [
        "List Indexing",
        "List Methods",
        "Tuples in Python",
        "Tuple Methods"
    ],
    "Dictionaries and Sets": [
        "Properties of Python Dictionaries",
        "Dictionary Methods",
        "Sets in Python",
        "Properties of Sets",
        "Operations on Sets"
    ],
    "Conditional Expressions": [
        "If, Else and Elif in Python",
        "Relational Operators",
        "Logical Operators",
        "Elif Clause"
    ],
    "Loops in Python": [
        "Types of Loops",
        "While Loop",
        "For Loop",
        "range() Function",
        "For Loop with Else",
        "Break Statement",
        "Continue Statement",
        "Pass Statement"
    ],
    "Functions and Recursion": [
        "Function Syntax and Example",
        "Function Call",
        "Function Definition",
        "Types of Functions",
        "Functions with Arguments",
        "Default Parameter Values",
        "Recursion"
    ],
    "File I/O": [
        "Types of Files",
        "Opening a File",
        "Reading a File",
        "Other Methods to Read Files",
        "Modes of Opening Files",
        "Writing Files in Python",
        "With Statement"
    ],
    "Object Oriented Programming": [
        "Class",
        "Object",
        "Modelling a Problem in OOP",
        "Class Attributes",
        "Instance Attributes",
        "self Parameter",
        "Static Method",
        "__init__ Constructor"
    ],
    "Inheritance & Advanced OOP": [
        "Types of Inheritance",
        "Single Inheritance",
        "Multiple Inheritance",
        "Multilevel Inheritance",
        "super() Method",
        "Class Method",
        "@property Decorator",
        "Getters and Setters",
        "Operator Overloading"
    ],
    "Advanced Python 1": [
        "New Features in Python",
        "Walrus Operator",
        "Type Definitions",
        "Advanced Type Hints",
        "Match Case",
        "Dictionary Merge & Update Operators",
        "Exception Handling",
        "Raising Exceptions",
        "try-else Clause",
        "try-finally",
        "if __name__ == '__main__'",
        "Global Keyword",
        "enumerate() Function",
        "List Comprehensions"
    ],
    "Advanced Python 2": [
        "Lambda Functions",
        "join() Method (Strings)",
        "format() Method (Strings)",
        "Map, Filter & Reduce"
    ],
    # Additional Useful Modules
    "Error Handling & Debugging": [
        "Debugging Techniques",
        "Using PDB",
        "Common Errors and Fixes",
        "Assertions"
    ],
    "Python Libraries Overview": [
        "NumPy Basics",
        "Pandas Basics",
        "Matplotlib Basics"
    ],
    "Data Handling & Processing": [
        "Reading CSV/Excel Files",
        "Data Cleaning",
        "Basic Data Visualization"
    ]
}
create_report_query = """
You are an expert Python tutor. Your task is to generate a mastery report for a learner who has just completed a short, adaptive diagnostic quiz. Your report must provide a clear assessment of their proficiency and a summary of their strengths and weaknesses. Base your analysis only on the provided quiz data and syllabus.

Generate a Python mastery report based on a learner's quiz data and a provided syllabus.

The report should assess their proficiency, summarize strengths and weaknesses, and list topics they've understood and those they still need to master.


Syllabus: A dictionary of Python modules and their corresponding topics. The modules are ordered by increasing advancement:
{syllabus}

The user answered a python quiz, and the data is as following

{question_data}


Instructions
Analyze and Map:

Infer the correctness of each answer by comparing the learner's response to the correct answer.

Map each question to one or more topics from the syllabus. For example:

A question about the purpose of type() maps to "Variables and Datatypes", specifically "type()".

A question on dictionary creation maps to "Dictionaries and Sets", specifically "Dict Properties".

Determine Mastery:

Mark a topic as "understood" if the learner answered all related questions correctly.

Mark a topic as "not_understood" if the learner missed even one related question.

Be Conservative: If a foundational topic (e.g., "Variables") is not understood, assume that all advanced topics that depend on it (e.g., "OOP") are also not understood, even if no questions were asked about them.

Structure the Output:

Provide the output as a JSON dictionary with the following keys:

"remaining": A list of dictionaries, where each dictionary contains a "module" name and a list of "topics" that need more work.

"understood": A list of strings, where each string is the name of a module the learner has mastered.

"summary": A concise, plain-English summary of the learner's strengths and areas for improvement.

Ordering: The modules and topics within both the "understood" and "remaining" lists must be sorted in order of increasing advancement, matching the order in the provided syllabus.

Example Output Format:
{
    "understood": [ "Introduction to Programming", "Variables and Datatypes" ],
    "remaining": [
        { "module": "Variables and Datatypes", "topics": ["Operators", "input()"] },
        { "module": "Strings", "topics": ["Slicing", "String Functions"] }
    ],
    "summary": "The learner has a solid grasp of basic Python concepts and variable identification but struggles with operators and string manipulation."
}
"""


progress = {}

create_coding_challenge_query = """
You are a Python tutor guiding a learner through short, focused micro-learning steps.  
The learner’s progress report is:

{progress}

# Instructions:
- From "remaining", pick one topic the learner has not yet mastered.  
- Then ask exactly ONE practice question**:
- A coding challenge to practice the topic.
- Keep it conversational and fun.  
- Never ask more than one question at a time.  
- Keep tone encouraging (like a coach).
- Output format must be:  

use strong tags or similar tags when necessary. DO NOT USE MARKDOWN.
use code tags for code examples.
Give proper spacing between sections.

output format:
<span class="question">Your practice question here</span>


"""


analyze_code_query = """

You are a Python tutor analyzing a student's code. The student has to solve the given coding challenge.

{question}

The student's code is:

{code}

# Instructions:
- Analyze the code and provide feedback in a structured format.  
- The output should be a json object with the following keys:
    - correct: boolean indicating if the student's code is correct or not. true or false
    If the student's code is corrent, then show quick tips for the student as follows:
    - quick_tips: an array of <li class="quick-tip"> tags showing quick tips for the student. Each quick tip should be a short, and there should be no more than 3 quick tips.

"""

module_name = ""
explain_module_query = """
You are an expert Python tutor. Your task is to provide a complete, clear, and engaging explanation of all topics within a single, specified module from the syllabus. Your explanation must be simple to understand and should build upon concepts the learner already knows.

The module to explain is {module_name}.

Rules
Explain each topic from the target module one by one, in the order they appear in the syllabus.

For each topic, provide a brief, easy-to-understand explanation followed by a clear, simple code example.

Ensure the code examples are runnable and include comments to explain each line.

Maintain a friendly and encouraging tone throughout the explanation.

The output should be in HTML. Don't use any markdown or other formatting. Use code tags for code examples, not ``` or ```python.

OUTPUT FORMAT
The output should be in HTML with the following structure:
<h2>Module Name</h2>
<h3>Topic 1</h3>
<p>Explanation of Topic 1</p>
<pre><code>Code example for Topic 1</code></pre>
<h3>Topic 2</h3>
<p>Explanation of Topic 2</p>
<pre><code>Code example for Topic 2</code></pre>
... and so on for all topics in the module.


... and so on for all topics in the module.

EXAMPLE OUTPUT
<h2>Strings</h2>
<h3>Slicing</h3>
<p>Slicing is a super handy way to grab a specific part of a string, just like you would cut a slice of pizza. It works similarly to how you would access items in a list or tuple. You can specify a starting point and an ending point to get a new, smaller string.</p>

<p>A simple string to slice</p>
<pre><code>
message = "Hello, Python!"

# Get a slice from index 7 to 13 (the word "Python")
# Remember, the end index is not included.
python_slice = message[7:13] 
print(python_slice) 

# Get a slice from the beginning to index 5
first_five = message[:5]
print(first_five)

# Get a slice from index 7 to the end
rest_of_string = message[7:]
print(rest_of_string)
</code></pre>

"""
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
    prompt = create_report_query
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
    prompt = create_coding_challenge_query
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
    result = call_gemini_model(prompt, model="gemini-2.5-flash").replace("```json", "").replace("```python", "").replace("```", "")
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
    question_data = []
    progress = ""
    return "OK"

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True)

