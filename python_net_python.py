# -*- coding: utf-8 -*-
"""
Created on Wed May 11 16:17:11 2022

@author: bdgcx
"""

#====================================================
#爬取PubMed论文基本信息
#====================================================
'''
论文题目、摘要、作者、期刊、发表日期、DOI编号等
指定关键词，如lung cancer
爬取前5页的论文信息

1.分析URL规则
https://pubmed.ncbi.nlm.nih.gov/?term=lung%20cancer&format=abstract&page=3
  网址相关信息                     固定不变              格式设置      1~5页
   (固定不变)                   (爬取前确定)             (固定不变)    (程序中循环)

2.分析目标元素
F12打开开发者工具，查看题目、摘要、作者、DOI号的源代码
'''

from base64 import b16decode
from pyparsing import FollowedBy
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import pandas as pd
#pubmed基础网站
pubmed_url='https://pubmed.ncbi.nlm.nih.gov/'
#需要搜素的关键字
kw='lung+cancer'
#需要搜素的文章格式
fmt='abstract'

#hd={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0','User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3741.400 QQBrowser/10.5.3863.400'}
headers={'User-Agent':'UserAgent().random'}
#headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
paper_data=pd.DataFrame(columns=['title','authors','doi','abstract'])
#循环获取前5页源代码并提取信息
for num in range(1,6):
    response=requests.get(pubmed_url,
                          params={'term':kw,
                                  'format':fmt,
                                  'page':str(num)},
                          headers=headers)    
    response.raise_for_status()
    response.encoding=response.apparent_encoding 

    #print(response.url)
    soup=BeautifulSoup(response.text,'html.parser')
    paper_list=soup.find_all('div',attrs={'class':'results-article'})
    
    paper_record={}
    for paper in paper_list:

        article=paper.article
        
        title=[]
        titles=article.h1.a.strings #string只返回主标题列表，strings返回主标题和副标题
        for s in titles:
            title.append(s.strip())#strip用于去除字符串头尾的空行(包括\n,\t等)
        #print(''.join(title))
        paper_record['title']=''.join(title)

        authors=[]
        if article.find('i',attrs={'class':'empty-authors'}):
            authors.append('No author listed')
        else:
            author_list=article.find_all('a',attrs={'class':'full-name'})
            for author in author_list:
                authors.append(author.string.strip())
        #print(','.join(authors))
        paper_record['authors']=','.join(authors)

        doi=article.find('a',attrs={'class':'id-link'})
        if doi is None:
            paper_record['doi']='No DOI'
        else:
            paper_record['doi']=doi.string.strip()
        
        abstract=[]
        if article.find('i',attrs={'class':'empty-abstract'}):
            paper_record['abstract']='No abstract avilable'
        else:
            content=article.find('div',attrs={'class':'abstract-content selected'})
            abstracts=content.find_all('p')#报错：TypeError: 'NoneType' object has no attribute 'find_all'可能是反爬虫原因
            for item in abstracts:
                for sub_content in item.strings:
                    abstract.append(sub_content.strip())
            #print('\n'.join(abstract))
            paper_record['abstract']='\n'.join(abstract)

        #写入论文dataframe
        paper_data=paper_data.append(paper_record,ignore_index=True)

#输出至文件
paper_data.to_excel('lung_cancer_papers.xlsx',index=False)


#====================================================
#期刊数据的自动爬取
#====================================================           
#目标：从ScienceDirect中选择某个子领域，爬取该领域下期刊近期论文的见刊信息统计每个期刊的平均审查时间及平均在线发表时间
#分析网址规则 https://www.sciencedirect.com/browse/journals-and-books/?contentType=JL&subject=hepatology
#                                                 基础网址             内容类型         领域名称
import requests
from fake_useragent import UserAgent
from lxml import etree
from bs4 import BeautifulSoup
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from pathlib import Path
import time
import matplotlib.pyplot as plt
import numpy as np
#定义日期计算函数
def caldays(day1,day2):
    time_array1 = time.strptime(day1, "%d %B %Y")
    timestamp_day1=int(time.mktime(time_array1))
    time_array2 = time.strptime(day2, "%d %B %Y")
    timestamp_day2=int(time.mktime(time_array2))
    result=(timestamp_day2-timestamp_day1)//60//60//24
    return result

