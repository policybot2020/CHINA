#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Policybot.io

# This file is part of Policybot.
#
#    xjp traceur is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    xjp traceur is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pyComtrade.  If not, see <http://www.gnu.org/licenses/>.
# ====================================================================
# 12.29.2021 updates by Jianyin Roachell.

from sys import exit
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.common.keys import Keys
from re import findall
from argparse import ArgumentParser
from random import randint, random
from requests import get
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import io
import re
import pandas as pd
from pandas import DataFrame
import os
import random
import datetime
from requests import get
from re import findall
from IPython.core.display import display, HTML
import sys
import time
import jieba
from jieba import analyse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib
from googletrans import Translator


######################### S t a r t  ################################
date = datetime.datetime.now().strftime('%Y-%m-%d') # today

def scrape_news(url):
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import TimeoutException
    import random
    #driver = webdriver.Firefox()
    from webdriver_manager.chrome import ChromeDriverManager
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    # another forloop that goes into each link and get data on:
    driver.implicitly_wait(random.randrange(30))

    if re.compile(r'(?:.doc)|(?:.pdf)').findall(str(url)): # check whether link is pdf or word doc
        d = {
                'article_source' :['none'], # /html/body/div/div[4]/div[7]/div[1]
                'body' :['none'],
        }

        X = pd.DataFrame(data=d)
        driver.close()
        return X
    # another forloop that goes into each link and get data on:
    else:
        time.sleep(3)
#################  if there is a error from socket, then randomize another one
        driver.get(url)
        driver.refresh()
        if re.compile(r'(?:.doc)|(?:.pdf)').findall(str(driver.current_url)): # check whether link is pdf or word doc
            d = {
                'article_source' :['none'],
                'body' :['none'],
            }
        # NORMAL people's daily papges
        elif driver.find_elements_by_xpath('/html/body/div[5]/div[2]'):
            d = {
                'article_source' :[driver.find_elements_by_xpath('/html/body/div[5]/div[1]')[0].text], # /html/body/div/div[4]/div[7]/div[1]
                'body' :[driver.find_elements_by_xpath('/html/body/div[5]/div[2]')[0].text],
            }

        else:
            d = {
                'article_source' :['none'], # /html/body/div/div[4]/div[7]/div[1]
                'body' :['none'],
            }

    df = pd.DataFrame(data=d)
    driver.close()
    return df


#########################################

def xi_talks(date): #信息公开 > 政策文件
    from webdriver_manager.chrome import ChromeDriverManager
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get('http://jhsjk.people.cn/result?title=&content=&form=0&year=0&submit=%E6%90%9C%E7%B4%A2') # bilateral relations & main page http://www.china-botschaft.de/det/sgyw/
    driver.implicitly_wait(5)
    posts_contents = []
    links = []
    dates = []
    title = []
    driver.refresh()
    # xi newest speeches
    delay = 3
    #try:
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[2]/ul/li[1]/a')))
    except TimeoutException:
        #print("Timed out waiting for page to load")
        driver.refresh()
    spot = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]  # in total 33
    for i in spot:
        num = str(i)
        thatday = re.search(r'\d{4}-\d{2}-\d{2}', driver.find_element_by_xpath('/html/body/div[5]/div[2]/ul/li['+ num +']').text.replace("/", "-"))
        if thatday.group(): # prevent some links titles from
            if thatday.group()  == str(date):
            #if driver.find_element_by_xpath('//*[@id="docMore"]/tbody/tr/td/table/tbody/tr['+ num +']/td[2]').text.strip().split()[0] # if any of cross referencing 10 dates to today's date
                dates.append(thatday.group()) #.strip().split()[0]
                links.append(driver.find_element_by_xpath('/html/body/div[5]/div[2]/ul/li['+ num +']/a').get_attribute('href')) # then get their links
                title.append(driver.find_element_by_xpath('/html/body/div[5]/div[2]/ul/li['+ num +']').text)
                time.sleep(2)
        else:
            pass
      # Scrape the links by using the function: Scrape_policy:
    if not links:
        driver.close()
        return
    #############################
    for i in links:
        posts_contents.append(scrape_news(i))
        #driver.implicitly_wait(3); time.sleep(3); time.sleep(random.randrange(10))
        #############################
    X = pd.concat(posts_contents, axis=0).reset_index(drop= True) # concat all dataframes together
    X = pd.concat([pd.DataFrame({'link':links}), pd.DataFrame({'title': title}),pd.DataFrame({'published_date': dates}),X], axis = 1) #pd.DataFrame({'published_date': dates})]
    X = X.replace(r'^\s+$', "ERROR: may contain PDF doc or unknown format", regex=True)
    driver.close()
    #################################################
    return X

###############################################################
data = xi_talks(date) ###############################################################
data = data.replace(r'', "Note:pdf, picture, or infographic", regex=True)

################################ Get randomized keywords for Subject Line ###############
list_0 = data['title']
subject = jieba.analyse.extract_tags(str(list_0), topK=10, withWeight=True, allowPOS=('n'))
lines = []
for i in subject:
    lines.append(i[0])
print(lines)
# for attempt in range(5): # five attempts
#     try:
from googletrans import Translator
translator = Translator()
topics = translator.translate(','.join(lines[:5])).text
# except AttributeError as e:
#     topics = lines
subject = str('XJP Traceur: '+str(date) + ' with ' + str(len(data)) + ' new posts about '+ str(topics))
    # except AttributeError as e:
    #     print('cannot translate')
    #     break
################################################################################################



############################### Get Ready for HTML Codes ##########################################

from googletrans import Translator
all_news = []
all_news_en = []
translator = Translator()
divider = str('<hr width="50%" size="8" align="center"> <hr yesshade>')




######################  ALTERNATE ENGLISH AND CHINESE FORMAT ###########################
list1 = all_news_en
list2 = all_news
result = [None]*(len(list1)+len(list2))
result[::2] = list1
result[1::2] = list2

content = []
for i in result:
    content.append(', '.join(i))

content_txt = ' '.join(content)

# Can now input into a news letter or html code
