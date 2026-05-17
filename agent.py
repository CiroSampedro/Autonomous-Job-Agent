import json
import ollama
from tools import BrowserTools


browser = BrowserTools()

goal = "Find remote AI agent jobs"

memory = []
completed_actions = set()

blocked_by_cloudflare = False

input("Logueate manualmente si hace falta y apretá ENTER...")

browser.save_session()


def clean_json(text):
    text = text.strip()

    if "```" in text:
        parts = text.split("```")
        if len(parts) > 1:
            text = parts[1].replace("json", "").strip()

    try:
        return json.loads(text)
    except:
        print("\nJSON ERROR:\n", text)
        raise


def planner(goal, memory, blocked):

    prompt = f"""
You are an autonomous job hunter.

STRICT FLOW:

PHASE 1 (DEFAULT):
search_jobs → get_job_titles → open_first_job → extract_page_text

IF blocked OR bad results:
PHASE 2:
search_remoteok → get_remoteok_titles

PHASE 3 (ONLY IF NEEDED):
search_upwork_jobs → get_upwork_titles → open_first_upwork_job → extract_page_text

THEN:
done

RULES:
- ONE action only
- VALID JSON only
- NO markdown
- NO text
- CONTINUE from memory
- NEVER repeat actions

blocked={blocked}

memory:
{json.dumps(memory, indent=2, ensure_ascii=False)}
"""

    res = ollama.chat(
        model="qwen2.5:7b",
        messages=[{"role": "user", "content": prompt}]
    )

    text = res["message"]["content"].strip()

    print("\nLLM:\n", text)

    if text.startswith("{"):
        return [json.loads(text)]

    return clean_json(text)


def analyze_job(text):

    prompt = f"""
Return ONLY JSON:

{{
"title": "",
"company": "",
"remote": true,
"salary": "",
"score": 1,
"reason": ""
}}

TEXT:
{text[:3000]}
"""

    res = ollama.chat(
        model="qwen2.5:7b",
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        return json.loads(res["message"]["content"])
    except:
        return {
            "title": "",
            "company": "",
            "remote": True,
            "salary": "",
            "score": 1,
            "reason": "parse error"
        }


max_steps = 15

for i in range(max_steps):

    print(f"\n--- STEP {i+1} ---")

    try:

        actions = planner(goal, memory, blocked_by_cloudflare)
        step = actions[0]
        action = step["action"]

        if action in completed_actions and action != "extract_page_text":
            print("⚠️ loop detected")
            break

        if action != "extract_page_text":
            completed_actions.add(action)

        print("EXEC:", action)

        # ---------------- INDEED
        if action == "search_jobs":
            r = browser.search_jobs(step.get("query", "AI jobs"))
            memory.append({"action": action, "result": r})

        elif action == "get_job_titles":
            r = browser.get_job_titles()
            print(r)
            memory.append({"action": action, "result": r})

        elif action == "open_first_job":
            r = browser.open_first_job()
            memory.append({"action": action, "result": r})

        # ---------------- EXTRACT
        elif action == "extract_page_text":

            text = browser.extract_page_text()

            if any(x in text.lower() for x in ["cloudflare", "verify", "ray id"]):
                blocked_by_cloudflare = True
                memory.append({"action": action, "result": "BLOCKED"})
            else:
                analysis = analyze_job(text)
                memory.append({"action": action, "analysis": analysis})

        # ---------------- REMOTEOK
        elif action == "search_remoteok":
            r = browser.search_remoteok(step.get("query", "AI jobs"))
            memory.append({"action": action, "result": r})

        elif action == "get_remoteok_titles":
            r = browser.get_remoteok_titles()
            print(r)
            memory.append({"action": action, "result": r})

        # ---------------- UPWORK
        elif action == "search_upwork_jobs":
            r = browser.search_upwork_jobs(step.get("query", "AI jobs"))
            memory.append({"action": action, "result": r})

        elif action == "get_upwork_titles":
            r = browser.get_upwork_titles()
            print(r)
            memory.append({"action": action, "result": r})

        elif action == "open_first_upwork_job":
            r = browser.open_first_upwork_job()
            memory.append({"action": action, "result": r})

        elif action == "done":
            print("DONE")
            break

    except Exception as e:
        print("ERROR:", e)
        memory.append({"error": str(e)})


print("\nMEMORY:\n")
print(json.dumps(memory, indent=2, ensure_ascii=False))

input("Enter...")
browser.close()