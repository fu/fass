<p align="center">
  <img src="https://raw.githubusercontent.com/fu/fass/main/logo/fass.png" />
</p>
<h2 align="center">FASS - FastAPI - Selenium - Scraper</h2>

This simple server enables scraping of website with dynamic content.
It exposes the parser via rest API: `http://localhost:8000/parse` and accepts POST in the form of, e.g.

```
curl -X POST "http://localhost:8000/parse/" -H "Content-Type: application/json" -d '[
            {
                "url": "https://github.com/pymzml/pymzML/",
                "name": "Github stars",
                "delay": "1",
                "patterns": [
                    {
                        "name": "Star Counter",
                        "regex": "Counter js-social-count\\\">(?P<Stars>[0-9]*)</span>"
                    }
                ]
            }
        ]'
```

the payload contains a list of websites to scrape, each containing the `url` a `name`, `delay` in seconds and `patterns`. The two first kwargs are self explenatory, the `delay` parameters defines how many seconds the selenium driver should wait until the page is scraped. The `pattern` represent a list of entities to extract from the page, defined by Python `regex` expression and a `name` which will be used in the returned json.

The example above return:

```
{
    "name":"Github stars",
    "all_fields_matched":true,
    "Star Counter":["154"]
}
```
Please note that the matched values are always a list since we match all occurences on page. If multiple Python regex groups are defined, the returned list will contain tuples.

## Installation

### From source

Clone this repo and 

`docker build -t fass_app .`

and

`docker run -d -p 8000:8000 fass_app`

then execute the curl command above.

### From Docker hub

`docker pull zerealfu/fass:0.1.0 ` 

for example. 

Have fun :)