#1.获取子领域的期刊列表
# 获取子领域下所有期刊页面源代码
url='https://www.sciencedirect.com/'
sd_url='https://www.sciencedirect.com/browse/journals-and-books/'
sd_response=requests.get(sd_url,
                         params={'contentType':'JL'},
                                 #'subject':'hepatology',
                         headers={'User-Agent':UserAgent().random},
                         timeout=30)
sd_response.raise_for_status()
sd_response.encoding=sd_response.apparent_encoding
#提取子领域下所有期刊的名称
jl_selector=etree.HTML(sd_response.text)
jl_name_xpath='''//li[@class="publication u-padding-xs-ver js-publication"]
                   //span[@class="publication-text"]/text()'''  #''' '''表示换行
jl_name_list=jl_selector.xpath(jl_name_xpath)
#提取子领域下所有期刊的跳转链接列表
jl_xpath='''//li[@class="publication u-padding-xs-ver js-publication"]
              /a/@href'''
jl_href_list=jl_selector.xpath(jl_xpath)

#驱动浏览器
#browser=webdriver.Chrome()
browser=webdriver.Edge()
browser.get(url)

#2.循环期刊链接列表
for jl_name,jl_href in zip(jl_name_list,jl_href_list):
    #print(jl_name,jl_href) 输出的是相对路径，需要拼接成绝对路径
    jl_issues_url=url+str(jl_href)+'/issues'
    jl_issues_response=requests.get(jl_issues_url,
                                    headers={'User-Agent':UserAgent().random})
    jl_issues_response.raise_for_status()
    jl_issues_response.encoding=jl_issues_response.apparent_encoding

    #创建用于储存期刊数据的空dataframe
    df=pd.DataFrame(columns=['Title','Info'])
    #获取该期刊issues集合的页面源代码
    issues_selector=etree.HTML(jl_issues_response.text)
    #提取issues相关跳转链接列表
    issues_xpath='''//li[@class="according-panel js-according-panel"][1]
                      /a[@class="anchor js-issue-item-link text-m"]/@href'''
    issues_list=issues_selector.xpath(issues_xpath)

    #设置论文计数器
    paper_counter=0
    #设置标识位用于储存当前期刊是否获得了足够的论文进行计算，默认为否
    counter_flag=False

#3.循环issues链接列表
    #获取某个issue页面数据
    for issue in issues_list:
        #获取完整网址
        issue_url=url+str(issue)
        #获取页面源代码
        issue_response=requests.get(issue_url,
                                    headers={'User-Agent':UserAgent().random})
        issue_response.raise_for_status()
        issue_response.encoding=issue_response.apparent_encoding
        #获取该issue下论文跳转链接列表
        paper_selector=etree.HTML(issue_response.text)
        paper_xpath='''//ol[@class="js-article-list article-list-items"]
                         //a[@class="<a class="anchor article-content-title u-margin-xs-top u-margin-s-bottom"]/@href'''
        paper_list=paper_selector.xpath(paper_xpath)
