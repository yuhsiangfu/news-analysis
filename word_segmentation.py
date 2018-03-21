# import modular
import collections
import jieba
import json
import os
import os.path
import sys


# define variables
DIRNAME_NEWS = "news\\"
DIRNAME_WORDS = "words\\"
FILENAME_STOP_WORDS = "stopwords_all.txt"
FILENAME_USER_DICT = "userdict_all.txt"
NON_BMP_MAP = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)


# define function
def is_all_cht(s):
    return all(['\u4e00' <= i <= '\u9fff' for i in s])


def process_and_save_news_files(news_files):
    # user-define directory
    jieba.dt.tmp_dir = os.getcwd()
    jieba.dt.cache_file = "jieba.cache"
    jieba.load_userdict(FILENAME_USER_DICT)

    # read the stopwords file
    stopwords = set([t.strip().lower() for t in open(FILENAME_STOP_WORDS, "r", encoding="utf-8", errors='ignore').readlines()])
    stopwords.add(" ")
  
    for i, filename_input in enumerate(news_files):
        # read news' json files
        news_data = {}
        
        with open(DIRNAME_NEWS + filename_input, "r", encoding="utf-8", errors='ignore') as f_in:
            news_data = json.load(f_in)

        # --------------------------------------------------
        # skip website's info.
        article = news_data["article"]
        ref_list = []

        for j, a in enumerate(article):
            if ("(中時電子報)" in a) or ("(中時)" in a) or ("文章來源" in a):
                ref_list.append(j)

        if ref_list:
            article = article[:min(ref_list)]

        # --------------------------------------------------
        # word segmentation and stopwords removal
        clean_words = []
        
        for a in article:
            t_list = []
            tmp = jieba.lcut(a)

            for t in tmp:
                t_ = str(t.lower())

                # chinese words: not stopwords,  length > 1
                if (t_ not in stopwords) and (len(t_) > 1) and is_all_cht(t_):
                    t_list.append(t_)

            clean_words += t_list
        
        # --------------------------------------------------
        # count words
        news_data["term-frequency"] = collections.Counter(clean_words)

        # --------------------------------------------------
        # save results of word segmentation
        # check the folder
        if not os.path.isdir(DIRNAME_WORDS):
            os.mkdir(DIRNAME_WORDS)

        # --------------------------------------------------
        # save results to json file
        filename_output = "{0}{1}_{2}_counts.json".format(DIRNAME_WORDS, news_data["id"], news_data["title"])
        
        with open(filename_output, 'w', encoding="utf-8", errors='ignore') as f_out:
            json.dump(news_data, f_out)

        # show running marks
        if ((i+1) % 30) != 0:
            print(".", end="")
        else:
            print(".")


def word_segmentation():    
    print(">>> START Word-Segmentation!!")
    print()

    print("[Msg] Get NEWS file list")
    news_file_list = os.listdir(DIRNAME_NEWS)

    print("[Msg] Process/Save NEWS files: words segmentation and clean stop-words")
    process_and_save_news_files(news_file_list)

    print()
    print(">>> STOP Word-Segmentation!!")


if __name__== "__main__":
    word_segmentation()
