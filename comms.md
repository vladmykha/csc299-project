Hello, I am taking a course in vibe coding and ai which is based on using ai and llm's tyo code your projects with and for you, these are the instructions

This project revolves around the use of AI-coding assistants to plan, specify, develop, and test your own software that includes: personal knowledge management system (PKMS) 
personal task management system a terminal-based chat interface to interact with your stored knowledge and tasks AI agents that interact with the stored knowledge or tasks 
The software must be written in Python, and must run portably on Windows, OSX, Linux. Your state should be stored in JSON documents, a SQLite database, or a Neo4J database

For my project I want an easier was for students to access my university's grading webside which is their own proprietary websirte for each students to access their records 
and anything they may ned for school, the student must login with their school credentials and they are redirected into their account with all of their records. 
Essentially, this is like the app pulse for depaul students but intead of being used for d2l like pulse is, I was to make my project for campus connect.

Nice, this is a fun project idea and it fits the class theme really well.

You basically want a **“CampusConnect Companion”**: a local tool that makes it easier for students to see grades / deadlines and manage their stuff, with AI on top.

Because Campus Connect is proprietary and behind login, you *shouldn’t* build something that:

* Stores other people’s passwords
* Tries to “log in for them” by bypassing normal flows
* Scrapes the site in a way that violates terms of service

But you **can absolutely** build a tool that:

* Helps the student *organize* and *interpret* what they see in Campus Connect
* Lets them paste / export their info into your app (or use any official export if that exists)
* Uses AI agents to query that local data, remind them of tasks, and act like a study assistant

Below is a concrete design that fits your assignment requirements.

---

## High-Level Project Idea

**Name idea:** `campus_companion` (or “DePaul Study Hub”)

**Core concept:**
A terminal-based app where a student can:

1. **Import their data** (e.g., copy/paste grades, upcoming deadlines, schedule from Campus Connect into a JSON/CSV template, or type it in).
2. The app **stores**:

   * Courses, assignments, grades
   * Personal notes (PKMS)
   * Tasks / todos with due dates (task manager)
3. A **chat-like terminal interface** lets them type things like:

   * “What assignments are due this week?”
   * “What’s my approximate grade in CSC 301?”
   * “Remind me to start my essay 3 days before it’s due.”
   * “Summarize my week and list priorities.”
4. An **AI “agent” layer** (LLM-connected) reasons over:

   * Stored grades + tasks
   * Their notes
   * And then responds/chat in the terminal.

---

## How it maps to the assignment requirements

> **1. Personal knowledge management system (PKMS)**

You can store:

* **Entities:**

  * `Course`: name, code, instructor, meeting time
  * `Assignment`: title, course, due date, weight, status, grade
  * `Note`: text + tags (course, topic, date)
  * `Exam`: date, type, weight

These go into **SQLite** (or JSON). For example:

```text
courses
  id | code  | name           | term | instructor

assignments
  id | course_id | title    | due_date | weight | grade | status

notes
  id | course_id | title    | content | created_at | tags
```

That’s your PKMS: structured, queryable knowledge about their academic life.

> **2. Personal task management system**

You layer a standard todo system on top:

* `Task`: title, description, due_date, related_course_id, priority, status (todo/in-progress/done)

Features:

* Add tasks: “add task 'start research for HIST 200 essay' due 2025-12-03”
* List tasks by:

  * course
  * due date
  * priority
* Mark tasks done
* Optional: auto-generate tasks (“For each assignment, create a task ‘start assignment X’ 3 days before due date”)

> **3. Terminal-based chat interface**

One main entrypoint, e.g.:

```bash
python main.py
```

Brings up a **REPL-like chat**:

```text
Campus Companion
----------------
Type 'help' for commands, or just talk to the assistant.

You> show my assignments for this week
AI> You have 3 assignments due this week:
    1. CSC 301 - Homework 4 (due 2025-12-02, status: todo)
    2. WRD 104 - Essay Draft (due 2025-12-03, status: in-progress)
    3. MAT 151 - Quiz 6 (due 2025-12-04, status: todo)
```

It can support two modes:

* **Command mode** (slash commands like `/add_task`, `/add_grade`, `/list_courses`)
* **Chat mode** (natural language routed through LLM that then calls internal functions)