#4.循环论文链接列表
        #获取该文章的题目
        for paper in paper_list:
             #获得完整网址
            paper_url=url+str(paper)
            #打开对应网址
            browser.get(paper_url)
            browser.implicitly_wait(10)#设置一个隐性时间，等待页面加载完成
            #设置异常处理,在页面加载失败时，将错误记载下来，然后继续运行，避免工作白费
            try:
                #获得文章题目
                paper_record={}
                title=browser.find_element(By.ID,'screen-reader-main-title')
                paper_record['Title']=title.text
                #点击show more按钮
                browser.find_element(By.ID,"show-more-btn").send_keys(Keys.ENTER)#利用回车打开showmore按钮
                #chains=ActionChains(browser)
                #chains.click(show_more).perform()
                #获取论文相关数据
                paper_record['Info']=browser.find_element(By.XPATH,'//div[@id="banner"]/div/p').text
                #data=browser.find_element(By.XPATH,'//div[@id="banner"]/div/p')
                #paper_record['Info']=data.text

                #将论文信息存储于期刊的dataframe中
                df=df.append(paper_record,ignore_index=True)
                #计数器加1
                #paper_counter=paper_counter+1
                paper_counter+=1
            except Exception as e:
                    print('Error',e)
            #设置标识位, 即设置每个期刊抓取的论文总篇数，满足预设数量时，设置标识位为True
            #如果已经爬取30篇论文信息则该期刊停止爬取
            paper_num=30
            if paper_counter==paper_num:
                counter_flag=True
                break
        if counter_flag:
            break
    #5.将每个期刊数据写入文件中
    file='C:/Users/bdgcx/OneDrive/python'+str(jl_href)+'.xlsx'
    df.to_excel(file,index=False)
#关闭浏览器
browser.quit()

#6.循环每个期刊的数据文件
#存放期刊数据的文件夹
fold=Path('C:/Users/bdgcx/OneDrive/python')
#创建DataFrame用于储存所有期刊数据
data=pd.DataFrame(columns=['Name','Accept Days','Online Days'])
#提取日期的正则表达式
receive_rule='Receice\s([\w\s]+)'
accept_rule='Accepted\s([\w\s]+)'
online_rule='online\s([\w\s]+)'
#7.提取每个文件中论文的相关日期并计算平均天数
for f in fold.rglob('*.xlsx'):
    receive_online_sum=0
    receive_online_counter=0
    #提取日期
    df=pd.read_excel(f)
    #计算日期差、累计日期差，计算平均日期
    for index in range(len(df)):
        info=df.iloc[index,1]
        #获取每个论文的日期
        receive_date=re.findall(receive_rule,info)
        accept_date=re.findall(accept_rule,info)
        online_date=re.findall(online_rule,info)
        #计算日期差及累计日期差
        if len(receive_date)!=0 and len(online_date)!=0:
            receive_to_online=caldays(receive_date[0],online_date[0])
            receive_online_sum=receive_online_sum+receive_to_online
            receive_online_counter=receive_online_counter+1
        
        if len(receive_date)!=0 and len(accept_date)!=0:
            receive_to_accept=caldays(receive_date[0],accept_date[0])
            receive_accept_sum=receive_accept_sum+receive_to_accept
            receive_accept_counter=receive_accept_counter+1
    
    #计算平均日期
    receive_online_avg=0
    if receive_online_counter!=0:
        receive_online_avg=receive_online_sum/receive_online_counter
    receive_accept_avg=0
    if receive_accept_counter!=0:
        receive_accept_avg=receive_accept_sum/receive_accept_counter
    
    if receive_online_avg!=0 or receive_accept_avg!=0:
        record={}
        record['Name']=f.stem
        record['Online Days']=round(receive_online_avg,2)
        record['Accept Days']=round(receive_accept_avg,2)
        data=data.append(record,ignore_index=True)

#8.计算每个期刊的平均天数并进行绘图
plt.figure(figsize=(20,10))
x=np.arange(1,len(data)+1)
plt.bar(x,data['Accept Days'],width=0.3,color='lightblue',label='Accept Days')
plt.bar(x+0.3,data['Online Days'],width=0.3,color='deepskyblue',label='Online Days')
plt.legend()
plt.ylim(0,365)
plt.xticks(x+0.15,x)
plt.ylabel('天数')
plt.xlabel('期刊编号')
plt.rc_params['font.sans-serif']=['SimHei']
#设置Accept Days的数字显示
for a1,b1 in zip(x,data['Accept Days']):
    text1=b1
    if b1>365:
        b1=365
        text1='>1 year'
    plt.text(a1,b1,text1,fontsize=8,verticalalignment='bottom',horizontalalignment='center')
