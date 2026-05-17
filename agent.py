import json
import ollama

from tools import BrowserTools


browser = BrowserTools()

goal = "Find remote AI agent jobs"

memory = []


# -------------------------
# CLEAN JSON
# -------------------------
def clean_json(text):

    text = text.strip()

    if "```" in text:

        parts = text.split("```")

        if len(parts) > 1:

            text = parts[1]

            text = text.replace(
                "json",
                ""
            ).strip()

    return json.loads(text)


# -------------------------
# PLANNER
# -------------------------
def planner(goal, memory):

    prompt = f"""
You are an autonomous AI job hunter agent.

Your job is to complete the goal
step by step using browser tools.

Available actions:

- search_jobs
- get_job_titles
- extract_page_text
- done

IMPORTANT:

- Only return ONE action at a time.
- Return ONLY valid JSON.
- Do not explain anything.
- Do not repeat useless actions.
- If jobs were already found,
you can finish with "done".

Example:

[
  {{
    "action": "search_jobs",
    "query": "AI agents"
  }}
]

Goal:
{goal}

Memory:
{memory}
"""

    response = ollama.chat(

        model="qwen2.5:7b",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    text = response["message"]["content"]

    print("\nRespuesta LLM:\n")
    print(text)

    return clean_json(text)


# -------------------------
# MAIN LOOP
# -------------------------
max_steps = 6

for i in range(max_steps):

    print(f"\n--- STEP {i+1} ---")

    try:

        actions = planner(
            goal,
            memory
        )

        step = actions[0]

        action = step["action"]

        print(f"\nEjecutando: {action}")

        # -------------------------
        # SEARCH JOBS
        # -------------------------
        if action == "search_jobs":

            result = browser.search_jobs(
                step["query"]
            )

            print(result)

            memory.append({
                "step": i,
                "action": action,
                "result": result
            })

        # -------------------------
        # GET JOB TITLES
        # -------------------------
        elif action == "get_job_titles":

            result = browser.get_job_titles()

            for job in result:

                print("-", job)

            memory.append({
                "step": i,
                "action": action,
                "result": result
            })

        # -------------------------
        # EXTRACT TEXT
        # -------------------------
        elif action == "extract_page_text":

            result = browser.extract_page_text()

            print(result[:1000])

            memory.append({
                "step": i,
                "action": action,
                "result": result[:1000]
            })

        # -------------------------
        # DONE
        # -------------------------
        elif action == "done":

            print("\nObjetivo completado")

            break

    except Exception as e:

        print("\nError:", e)

        memory.append({
            "step": i,
            "error": str(e)
        })


# -------------------------
# FINAL MEMORY
# -------------------------
print("\nMEMORIA FINAL:\n")

print(memory)

input("\nEnter para cerrar...")

browser.close()