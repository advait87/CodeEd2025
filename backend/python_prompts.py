# python_prompts.py

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

create_coding_challenge_query = """
You are an expert Python tutor. Your task is to generate a single, clear, and relevant programming task for a learner based on a specified topic. The task must be a short, self-contained coding challenge formatted in a clear, LeetCode-style.

USER PROMPT
Given the following learner mastery data, generate a task for the next remaining topic in the syllabus. This will always be the first topic in the first module listed under the "remaining" key. The task should be designed to assess the learner's understanding of this topic.

Learner's Mastery Data
{
"understood": [
{ "module": "Introduction to Programming", "topics": ["What is Python?"] },
{ "module": "Variables and Datatypes", "topics": ["Identifiers", "type()"] }
],
"remaining": [
{ "module": "Variables and Datatypes", "topics": ["Operators", "input()"] },
{ "module": "Strings", "topics": ["Slicing", "String Functions"] }
],
"summary": "The learner has a solid grasp of basic Python concepts and variable identification but struggles with operators and string manipulation."
}

Rules
The task must be directly related to the first topic in the first module of the remaining list.

The task must be a coding challenge that requires the learner to write a code snippet.

The task must include a problem description and at least one example case with Input, Output, and an Explanation.

Output (strict Markdown string format)
The output should be a single Markdown string containing the task title, a brief problem description, and one or more examples. No extra information or dictionary formatting.

EXAMPLE OUTPUT
### **1. Two Sum**

Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.

**Example 1:**

**Input:** `nums = [2,7,11,15]`, `target = 9`
**Output:** `[0,1]`
**Explanation:** Because `nums[0] + nums[1] == 9`, we return `[0, 1]`.

**Example 2:**

**Input:** `nums = [3,2,4]`, `target = 6`
**Output:** `[1,2]`"""

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