#设置Online Days的数字显示
for a2,b2 in zip(x,data['Online Days']):
    text2=b2
    if b2>365:
        b2=365
        text2='>1 year'
    plt.text(a2+0.3,b2,text2,fontsize=8,va='bottom',ha='center')
#设置编号对应期刊的内容显示
name_label=[]
for index,name in zip(x,data['Name']):
    name_text=str(index)+':'+name
    name_label.append(name_text)

names='\n'.join(name_label)
plt.text(17,200,names,fontsize=8,ha='left')
plt.show()
#====================================================
#网络爬虫
#====================================================
'''
是一种按照一定的规则，自动地抓取网络信息的程序或脚本

1.通用爬虫
搜索引擎的爬虫系统，追求大的爬行覆盖范围
2.聚焦爬虫
针对某种内容爬虫，只对特定的网站进行爬取

爬虫的一般流程：
1.获取网页内容：给一个网址发送请求，该网址会返回整个网页的数据
Urllib库: python内置HTTP请求库,一系列用于操作URL的功能
Requests库:模拟浏览器操作，下载网页内容
Selenium库:模拟人自动与网站交互，支持所有主流的浏览器
2.解析网页内容：从整个网页数据中提取想要的数据
re库:python内置正则表达式模块,解析速度较快
beautifulsoup库:结构化网页数据，轻松获取网页内容
lxml库:轻松处理XML和HTML文件,支持XPath解析方式,解析效率非常高
3.保存数据：数据可保存在数据库或文件中
pymysql: python实现的MySQL客户端操作库
pymongo: 直接连接mongodb数据库进行查询操作

Scrapy爬虫框架:爬取网站数据，提取结构性数据
全能型选手，可以覆盖上述整个流程
'''

#====================================================
#网页的组成与结构
#====================================================
'''
网络的工作原理

常见的网络结构模式
1.客户端/服务器模式（Client/Server,C/S）爬虫不可用
2.浏览器/服务器模式（Brower/Server,B/S）爬虫可用

Uniform Resource Locator: URL,统一资源定位符，是互联网上的文件路径
网址完整模式 https://www.dxy.cn:443/index.html
1.协议：告诉浏览器使用哪种功能，如http,https,ftp
2.服务器地址：服务器的名称或IP地址，如www.dxy.cn
3.端口：获取服务器资源的入口，如443
4.资源路径：文件在服务器中的位置

Hyper Text Markup Language: HTML 超文本标记语言
HTML文件的后缀名有.html,.htm
不是一种编程语言，而是一种标记语言
1.给文本加上表明文本含义的标签（Tag）,让用户（人或程序）能对文本得到更好的理解
HTML的标签是由尖括号包围的关键词，如<html>
HTML标签通常是成对出现的，如<html> 开始标签和</html> 结束标签
2.所有的HTML文档都应该有一个<html>标签
3.<html>标签可以包含两个部分<head>和<body>
<head>存放网页的元信息，不会被显示在网页中
<body>存放网页的具体内容

示例：
<html>

<head>
<title>我的第一个HTML网页</title>
</head>

<body>
<p>body 元素的内容会显示在浏览器中。</p>
</body>

</html> 

HTML常见的标签
1.标题
通过<h1>~<h6>标签来定义
2.段落
通过<p>标签来定义
3.链接
通过<a>标签来定义
4.图片
通过<img>标签来定义,是一个自闭合标签

示例
<html>
<body>

<h1>这是一个一级标题</h1>
<h2>这是一个二级标题</h2>
<p>这是一个段落。</p>
<p><a href="https://pubmed.ncbi.nlm.nih.gov/">这是pubmed的链接</a></p>
<p>

一幅图像
<img src="C:/Users/bdgcx/OneDrive/图片/壁纸/099e7d0f3bf529381a800f483044c98.jpg"
width="128" height="128" />
</p>

</body>
</html>

查看网页源代码

网络爬虫的主要原理就是在网页的源代码中将我们需要的内容提取出来

以Chrome浏览器为例：
方法1
打开一个网页
右键单击空白处
点击右键菜单中的“查看源代码”

方法2（推荐）
打开一个网页
按F12打开开发者工具
选择“Elements”
点击框加箭头标志可进入选择元素模式

HTML决定了网页的结构和内容，可以将HTML看作房子的骨架与结构
'''

