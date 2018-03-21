# coding=utf-8
# import modular
import bisect
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import os.path
import pickle
import sys

from sklearn.manifold import MDS
from sklearn.manifold import TSNE

# define variables
CACHENAME_TD_MATRIX = "cache-td-matrix.pickle"
DIRNAME_NEWS = "news\\"
DIRNAME_WORDS = "words\\"
FILENAME_PLOT = "latent_space.png"
NON_BMP_MAP = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
MATRIX_SCALAR = 0.5
THRESHOLD_KEY_WORDS = 9
THRESHOLD_LSA_SIGMA = 0.9
PLOT_FONT_SIZE = 10
PLOT_X_SIZE = 7
PLOT_Y_SIZE = 7


# define functions
def read_words_docs_matrix(counts_file_list, threshold_tf=1):
    text_terms = None
    text_docs = None
    td_matrix = None

    if os.path.isfile(CACHENAME_TD_MATRIX):
        print("[Msg][TD-Matrix] Read the TD-Mmatrix")
       
        with open(CACHENAME_TD_MATRIX, 'rb') as f_in:
            text_terms, text_docs, tfidf = pickle.load(f_in)
    else:
        # TERMS and DOCS tags
        print("[Msg][TD-Matrix] Create the TD-Mmatrix")
        
        text_docs = ["d{0}".format(i+1) for i in range(len(counts_file_list))]
        text_terms = []

        # read json files of word segmentation results
        docs_list = []
        terms_set = set()

        for i, filename_input in enumerate(counts_file_list):
            with open(DIRNAME_WORDS + filename_input, "r", encoding="utf-8", errors="ignore") as f_in:
                # read tf
                words = json.load(f_in)
                words = words["term-frequency"]

                # choose tf > the threshold
                if threshold_tf > 1:
                    words = {t: tf for t, tf in words.items() if tf >= threshold_tf}

                # append filtered tf to a list
                if words:
                    docs_list.append(words)
                    terms_set |= set(words)

        # --------------------------------------------------
        # create term-index
        terms_index = {}

        if terms_set:
            for i, t in enumerate(sorted(terms_set)):
                # index of a word
                terms_index[t] = i

                # add its tag to a list
                text_terms.append(t)
        
        # --------------------------------------------------
        num_terms = len(terms_index)  # rows: terms
        num_docs = len(docs_list)     # cols: docs

        print("terms:", num_terms)
        print("docs: ", num_docs)

        # create TF matrix
        tf = np.zeros([num_terms, num_docs])

        for j, doc in enumerate(docs_list):
            for t, tf_ in doc.items():
                i = terms_index[t]

                # TF
                # tf[i,j] = tf_
                tf[i, j] = 1 + np.log(tf_)

        # create IDF matrix
        idf = np.zeros([num_terms, num_docs])
        
        for i in range(num_terms):
            t = tf[i, :]
            b = t > 0
            nt = len(t[b])

            # idf
            idf[i, b] = np.log(1 + (num_docs / nt))
        
        # create TFIDF matrix
        # tfidf = np.zeros([num_terms, num_docs])
        #
        # for i in range(num_terms):
        #     idf_ = idf[i,:]
        #     tf_ = tf[i,:]
        #     b = tf_ > 0
        #     tfidf[i, b] = tf_[b] * idf_[b]
        #
        tfidf = np.multiply(tf, idf)

    return text_terms, text_docs, tfidf


def get_k_singulars(s, p=0.9):
    s_cum = np.cumsum(s)
    c_max = np.amax(s_cum) * p
    k = bisect.bisect_left(s_cum, c_max)

    return k


def matrix_linear_scaling(m, scalar=1.0):
    # get dimensions of matrix
    d1, d2 = m.shape

    # normalization
    for i in range(m.ndim):
        col_i = m[:, i]
        col_max = np.amax(col_i)
        m[:, i] = np.divide(col_i, col_max)

    # create diagonal matrix
    s = np.zeros([d1, d1])

    for i in range(d1):
        for j in range(d1):
            s[i, j] = np.linalg.norm(m[i] - m[j])

    # linearly scaling the matrix
    s = np.multiply(s, scalar)
    m = np.dot(s, m)

    return m


def lsa(txt_t, txt_d, m, k=2, p=0.9):
    print("[Msg][LSA] Use SVD to decompose the TD-Matrix")
    
    # SVD
    u, s, vT = np.linalg.svd(m)

    # --------------------------------------------------
    # get top-k singular values of the matrix
    k = get_k_singulars(s, p)
    k = k if k > 2 else 2

    print("k: ", k)
    # print("k/2: ", round(k/2))

    u_ = u[:, :k]     # u
    s_ = np.diag(s)  # s
    s_ = s_[:k, :k]
    vT_ = vT[:k, :]   # vT

    # --------------------------------------------------
    # transfer terms and docs to the latent semantic space
    u_s_ = np.dot(u_, s_)
    # s_vT_ = np.dot(s_,vT_).transpose()

    # --------------------------------------------------
    print("[Msg][LSA] Project the latent space to a 2d-plane")

    # project the latent semantic space to a 2-d space
    # u_s_embedded = MDS(n_components=2, max_iter=1000).fit_transform(u_s_)
    u_s_embedded = TSNE(n_components=2, init='pca', random_state=0).fit_transform(u_s_)

    # do liner scaling to the 2-d space
    u_s_embedded = matrix_linear_scaling(u_s_embedded, scalar=MATRIX_SCALAR)

    # --------------------------------------------------
    print("[Msg][LSA] Draw a LSA 2d-plot")

    # plot setting of showing chinese words
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False

    # create figure
    fig, axes = plt.subplots(figsize=(PLOT_X_SIZE, PLOT_Y_SIZE), facecolor='w')

    x = [u[0] for u in u_s_embedded]
    y = [u[1] for u in u_s_embedded]

    axes.scatter(x, y, marker="o", facecolors='none', edgecolors='b', s=0, alpha=0.8)
    
    for i, t in enumerate(txt_t):
        axes.annotate(u"{0}".format(t), (x[i], y[i]), color="b", fontsize=PLOT_FONT_SIZE)
    
    # --------------------------------------------------
    # plt.legend(["terms", "docs"], loc=0)
    plt.tick_params(axis='both', which='major', labelsize=6)
    plt.tick_params(axis='both', which='minor', labelsize=6)
    
    plt.tight_layout()
    plt.savefig(FILENAME_PLOT, dpi=300, bbox_inches='tight', pad_inches=0.05)
    plt.close(fig)  


def latent_semantic_analysis():    
    print(">>> START Latent-Semantic-Analysis!!")
    print()

    print("[Msg] Get word-counts file list")
    counts_file_list = os.listdir(DIRNAME_WORDS)

    print("[Msg] Read/Create the Words-Docs matrix")
    text_terms, text_docs, tfidf = read_words_docs_matrix(counts_file_list, threshold_tf=THRESHOLD_KEY_WORDS)

    print("[Msg] Latent semantic analysis")
    lsa(text_terms, text_docs, tfidf, p=THRESHOLD_LSA_SIGMA)

    print()
    print(">>> STOP Latent-Semantic-Analysis!!")


if __name__ == "__main__":
    latent_semantic_analysis()
