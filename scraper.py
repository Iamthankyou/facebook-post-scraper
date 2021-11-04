import argparse
import time
import json
import csv
import re
from selenium.common.exceptions import NoSuchElementException

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs

import logging
import sys
import os

import math

def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('log.txt', mode='w')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger

with open('facebook_credentials.txt') as file:
    EMAIL = file.readline().split('"')[1]
    PASSWORD = file.readline().split('"')[1]

def check_exists_by_xpath(webdriver,xpath):
    try:
        webdriver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def check_exists_by_id(webdriver,id):
    try:
        webdriver.find_element_by_id(id)
    except:
        return False
    return True

def check_exists_click(webdriver, element):
    try:
        webdriver.click()
    except:
        return False
    return True


def _extract_comments_(item):
    mydivs = item.find_all("div", {"class": "kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x c1et5uql"})
    comments = dict()
    i = 1
    for comment in mydivs:
        comments[i] = comment.find("div", dir="auto").text
        i+=1

    return comments

def _extract_html_filename(bs_data, file_name):
    postBigDict =  _extract_comments_(bs_data)

    with open('./'+file_name+'.json', 'w', encoding='utf-8') as file:
        file.write(json.dumps(postBigDict, ensure_ascii=False).encode('utf-8').decode())

    return postBigDict

def _extract_html(bs_data):
    postBigDict =  _extract_comments_(bs_data)

    with open('./postBigDict.json', 'w', encoding='utf-8') as file:
        file.write(json.dumps(postBigDict, ensure_ascii=False).encode('utf-8').decode())

    return postBigDict

def _extract_to_json(data, file_name):
    comments = data.find_all("div", {"data-sigil": "comment-body"})
    list_comments = list()

    for i in comments:
        list_comments.append(i.text)

    with open('./'+file_name+'.json', 'w', encoding='utf-8') as file:
        file.write(json.dumps(list_comments, ensure_ascii=False).encode('utf-8').decode())

def _extract_file_html(file_name):
    f = open(file_name,'r')
    soup = bs(f.read())
    _extract_to_json(soup,file_name)

def _login(browser, email, password):
    browser.get("http://facebook.com")
    browser.maximize_window()
    browser.find_element_by_name("email").send_keys(email)
    browser.find_element_by_name("pass").send_keys(password)
    browser.find_element_by_name('login').click()
    time.sleep(5)

def _count_needed_scrolls(browser, infinite_scroll, numOfPost):
    if infinite_scroll:
        lenOfPage = browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;"
        )
    else:
        # roughly 4 post per scroll
        lenOfPage = int(math.ceil(numOfPost / 4))
    logger.info("Number Of Scrolls Needed " + str(lenOfPage))
    return lenOfPage


def _scroll(browser, infinite_scroll, lenOfPage):
    lastCount = -1
    match = False

    while not match:
        if infinite_scroll:
            lastCount = lenOfPage
        else:
            lastCount += 1

        time.sleep(5)

        if infinite_scroll:
            logger.info("Scrolling page infinity")
            lenOfPage = browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return "
                "lenOfPage;")
        else:
            logger.info("Scroll page th" + str(lastCount))
            browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return "
                "lenOfPage;")

        if lastCount == lenOfPage:
            match = True

def read_comment_mobile_post(browser,page, url_name_page):
    browser.get(page)
    logger.info("Check")

    i = 1
    error = 0
    count = 0

    error_click = 0
    file_full = 0

    res = re.search('fbid=[0-9]+',page).group(0).split('=')[1]
    logger.info('The id of post: '+str(res))

    while True:
        count += 1
        if check_exists_by_id(browser,'see_next_'+res):
            more = browser.find_element_by_id('see_next_'+res)
            try:
                more.click()
            except:
                logger.error("Error: click, auto try again")
            error = 0
        elif check_exists_by_id(browser,'see_prev_'+res):
            more = browser.find_element_by_id('see_prev_' + res)
            try:
                more.click()
            except:
                logger.error("Error: click, auto try again")
            error = 0
        else:
            logger.error("Error: not finding id, auto try again" + str(error))
            error +=1
            if error == 20:
                break

        if (count == 100):
            count=0
            logger.info("Save :")
            source_data = browser.page_source
            bs_data = bs(source_data, 'html.parser')

            curr = bs_data.find_all("div", {"data-sigil": "comment-body"})
            try:
                ff = open(r'./'+url_name_page+'/'+res+'.html', 'r')
                file_prev = bs(ff.read())
                prev = file_prev.find_all("div", {"data-sigil": "comment-body"})
                logger.info("Curr= " + str(len(curr)) + ", Prev= "+ str(len(prev)))

                if len(curr)>len(prev):
                    file_full=0
                    with open(r'./'+url_name_page+'/'+res+'.html', "w", encoding="utf-8") as file:
                        file.write(str(bs_data.prettify()))
                else:
                    logger.info("Full loop: " + str(file_full) + "/" + "2")
                    file_full+=1
                    if file_full==3:
                        break
            except:
                with open(r'./'+url_name_page+'/' + res + '.html', "w", encoding="utf-8") as file:
                    file.write(str(bs_data.prettify()))

    logger.info("Saved file html!")
    source_data = browser.page_source
    bs_data = bs(source_data, 'html.parser')
    with open(r'./'+url_name_page+'/'+res+'.html', "w", encoding="utf-8") as file:
        file.write(str(bs_data.prettify()))

    # browser.close()

