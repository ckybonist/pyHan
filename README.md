# pyHan

## 介紹
此專案爬取中國時報、聯合報 及 Yahoo新聞的新聞資料，並對新聞進行分詞，最終產生各種長度的詞彙頻率。

## 分詞
本專案首先以 [Ngrams](https://ai.googleblog.com/2006/08/all-our-n-gram-are-belong-to-you.html) 產生初步的
辭彙庫，並基於 ngrams 詞彙庫來進行 [Maximum Matching](http://www.52nlp.cn/maximum-matching-method-of-chinese-word-segmentation) 
分詞產生另一組辭彙庫。

## 爬蟲
主要是針對新聞網站提供的 RSS 去爬取資料，使用的函式庫包括：

- feedparser: 解析 RSS feed
- urllib and requests: 解析網址和發送 http 請求
- beautifulsoup4: 解析 HTML

## 輸出
- 此程式輸出長度為 2 ~ 5 的詞彙，檔案皆置於 `output/`
- `output/lexicon`: 裡面有 MM.json 及 Ngrams.json 兩個檔案，分別紀錄了兩種分詞方法所產生的詞彙
- `output/stats/grams`: 此路徑中含有 ngrams 方法統計出的日、月、年熱門詞彙
