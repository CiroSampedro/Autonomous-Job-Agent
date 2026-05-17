from playwright.sync_api import sync_playwright


class BrowserTools:

    def __init__(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=False
        )

        self.page = self.browser.new_page()

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
    # SEARCH JOBS
    # -------------------------
    def search_jobs(self, query):

        search_url = (
            f"https://www.indeed.com/jobs?q={query}&l=Remote"
        )

        self.page.goto(
            search_url,
            wait_until="domcontentloaded"
        )

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

            jobs.append(
                links.nth(i).inner_text()
            )

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

        return "Primer trabajo abierto"

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