def read_comment_post(page):
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")

    # Pass the argument 1 to allow and 2 to block
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    browser = webdriver.Chrome(executable_path="./chromedriver", options=option)
    _login(browser, EMAIL, PASSWORD)
    browser.get(page)

    # showComment = browser.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div[1]/div/div/div[2]/div/div[3]/div/span')
    # showComment.click()
    # time.sleep(3)

    choose_option_comment = browser.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div[2]/div[1]/div/div/div/span')
    choose_option_comment.click()
    time.sleep(3)


    allComment = browser.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div/div/div/div[1]/div/div[3]')
    allComment.click()
    time.sleep(3)

    moreComments = browser.find_elements_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div[2]/div[2]/div[2]/div[1]/div[2]/span/span')

    i = 1
    while len(moreComments) != 0:
        logger.info("Scrolling through to click on more comments " + str(i))
        i+=1
        for moreComment in moreComments:
            # action = webdriver.common.action_chains.ActionChains(browser)
            try:
                # move to where the comment button is
                # action.move_to_element_with_offset(moreComment, 5, 5)
                # action.perform()
                moreComment.click()
            except:
                # do nothing right here
                pass

        moreComments = browser.find_elements_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div[2]/div[2]/div[2]/div[1]/div[2]/span/span')

    source_data = browser.page_source

    bs_data = bs(source_data, 'html.parser')
    mydivs = bs_data.find_all("div", {"class": "kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x c1et5uql"})
    logger.info(str(len(mydivs)))
    postBigDict = _extract_html_filename(bs_data,'comments')
    sleep(10000)

def read_all_link_post(browser,page, numOfPost, infinite_scroll):
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")

    # Pass the argument 1 to allow and 2 to block
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    browser.get(page)
    lenOfPage = _count_needed_scrolls(browser, infinite_scroll, numOfPost)
    _scroll(browser, infinite_scroll, lenOfPage)

    source_data = browser.page_source
    bs_data = bs(source_data, 'html.parser')
    links = get_all_href_post(bs_data)

    prev = len(links)

    num_not_inc = 0

    while len(links) < numOfPost:
        logger.error("len(links)<numOfPost: " + str(len(links)) + "<" + str(numOfPost))
        _scroll(browser, False, 1)
        source_data = browser.page_source
        bs_data = bs(source_data, 'html.parser')
        links = get_all_href_post(bs_data)

        if prev==len(links):
            logger.info("Not increase num post: " + str(num_not_inc) + "/2")
            num_not_inc+=1
            if num_not_inc == 3:
                break
        else:
            num_not_inc = 0

        prev = len(links)


    links = links[0:numOfPost]

    with open('links.txt', 'w') as f:
        for link in links:
            f.writelines(link+"\n")
    logger.info('All links saved in link.txt')

    return links

def get_all_href_post(source):
    posts = source.find_all("a", {"data-sigil": "feed-ufi-focus feed-ufi-trigger ufiCommentLink mufi-composer-focus"})
    list_href = ['https://touch.facebook.com'+post['href'] for post in posts]
    return list_href

