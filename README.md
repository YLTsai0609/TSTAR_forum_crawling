# 輿情偵測-資料獲取
![iamge](https://github.com/YLTsai0609/TSTAR_forum_crawling/blob/master/Data%2BScience%2BWorkflow_pic.jpg)
[source](http://sadiestlawrence.com/blog/data-science-workflow)

需要成為一個 Data Scientist 除了需要modeling及analytics的技巧之外，常常也會遇到需要外部資料獲得我們想要的結果。本專案實作了從mobile01爬取具有"台灣之星", "台星"等具有台灣之星相關關鍵字的輿情監測資料獲取實作，以下為可落地的商業價值及所使用技術

*************************************************

## 商業價值

* 在企業內通常由人為監管輿情(e.g. 例如某個部門的工作為監看各大論壇中鄉民對於公司企業，產品，新品的評價)，透過本專案延伸，可減少人員統整正面/負面文章的時間，大幅降低相關人員工作loading，同時提升相關人員產能。
* 針對新品推出市場之前，利用過去新品(新聞)推出市場前相關聲量，作為新品(新聞)推出時的聲量預測benchmark，協助決策輔助。
*************************************************

## 爬取方法
每天進入mobile01的[手機討論版](https://www.mobile01.com/topiclist.php?f=18)，以"台灣之星"，"台星"，為關鍵字，爬取前3頁內容。
*************************************************

## 爬取欄位

|欄位|描述|
|---|----|
|title|文章標題|
|publish_timestamp|發文日期時間|
|page|總共頁數|
|author|作者|
|popularity|人氣|
|replys|回應數|
|content|內容|

其中content(內容)為一個json array，內容包含了:

|欄位|描述|
|---|----|
|host / not host|是否為發文人|
|name|使用者暱稱|
|member_level|會員等級|
|personal_score|個人積分|
|written_timesatamp|回應日期時間|
|discussion|回應內容|

其中回應內容也包含了html標籤，取用需要再經過資料清理

*************************************************  
## 技術

* Python(
numpy==1.16.2
pandas==0.24.2
requests==2.21.0
bs4
sqlalchemy
logging )
* Google Cloud (CloudSQL, Compute Engine )
* Linux tool (crontab) 
* MySQL viewer (Sequel Pro)

*************************************************


## Future Work

* 爬取各種不同難度的資料(e.g. 會被js遮蔽的元件(購物車價格) [使用 PhantomJs, Selenium](https://codertw.com/%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80/509196/) )
* 更廣的資訊及效率 ([使用multi-processing](https://blog.csdn.net/qq_23926575/article/details/76375042) )
* 方便維護及團體協作 ([認識MVC架構及實作](https://blog.csdn.net/u012491646/article/details/83932966))
