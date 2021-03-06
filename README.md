# Facebook Scraper Selenium

Crawler Comment Facebook Public Posts without using Facebook API

## What It can Do

- Scrape Public Post Text
  - Raw Text
  - Link
- Scrape Public Post Comments
  - Links in Comments

## Install Requirements

Make sure chrome is installed and `chromedriver` is placed in the same directory as the file

Place your Facebook login in info into `facebook_credentials.txt`

```sh
pip install -r requirements.txt
```

## Usage

#### 0. Find link

```
Open http://touch.facebook.com/ and find the URL of the page you want to crawl
```

#### 1. Use scraper.py to crawler

```
usage: scraper.py [-h] -page PAGE -len LEN [-infinite INFINITE] [-usage USAGE]
                  [-comments COMMENTS]


```

#### 2. Use `extract()` to grab list of posts for additional parsing

```
from scraper import extract

list = extract(page, len, etc..)

# do what you want with the list
```

Return value of `extract()` :

```python
[
{
 'Comments':}
]
```

### Note:

- Please use this code for Educational purposes only
