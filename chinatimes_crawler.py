# import modular
import bs4
import json
import os
import os.path
import random
import requests
import time


# define global variables
CHINATIMES_URL = "http://www.chinatimes.com/politic/total"
DIRNAME_NEWS = "news\\"
SLEEP_TIME = 5


# define functions
def get_news_urls_from_page(page_url):
    news_urls = []

    try:
        r = requests.get(page_url)
        r.raise_for_status()

        if r.status_code == requests.codes.ok:
            soup = bs4.BeautifulSoup(r.text, "html.parser")
            section = soup.find("section", attrs={"class": "news-list"})
            
            for li in section.ul.find_all("li"):
                # URL formal of each news
                # http://www.chinatimes.com/realtimenews/20180118003511-260417
                # url = "http://www.chinatimes.com{0}".format(li.a["href"])
                url = "{0}".format(li.a["href"])
                _id = url[url.rindex("/")+1:]
                _time = li.time["datetime"]
                title = li.h3.text.strip(" \t\r\n")

                news_data = {"id": _id, "url": url, "time": _time, "title": title}

                news_urls.append(news_data)
        else:
            # pass to the below "return" statement
            pass
    except Exception as e:
        print("[ERR] {0}".format(e))
        print()
    
    return news_urls


def get_page_urls_of_website(website_url):
    news_urls_list = []
    
    try:
        # connect to each URL of news
        r = requests.get(website_url)
        r.raise_for_status()

        if r.status_code == requests.codes.ok:
            # total number of pages
            soup = bs4.BeautifulSoup(r.text, "html.parser")
            pages = soup.find_all("div", attrs={"class": "pagination"})[0]
            num_page = int(pages.find_all("li")[-3].text.strip())

            # URL format of each page:
            # http://www.chinatimes.com/armament/total?page=1
            page_list = ["{0}?page={1}".format(website_url, i + 1) for i in range(0, num_page)]

            # get url of each news
            for page_url in page_list:
                news_urls = get_news_urls_from_page(page_url)

                if news_urls:
                    print(".", end="")
                    news_urls_list.append(news_urls)
                else:
                    # skip this page, and go to the next page
                    pass
                
                time.sleep(random.randint(1, SLEEP_TIME))
        else:
            # pass to the below "return" statement
            pass
    except Exception as e:
        print("[ERR] {0}".format(e))

    print()

    return news_urls_list


def get_article_from_url(news_url):
    text_list = []

    try:
        r = requests.get(news_url)
        r.raise_for_status()

        if r.status_code == requests.codes.ok:
            # get contents of news
            soup = bs4.BeautifulSoup(r.text, "html.parser")
            article = soup.find("article", attrs={"class": "arttext"})
            text_list = [p.text.strip(" \t\r\b") for p in article.find_all("p") if p.text.strip(" \t\r\n")]

            # skip "(中時電子報)" and "文章來源"
            # text_list = text_list[:-2]
        else:
            # skip this news, and go to the next news
            pass
    except Exception as e:
        print("[ERR] {0}".format(e))

    time.sleep(random.randint(1, SLEEP_TIME))
    
    return text_list


def save_news_to_file(news):
    # 取得新聞內容
    news_url = news["url"]
    news_article = get_article_from_url(news_url)

    if news_article:
        # 檢查是否有"news"資料夾
        if not os.path.isdir(DIRNAME_NEWS):
            os.mkdir(DIRNAME_NEWS)
        else:
            pass
        
        # 寫入JSON檔
        filename = "{0}{1}_{2}.json".format(DIRNAME_NEWS, news["id"], news["title"])
        news["article"] = news_article
        
        with open(filename, 'w', encoding="utf-8", errors='ignore') as f:
            json.dump(news, f)
    else:
        # skip this news, and go to the next news_url
        pass


def chinatimes_crawler(website_url=CHINATIMES_URL):    
    print(">>> START ChinaTimes-Crawler!!")
    print()

    print("[Msg] Get urls of ChinaTimes website")
    news_page_list = get_page_urls_of_website(website_url)

    for i in news_page_list:
        print(i)
    
    if news_page_list:
        print("[Msg][Save] Save news to files")

        for news_page in news_page_list:
            for news in news_page:
                save_news_to_file(news)

                print(".", end="")
            print()
    else:
        print("[ERR] Can not connect to the ChinaTimes website: {0}".format(website_url))
        print()

    print()
    print(">>> STOP ChinaTimes-Crawler!!")


if __name__ == "__main__":
    chinatimes_crawler()