def read_num_post(browser,page, numOfPost):
    # Find name page
    url_name_page = "default_folder"

    browser.get(page)
    try:
        source_data = browser.page_source
        bs_data = bs(source_data, 'html.parser')
        url_name_page = bs_data.find("a", {"data-sigil": 'MBackNavBarClick'}).text
    except Exception as e:
        logger.error("Not finding url_name_page")
        logger.error(e);

    try:
        os.mkdir('./'+url_name_page)
    except Exception as e:
        logger.error("Can't create folder " + url_name_page)
        logger.error(e)

    # Create file links.txt
    links = read_all_link_post(browser,page, numOfPost, False)
    start = 0
    end = len(links)

    with open('links.txt', "r") as file:
        line = file.readline()
        while line:
            start+=1
            logger.info("Read page " + str(start)+"/"+str(end)+': '+ line)
            try:
                read = True
                try:
                    fi = open('./'+url_name_page+'/saved.txt','r')
                    links_saved = fi.readline()
                    while links_saved:
                        links_saved=links_saved[0:len(links_saved)-1]
                        if links_saved == re.search('fbid=[0-9]+',line).group(0).split('=')[1]:
                            logger.info('This post saved, auto read next post')
                            read = False
                            break
                        links_saved = fi.readline()
                    fi.close()
                except Exception as e:
                    logger.error('Not found file saved, auto create next loop')
                    logger.error(e)

                if read:
                    read_comment_mobile_post(browser,line, url_name_page)
                    with open('./'+url_name_page+'/saved.txt','a') as f:
                        id = re.search('fbid=[0-9]+', line).group(0).split('=')[1]
                        f.writelines(id+"\n")
                    logger.info("End of read post: "+ line)
            except Exception as e:
                logger.error("Error read: "+ line)
                logger.error(e)

            line = file.readline()

def read_comment_page_desktop(page, numOfPost, infinite_scroll=False, scrape_comment=False):
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")

    # Pass the argument 1 to allow and 2 to block
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    # chromedriver should be in the same folder as file
    browser = webdriver.Chrome(executable_path="./chromedriver", options=option)
    _login(browser, EMAIL, PASSWORD)
    browser.get(page)
    lenOfPage = _count_needed_scrolls(browser, infinite_scroll, numOfPost)
    _scroll(browser, infinite_scroll, lenOfPage)

    elements =  browser.find_elements_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div[2]/div[1]/div/div/div/span')
    while len(elements)>0:
        for e in elements:
            e.click()
            time.sleep(3)

            allComment = browser.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div/div/div/div[1]/div/div[3]')
            allComment.click()
            time.sleep(3)

    for i in range(2,numOfPost):
        if scrape_comment:
            # first uncollapse collapsed comments
            s = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div[2]/div/div[2]/div[2]/div/div/div[2]/'
            f = '/div/div/div/div/div/div/div/div/div/div[2]/div/div[4]/div/div/div[2]/div[5]/div[1]/div[2]/span/span'
            res = s + 'div[' + str(int(i)) + ']' + f
            moreComments = browser.find_elements_by_xpath(res)

            while len(moreComments) != 0:
                logger.info("Scrolling through to click on more comments "+str(i))
                for moreComment in moreComments:
                    # action = webdriver.common.action_chains.ActionChains(browser)
                    try:
                        # move to where the comment button is
                        # action.move_to_element_with_offset(moreComment, 5, 5)
                        # action.perform()
                        moreComment.click()
                    except:
                        # do nothing right here
                        pass

                moreComments = browser.find_elements_by_xpath(res)

    # Now that the page is fully scrolled, grab the source code.
    source_data = browser.page_source

    # Throw your source into BeautifulSoup and start parsing!
    bs_data = bs(source_data, 'html.parser')
    mydivs = bs_data.find_all("div", {"class": "kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x c1et5uql"})
    logger.info(str(len(mydivs)))
    postBigDict = _extract_html(bs_data)
    # browser.close()

    return postBigDict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Facebook Page Scraper")

    required_parser = parser.add_argument_group("Required arguments")

    optional_parser = parser.add_argument_group("Optional arguments")
    optional_parser.add_argument('-page', '-p', help="Facebook page URL", required=False)
    optional_parser.add_argument('-list', '-l', help="Directory file list facebook post", required=False)
    optional_parser.add_argument('-numOfPost', '-n', help="Number post you want to read", required=False)

    args = parser.parse_args()

    logger = setup_custom_logger('myapp')

    # INIT login
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")

    # Pass the argument 1 to allow and 2 to block
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    browser = webdriver.Chrome(executable_path="./chromedriver", options=option)
    _login(browser, EMAIL, PASSWORD)

    if args.list:
        file = open(args.list, "r")
        line = file.readline()
        folder = "default"
        try:
            os.mkdir('./' + folder)
        except Exception as e:
            logger.error("Can't create folder: " + folder)
            logger.error(e)

        while line:
            logger.info("Page: "+ line)
            try:
                read_comment_mobile_post(browser,line,folder)
                logger.info("End: "+ line)
            except Exception as e:
                logger.error("Error read: "+ line)
                logger.error(e)
            line = file.readline()
        file.close()
    else:
        page = args.page
        if args.numOfPost:
            read_num_post(browser,page, int(args.numOfPost))
        else:
            read_comment_mobile_post(browser,page)
