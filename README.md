# News-Analysis
In this project, there are three parts of it: 1.News crawler, 2.Word segmentation and 3. Words visualization.<br />

## News Crawler
In this code, it will connect to chinatimes website and crawl news of a specific topic. For each topic, the news crawler will collect the page's URL of a topic, then collect news URLs of each page, and save the news data to json files in the "news" folder. <br />

## Word Segmentation
In this code, the news data will be processed by removing stopwords and user defined directory. The words of cleaned news data will be segmented from paragraphs by using the jieba library. Final, the segmented words statistics will be saved to json files in the "words" folder.<br />

## Words Visulization
In this code, the words will be used to create TERMS-DOCS (TD) matrix, and TD matrix will be processed by using singular value decomposition (SVD) to reduce dimensions of TD matrix. Last, the multidimensional scaling (MDS) or t-distributed Stochastic Neighbor Embedding (t-SNE) is used to project the reduced TD matrix to a 2-d space by using for words visulization.<br />

# Contact
1.If you have any questions please email to yuhisnag.fu@gmail.com.

Yu-Hsiang Fu, 20180321 updated.