#====================================================
#CSS与JavaScript
#====================================================
'''
Cascading Style Sheet: CSS 层叠样式表
用来控制HTML中所有元素如何展现
可以将CSS看作房子的外观

JavaScript
使HTML具有交互性
属于HTML和 Web的编程语言
对页面行为进行编程，负责页面的交互逻辑
'''

#====================================================
#请求与内容抓取
#====================================================
'''
HTTP的请求与响应
Hyper Text Transfer Protocol 超文本传输协议
超文本：超出普通文本，如网页就是一种超文本
协议：互联网中通信时，计算机之间必须共同遵守的规定或规则
作用：用于网络服务器传输超文本到本地浏览器的传送协议

HTTP协议使客户端发起请求，服务器回送响应
HTTP中常用的是Get和Post请求参数
1.Get请求
通常是从指定的资源请求数据，即从服务器上获得数据
不带参数的Get请求：http://www.baidu.com
带参数的Get请求：http://www.baidu.com?wd=python 
(参数写入URL，参数是key=value格式，多个参数之间用&连接)
2.Post请求
向指定的资源提交要被处理的数据，即向服务器上传数据
参数不再写入URL，而是放入请求报文中进行传输


HTTPS是HTTP协议的安全版本

一个HTTP请求由请求行(request line),请求头部(request header),
空行和请求体四部分组成
一个HTTP响应由状态行，响应头部和响应正文3部分组成
状态码是响应报文状态行的中包含的一个3位数字，表明特定的请求是否被满足
如果未满足，原因是什么
例
1XX 通知信息 100：服务器正在处理客户请求
2XX 成功 200：请求成功（OK）
3XX  重定向 301：页面改变了位置
4XX 客户错误 403：禁止的页面 404：页面未找到
5XX 服务器错误 500:服务器内部错误 503：以后再试
'''

'''
使用Requests库获取网页源代码
适合爬取网页的HTML文档信息，但无法解析CSS,JavaScript代码
'''
import requests

requests.get()
requests.post()

#不带参数的Get请求
response=requests.get('http://www.baidu.com')
response.raise_for_status()
response.encoding=response.apparent_encoding
print(response.text)#输出请求的源代码
'''
reponse的属性及含义
response.status_code  状态码
response.text  文本形式的响应内容（response.content编码后的结果）
response.url 请求url
response.headers  响应头信息
response.encoding  获取响应内容编码
response.apparent_encoding  从内容中分析响应内容的编码方式（备选编码方式）
response.content  bytes形式的响应内容

response.raise_for_status  判断状态码是否为200
response.encoding=response.apparent_encoding 避免乱码
'''
#带参数的Get请求,使用params接收参数，参数通常写成字典模式
response=requests.get('http://www.baidu.com/s', #进入百度的搜索页面
             params={'wd':'python'})
response.raise_for_status()
response.encoding=response.apparent_encoding
print(response.url)#输出网址在浏览器中打开看一下是否正确
#将请求结果写入文件
file=open('C:/Users/bdgcx/Desktop/baidu_python.html',
          'w',
          encoding='utf-8')
file.write(response.text)
file.close()

# post使用data接收参数，参数通常写成字典模式
data={
      'dxy':'python',
      'key2':'value2',
      'arr':['one','two']
      }
requests.post('http://httpbin.org/post',#专门用于测试get和post的网站
              data=data)

response=requests.post('http://httpbin.org/post', 
              data={'dxy':'python','key2':'value2'})
response.raise_for_status()
response.encoding=response.apparent_encoding
file=open('C:/Users/bdgcx/Desktop/post.html',
          'w',
          encoding='utf-8')
