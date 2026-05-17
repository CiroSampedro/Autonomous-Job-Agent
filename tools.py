from playwright.sync_api import sync_playwright
import os


class BrowserTools:

    def __init__(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=False
        )

        # -------------------------
        # LOAD SAVED SESSION
        # -------------------------
        if os.path.exists("state.json"):

            self.context = self.browser.new_context(
                storage_state="state.json"
            )

        else:

            self.context = self.browser.new_context()

        self.page = self.context.new_page()

    # -------------------------
    # SAVE SESSION
    # -------------------------
    def save_session(self):

        self.context.storage_state(
            path="state.json"
        )

        return "Sesión guardada"

    # -------------------------
    # NAVIGATE
    # -------------------------
    def navigate(self, url):

        self.page.goto(
            url,
            wait_until="domcontentloaded"
        )

        return f"Navegado a {url}"

    # -------------------------
    # SEARCH JOBS (INDEED)
    # -------------------------
    def search_jobs(self, query):

        search_url = (
            f"https://www.indeed.com/jobs?q={query}&l=Remote"
        )

        self.page.goto(
            search_url,
            wait_until="domcontentloaded"
        )

        self.page.wait_for_timeout(3000)

        return f"Buscando trabajos: {query}"

    # -------------------------
    # GET JOB TITLES
    # -------------------------
    def get_job_titles(self):

        self.page.wait_for_selector("h2 a")

        links = self.page.locator("h2 a")

        count = min(links.count(), 5)

        jobs = []

        for i in range(count):

            title = links.nth(i).inner_text().strip()

            if len(title) > 3:

                jobs.append(title)

        return jobs

    # -------------------------
    # OPEN FIRST JOB
    # -------------------------
    def open_first_job(self):

        self.page.wait_for_selector("h2 a")

        first_job = self.page.locator(
            "h2 a"
        ).first

        first_job.click()

        self.page.wait_for_load_state(
            "domcontentloaded"
        )

        self.page.wait_for_timeout(3000)

        return "Primer trabajo abierto"

    # -------------------------
    # REMOTEOK SEARCH
    # -------------------------
    def search_remoteok(self, query):

        formatted_query = query.replace(
            " ",
            "-"
        )

        url = (
            f"https://remoteok.com/remote-{formatted_query}-jobs"
        )

        self.page.goto(
            url,
            wait_until="domcontentloaded"
        )

        self.page.wait_for_timeout(3000)

        return f"Buscando en RemoteOK: {query}"

    # -------------------------
    # REMOTEOK TITLES
    # -------------------------
    def get_remoteok_titles(self):

        self.page.wait_for_selector(
            "td.company_and_position h2"
        )

        jobs = self.page.locator(
            "td.company_and_position h2"
        )

        count = min(jobs.count(), 5)

        titles = []

        for i in range(count):

            title = jobs.nth(i).inner_text().strip()

            if len(title) > 3:

                titles.append(title)

        return titles

    # -------------------------
    # EXTRACT PAGE TEXT
    # -------------------------
    def extract_page_text(self):

        self.page.wait_for_load_state(
            "domcontentloaded"
        )

        text = self.page.locator(
            "body"
        ).inner_text()

        return text[:5000]

    # -------------------------
    # CLOSE
    # -------------------------
    def close(self):

        self.browser.close()

        self.playwright.stop()