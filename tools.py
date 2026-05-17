from playwright.sync_api import sync_playwright
import os
import time


class BrowserTools:

    def __init__(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=False
        )

        if os.path.exists("state.json"):
            self.context = self.browser.new_context(storage_state="state.json")
        else:
            self.context = self.browser.new_context()

        self.page = self.context.new_page()

    # -------------------------
    def save_session(self):
        self.context.storage_state(path="state.json")
        return "saved"

    # -------------------------
    def search_jobs(self, query):
        url = f"https://www.indeed.com/jobs?q={query}&l=Remote"
        self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)
        return "indeed ok"

    def get_job_titles(self):
        self.page.wait_for_selector("h2 a", timeout=15000)
        loc = self.page.locator("h2 a")
        return [loc.nth(i).inner_text().strip() for i in range(min(5, loc.count()))]

    def open_first_job(self):
        self.page.locator("h2 a").first.click()
        time.sleep(3)
        return "indeed opened"

    # -------------------------
    def search_remoteok(self, query):
        url = f"https://remoteok.com/remote-{query.replace(' ', '-')}-jobs"
        self.page.goto(url, timeout=60000)
        time.sleep(3)
        return "remoteok ok"

    def get_remoteok_titles(self):
        self.page.wait_for_selector("td.company_and_position h2", timeout=15000)
        loc = self.page.locator("td.company_and_position h2")
        return [loc.nth(i).inner_text().strip() for i in range(min(5, loc.count()))]

    # -------------------------
    # UPWORK FIX REAL
    # -------------------------
    def search_upwork_jobs(self, query):

        url = f"https://www.upwork.com/nx/search/jobs/?q={query.replace(' ', '%20')}"

        self.page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # scroll to force render
        for _ in range(3):
            self.page.mouse.wheel(0, 2000)
            time.sleep(2)

        return "upwork loaded"

    def get_upwork_titles(self):

        selectors = [
            "[data-test='job-tile-title-link']",
            "h2",
            "h4",
            "article h2"
        ]

        for sel in selectors:

            try:
                loc = self.page.locator(sel)
                count = loc.count()

                if count > 0:

                    titles = []

                    for i in range(min(count, 10)):

                        try:
                            text = loc.nth(i).inner_text().strip()

                            if len(text) > 6 and "proposals" not in text.lower():
                                titles.append(text)

                        except:
                            continue

                    if titles:
                        return titles

            except:
                continue

        return []

    def open_first_upwork_job(self):

        loc = self.page.locator("[data-test='job-tile-title-link']")

        for i in range(min(loc.count(), 10)):

            try:
                text = loc.nth(i).inner_text().strip()

                if len(text) > 6:
                    loc.nth(i).click()
                    time.sleep(4)
                    return f"upwork opened: {text}"
            except:
                pass

        return "no upwork job opened"

    # -------------------------
    def extract_page_text(self):

        time.sleep(2)

        text = self.page.locator("body").inner_text()

        return text[:5000]

    def close(self):
        self.browser.close()
        self.playwright.stop()