file.write(response.text)
file.close()

'''
使用Selenium模拟浏览器操作
Selenium是一个浏览器自动测试组件
通过驱动浏览器，完全模拟浏览器操作
支持跨不同浏览器、平台和编程语言的自动化
由于Selenium解析了CSS,JavaScript所以相对requests爬虫效率要低

Selenium环境搭建
1.安装Selenium: pip install selenium
2.安装浏览器驱动程序
查看浏览器版本，根据浏览器和版本号进行下载
Chrome: https://sites.google.com/a/chromium.org/chromedriver/downloads
Edge: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
将解压得到的文件放入指定文件夹中
windows系统：Anaconda安装目录下的Scripts文件夹
默认安装时：C:\ProgramData\Anaconda3\Scripts
Mac系统：/usr/local/bin/
'''
#Selenium导入
from selenium import webdriver
#驱动目标浏览器
browser=webdriver.Chrome()
browser=webdriver.Edge()
#打开目标网址
browser.get('http://www.baidu.com')
#定位元素
'''
 find_element()查找单个元素
 find_elements()查找多个元素，返回一个列表
 查找方法及对应属性
 id  By.ID
 name  By.NAME
 class name   By.CLASS_NAME
 tag name    By.TAG_NAME
 link text   By.LINK_TEXT
 partial link text    By.PARTIAL_LINK_TEXT
 xpath    By.XPATH
 css selector   By.CSS_SELECTOR
 
'''
#Chrome浏览器F12出现源代码后点击框加箭头图标，将鼠标至于想要定位的元素就会高亮源代码
from selenium.webdriver.common.by import By
input_elem=browser.find_element(By.ID,'kw') #Chrome中百度的搜索框
submit_elem=browser.find_element(By.ID,'su') #Chrome中百度的百度一下按钮

#等待页面加载
'''
当一个页面被加载到浏览器时，该页面内的元素可以在不同的时间点被加载
waits提供了一些操作之间的时间间隔
主要是定位元素或针对该元素的任何其他操作
'''
#使用前导入
from selenium.webdriver.support.ui import WebDriverWait
#创建browser时设置全局元素等待超时的事件（隐式等待）
browser=webdriver.Chrome()
browser.implicitly_wait(10)#表示查找元素时超时时间是10秒
elem=browser.find_element(By.ID,'kw')

#模拟鼠标操作
#使用webdriver提供的ActionChains类模拟鼠标事件
#导入
from selenium.webdriver import ActionChains
#调用
chains=ActionChains(browser)
chains.click(submit_elem).perform()#左击
chains.context_click(elem).perform()#右击
chains.double_click(elem).perform()#双击
chains.move_to_element(elem).perform()#鼠标悬停

#示例
from selenium import webdriver
from selenium.webdriver import ActionChains
browser=webdriver.Chrome()
chains=ActionChains(browser)
browser.get('...')
#定位到要悬停的元素
elem=browser.find_element(By.LINK_TEXT,'...')
#对定位到的元素执行左击操作
chains.click(elem).perform()
#perform():执行操作，所有鼠标操作调用其他操作方法后，都要再次调用执行操作，表示执行某个鼠标操作

#模拟键盘操作
#导入key模块
from selenium.webdriver.common.keys import Keys
#常用的键盘操作
input_elem.sendkeys('Pythona')#输入内容
import time
time.sleep(3)#休眠3秒
input_elem.sendkeys(Keys.Back_SPACE)#退格
elem.sendkeys(Keys.SPACE)#空格
elem.sendkeys(Keys.ENTER)#回车
elem.sendkeys(Keys.CONTROL,'c')#ctrl+c,复制
elem.sendkeys(Keys.CONTROL,'a')#ctrl+a,全选
elem.sendkeys(Keys.CONTROL,'v')#ctrl+v，粘贴
elem.clear()#清空内容

#模拟下拉框操作，使用Select类
from selenium.webdriver.support.select import Select
#返回所有选项
pro=Select(browser.find_element(By.ID,'pro'))
for option in pro.options:
    print(option.text)