> **4. AI agents that interact with the stored knowledge or tasks**

Design at least one or two “agents”:

1. **Grade Assistant Agent**

   * Answers: “What’s my current grade in X?”
     → Look up assignments for course X, compute weighted average from stored grades.
   * Answers: “What do I need on the final to get a B?”
     → Simple grade calculation.

2. **Planning / Task Agent**

   * Given tasks + due dates, it:

     * Prioritizes tasks for the week
     * Splits large tasks into subtasks (e.g., “Essay 3” → outline, research, first draft, revision).
   * Answer queries:

     * “Plan my week.”
     * “What are the top 3 tasks I should do today?”

3. **Note Assistant Agent (PKMS AI)**

   * Searches notes by keyword, course, date.
   * Summarizes notes:

     * “Summarize my CSC 301 notes from last week.”
   * Helps generate study questions from notes:

     * “Make quiz questions from my CSC 301 midterm notes.”

Internally: the “AI agent” can be a function that:

* Reads from SQLite
* Formats a context string
* Sends it to an LLM (your class will prob give you an API or local model)
* Returns the reply in the terminal.

---

## How Campus Connect fits in (safely)

You **do not**:

* Store or handle DePaul passwords.
* Auto-login to Campus Connect for the user.

You **do**:

* Provide a small command like:

```text
You> import_grades
App> Copy your grades table from Campus Connect and paste it below.
     End with a single line: END
You> CSC 301 | HW1 | 100 | 10%
You> CSC 301 | HW2 | 85  | 10%
You> ...
You> END
App> Parsed 6 assignments for CSC 301 and saved them.
```

Or:

* Give them a `.csv` template they can fill in manually and then run:
  `python import_grades.py grades.csv`

This keeps you **within bounds** but still uses Campus Connect as the source of truth for the student.

---

## Storage choice: SQLite (recommended)

From your spec:

> Your state should be stored in JSON documents, a SQLite database, or a Neo4J database.

For a project like this, **SQLite is ideal**:

* Single file, very portable.
* Easy querying (grades, tasks, notes).
* Works on Windows/Mac/Linux.

You can:

* Use a single `campus_companion.db` file.
* Optionally have **backup/export as JSON** for portability.

---

## Rough module breakdown

You can structure the project like:

* `main.py`

  * Starts the REPL / chat loop.
* `storage.py`

  * Handles SQLite connections and CRUD for courses, tasks, notes, assignments.
* `models.py`

  * Dataclasses for `Course`, `Assignment`, `Task`, `Note`.
* `commands.py`

  * Functions for each command (`add_task`, `list_tasks`, `add_course`, `add_grade`, etc.).
* `ai_agent.py`

  * Interfaces with LLM.
  * Functions:

    * `answer_query_about_grades(user_text)`
    * `plan_tasks(user_text)`
    * `summarize_notes(user_text)`
* `import_export.py`

  * Functions to import from CSV / text.
  * Export all data to JSON backup.

---

## Example user flows (that your professor will like)

1. **Setup**

   * User adds their courses:

     * `/add_course "CSC 301" "Data Structures II" "Fall 2025"`
   * User imports or types assignments:

     * `/add_assignment "CSC 301" "HW1" 2025-12-01 0.1`
   * User adds tasks:

     * `/add_task "Start HW1 for CSC 301" 2025-11-29 --course "CSC 301"`

2. **Daily usage**

   * User runs `python main.py`
   * Chat:

     * “What should I work on today?”
     * “Show my upcoming assignments by course.”
     * “Give me a study plan for my CSC 301 exam.”

3. **AI-powered stuff**

   * “Summarize my notes for WRD 104 and generate 5 possible exam questions.”
   * “Based on my tasks and deadlines, create a 3-day plan and highlight critical tasks.”

---

## Next step: what I can do for you now

If you’d like, I can next:

* Sketch the **database schema** in more detail.
* Draft a **minimal skeleton code** in Python:

  * basic SQLite setup
  * a simple REPL loop
  * placeholder `ai_agent` function you can later hook to whatever LLM your course uses.
* Or design the **exact commands + chat prompts** you’ll support, so you can show that in your proposal / writeup.

Tell me which you want me to start with and I’ll build a first version of it.
