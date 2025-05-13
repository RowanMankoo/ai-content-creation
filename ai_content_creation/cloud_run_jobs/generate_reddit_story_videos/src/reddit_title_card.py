from string import Template
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright
import random
from logging import getLogger

logger = getLogger(__name__)

TEMPLATE_PATH = Path("assets/template.html")
AVATAR_PATH = Path("assets/avatar.png")

def make_reddit_card(
    title,
    username,
    subreddit,
    output,
    width=800,
    height=600,
    scale=1,
):

    img_data = base64.b64encode(AVATAR_PATH.read_bytes()).decode("ascii")
    avatar_url = f"data:image/png;base64,{img_data}"

    html = Template(TEMPLATE_PATH.read_text(encoding="utf-8")).substitute(
        title=title,
        username=username,
        subreddit=subreddit,
        age=random.choice(["1h", "2h", "3h", "4h", "5h"]),
        points=random.randint(10000, 99999),
        comments=random.randint(1000, 9999),
        avatar_url=avatar_url,
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": width, "height": height}, device_scale_factor=scale
        )
        page.set_content(html, wait_until="networkidle")

        # Select the card and screenshot just that element
        card = page.query_selector(".card")
        if not card:
            raise RuntimeError("Could not find .card element in the template")
        card.screenshot(path=output, omit_background=True)
        browser.close()

    logger.info(f"Wrote {output}")