#（取消）选中某一个选项
#1.通过value属性
pro.select_by_value('bj')
pro.deselect_by_value('bj')
#2.通过index索引
pro.select_by_index(0)
pro.deselect_by_index(0)
#3.通过标签文字
pro.select_by_visible_text('广东')
pro.deselect_by_visible_text('广东')

#示例
from selenium.webdriver.support.select import Select
browser.get('http://sahitest.com/demo/selectTest.htm')
from selenium.webdriver.support.ui import WebDriverWait
browser.implicitly_wait(10)#表示查找元素时超时时间是10秒
pro=Select(browser.find_element(By.ID,'s1'))
for option in pro.options:
    print(option.text)
pro.select_by_value('o2')


#截图操作
#整个窗口截图并保存
browser.get_screenshot_as_file('./baidu_python.png')
#指定元素截图并保存
#找到目标元素
elem=browser.find_element(By.ID,'kw')
#截取搜索框元素
elem.screenshot('./kw.png')
#后缀名建议写.png,否则会有warning提示

#关闭浏览器
#关闭当前窗口
browser.close()
#关闭所有窗口
browser.quit()

#====================================================
#解析与信息提取
#====================================================
'''
利用正则表达式
'''
import re
import requests

response=requests.get('http://www.baidu.com/')
response.raise_for_status()
response.encoding=response.apparent_encoding

title=re.findall(r'<title>(.*?)</title>', response.text)
print(title[0])
    
'''
基于Beauyiful Soup的方法
Beauyiful Soup是一个HTML解析器
提供简单的从HTML文件中提取信息的python库
将HTML转成为一个标签树

示例HTML文件：
<html>

<head>
<title>The Dormouse's story</title>
</head>

<body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters;and their names were
  <a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
  <a href="http://example.com/lacie" class="sister" id="link2">Lacie</a>and
  <a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
  and they lived at the bottom of a well.</p>
  
</body>

</html> 
'''
#导入
from bs4 import BeautifulSoup
#常见解析流程
#1.获取某个网页的html代码，如利用requests,selenium等库
response=requests.get('http://www.baidu.com')
response.raise_for_status()
response.encoding=response.apparent_encoding
html=response.text
#2.利用BetifulSoup解析html代码
soup=BeautifulSoup(html,'html.parser')
print(soup.prettify())#输出排版后的HTML内容

#BeautifulSoup中搜索单一对象
#soup.tag_name只能获取当前标签下的第一个标签
soup.head()
#匹配<head><title>The Dormouse's story</title></head>
soup.title()
#匹配<title>The Dormouse's story</title>

#soup.find('tag_name')用于查找符合查询条件的第一个标签节点
soup.find('head')#与soup.head()同效果
soup.find('p',attrs={'class':'story'})#匹配第2个<p>的内容

#BeautifulSoup中搜索多个对象
soup.find_all('tag_name')#查找所有符合条件的标签节点，返回一个列表
soup.find_all('title')
#匹配[<title>The Dormouse's story</title>]
soup.find_all('a')
# 匹配[<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
# <a href="http://example.com/lacie" class="sister" id="link2">Lacie</a>,
# <a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>]

#BeautifulSoup获取标签对象的相关信息

#例<p class="title"><b>The Dormouse's story</b></p>
#获得该标签的名称
soup.p.name()#得到结果为p
#获得该标签的属性
soup.p.attrs()#得到结果为{'class':['title']}
#获得该标签内的内容文字
soup.p.string()#得到的结果为The Dormouse's story

'''
基于XPATH的方法
XPATH是一种可以确定HTML文档中某部分位置的语言
XML Path Language 即XML路径语言
最初用于搜寻XML文档，但是同样适用于HTML文档的搜索
XPATH基于树状结构，使用路径表达式在XML/HTML文档中选取节点

<html> 文档节点
<b>The Dormouse's story</b> 元素节点
class="story" 属性节点
Elsie 文本节点
'''

