# AI_LOG.md

Every time you update your project, please make a note of what you did in the `AI_LOG.md` file, according to the following template.

---

## [Milestone name] — [2026-09-17]
**Tool(s) used:** Gemini and ChatGPT
**What I asked for:** Assistance in generating documentation for a project component, specifically drafting clean Markdown formatting and outlining technical steps.
**What I kept as-is:** The initial structural outline and the foundational code snippets provided by the AI, which correctly matched the required syntax and formatting.
**What I changed or rejected, and why:** Refined and edited the generated explanatory text to better reflect the specific project context, and removed redundant wrapper text to keep the documentation concise and readable.
**Something the AI got wrong that I had to catch:** None

---
# AI Collaboration Log (AI_LOG.md)

## 1. Tools and Prompts
* **Tools Used:** Gemini personal AI collaborator.
* **Key Prompts:** 
  * "How can I make initial user passwords default to their joining date in `database.py`?"
  * "How do I structure `SPRINT_01.md` to match my professor's agile homework requirements?"

## 2. What Was Retained or Changed
* **Retained:** The FastAPI routing and the Python logic separating the MongoDB query by email to allow flexible password/joining-date validation.
* **Changed:** Adjusted default role assignments to strictly enforce the Principle of Least Privilege (`role="employee"` by default).

## 3. Errors Caught
* **Issue:** FastAPI form handling threw a 422 error because `python-multipart` was missing when parsing HTML form inputs.
* **Resolution:** Installed `python-multipart` via pip in the terminal.

## 4. One Decision the Team Can Explain Without AI
* **Decision:** Using SHA-256 for password hashing alongside a clear joining-date fallback mechanism. 
* **Explanation:** Storing plain text passwords is a security risk. Hashing provides basic protection, while allowing the joining date as a temporary initial password solves the onboarding problem for brand-new employees before they set their custom passwords.