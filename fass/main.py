import re
import time
from fastapi import FastAPI, HTTPException, Request, Form, Depends
from typing import Optional, List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import logging

app = FastAPI()


@app.get("/check/")
async def check():
    logging.basicConfig(level=logging.INFO)
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    except Exception as e:
        logging.exception("Failed to initialize the WebDriver: %s", str(e))


"""Webscraper using selenium.

curl -X POST "http://localhost:8000/parse/" -H "Content-Type: application/json" -d '[
            {
                "url": "https://github.com/pymzml/pymzML/",
                "name": "Github stars",
                "delay": "10",
                "patterns": [
                    {
                        "name": "Star Counter",
                        "regex": "Counter js-social-count\\\">(?P<Stars>[0-9]*)</span>",
                    }
                ]
            }
        ]'

"""


def validate_payload(items: List[Dict]):
    """Validate payload.

    Yes one could use pydantic but wanted to avoid too many dependencies.

    Required fields are "url", "name" and "patterns".
    Patterns has to be a list and each entry must have "name" and "regex"
    """
    # Validate the overall structure
    for item in items:
        if not all(key in item for key in ["url", "name", "patterns"]):
            raise ValueError("Each item must have 'url', 'name', and 'patterns' keys")
        if not isinstance(item["patterns"], list):
            raise ValueError("'patterns' must be a list")

        # Validate each pattern in 'patterns'
        for pattern in item["patterns"]:
            if not all(key in pattern for key in ["name", "regex"]):
                raise ValueError("Each pattern must have 'name' and 'regex' keys")
    return items


@app.post("/parse/")
async def parse(request: Request):
    try:
        # Extract JSON body and validate
        json_body = await request.json()
        items = validate_payload(json_body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    for item in items:
        item_data = {"name": item["name"]}
        url = item["url"]
        patterns = item["patterns"]
        delay = int(item.get("delay", 10))
        item_data["all_fields_matched"] = True
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            service = Service(executable_path="/usr/bin/chromedriver")

            driver = webdriver.Chrome(service=service, options=chrome_options)

            driver.get(url)
        except Exception as e:
            logging.exception("Failed to scrape the website.")
            raise HTTPException(status_code=500, detail=str(e))

        time.sleep(delay)
        page_source = driver.page_source
        driver.quit()

        logging.debug(f"Recieved {patterns}")
        for pattern in patterns:
            regex = re.compile(pattern["regex"])
            matches = regex.findall(page_source)
            if len(matches) == 0:
                logging.debug(f"No match for {pattern['name']}")
                item_data["all_fields_matched"] = False
                continue
            item_data[pattern["name"]] = matches

    return item_data