#XPATH搜索指定元素的方法
#python中使用xpath
from lxml import etree
#使用etree对获取网页源代码进行解析
data=etree.HTML(response.text)
#利用XPATH获取指定元素
elem=data.xpath('//title')#括号里是元素的XPATH路径字符串

'''
XPATH常用的路径表达式
/  从根节点开始查找,是获取直接子节点 /html/body/p/b
//  从当前节点向后搜索所有后代节点，而不考虑他们的位置   //b等同于/html/body/p/b
nodename  从当前节点选择名称为nodename的节点，即选取此节点的所有子节点   //title    //*可以查找所有节点
.  选取当前节点
..  选取当前节点的父节点
@attrib  从当前节点选择文档中的属性
[@attrib='value'] 从当前节点选择文档中属性为attrib的节点，并且属性值为value(选取给定属性具有给定值的所有元素)
text() 从当前节点选择文档中的文本内容
'''

#====================================================
#框加与反爬机制
#====================================================
#Scrapy框架
#官方文档：https://docs.scrapy.org/en/latest/
#中文文档：https://scrapy-chs.readthedocs.io/zh_CN/0.24/intro/tutorial.html

#Scrapy的安装
conda install -c conda-forge scrapy
#Scrapy的使用
#创建一个Scrapy项目：scrapy startproject mySpider(项目名称)
'''
该项目的目录结构如下：
scrapy.cfg
mySpider/
    __init__.py
    items.py
    middlewares.py#中间件文件
    pipelines.py#管道文件
    settings.py#配置文件
    spiders/
        __init__.py
'''
#定义需要爬取的数据(items.py文件)
#编写提取数据的爬虫(在spiders文件夹中)
#执行爬虫并保存数据
scrapy crawl mySpider -o items.json

#反爬虫
'''
爬虫的合法性
多数网站允许将爬虫爬取的数据用于个人使用或科学研究
一下几种数据不能爬取：
1.个人隐私数据：如姓名、手机号、年龄、血型、婚姻状况等，爬取此类数据将触犯个人信息保护法
2.明确禁止他人访问的数据：如用户设置了账号密码等权限设置，进行了加密的内容
robot.txt协议
通过位于网站根目录下的robot.txt文件，提示网络机器人哪些网页可以被爬取，哪些网页不可以被爬取

限制爬虫程序访问服务器资源和获取数据的行为称为反爬虫
'''
#常见反爬虫操作：
#1.User-Agent请求头验证
#将要请求的User-Agent值伪装成一般用户登陆网站时使用的User-Agent值
#随机生成User-Agent添加到header中
#借助fake_useragent
#a.安装：pip install fake_useragent
from fake_useragent import UserAgent
#b.使用UserAgent生成随机User-Agent值
import requests
from fake_useragent import UserAgent

headers = {'User-Agent': UserAgent().random}
r = requests.get('http://www.baidu.com', headers=headers)
#使用Selenium模拟使用浏览器
#2.IP地址验证和限制访问频率
#使用ip代理池、降低访问频率
#requests降低访问频率
#a.每次访问后设置等待时间，使用time.sleep(等待时间)实现请求间隔
import time 
import random
time.sleep(random.randint(1,9))
#b.设置代理访问 免费代理：西刺代理、快代理  付费代理
proxie={'http':'http://175.42.129.XXX:9999',
        'https':'https://175.44.108.XXX:9999'}
reponse = requests.get(url='http://www.baidu.com',proxie=proxie)
#3.图形验证码
#a下载或截图验证码，使用图像识别程序进行自动识别 利用pytesseract识别验证码
#先安装Tesseract-OCR并配置环境变量
#安装：pip install pytesseract
#先下载或截图验证码，使用pytesseract识别验证码
import pytesseract
from PIL import Image
image = Image.open('验证码.jpg')
code=pytesseract.image_to_string(image)
#b.使用Selenium实现鼠标的点击、拖动、释放等行为

















