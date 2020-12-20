### ＮＩＳｆｅｅd back ### need line break, , bold the titles and qiandiao keywords
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


######################### L O G ################################
date = '2020-12-19'
#date = datetime.datetime.now().strftime('%Y-%m-%d') - datetime.timedelta(days=1)
# yesterday = datetime.datetime.today() - (datetime.timedelta(days=1))
# date = yesterday.strftime('%Y-%m-%d')
#date = datetime.datetime.now().strftime('%Y-%m-%d')

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
data.to_excel(r'C:\Users\ASUS\Desktop\policybot\policybot_venv\projects\xi_speech\_'+str(date)+'_daily_xi_monitor.xlsx',encoding ='utf_8_sig')

###############################################################
###############################################################
data = pd.read_excel(r'C:\Users\ASUS\Desktop\policybot\policybot_venv\projects\xi_speech\_'+str(date)+'_daily_xi_monitor.xlsx',encoding ='utf_8_sig')

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

def get_key_phrase(keyword,doc):
    """
    description: output sentences that contains the keyword and the sentence following.
    parameters:
        input:
            keyword: a string, in single quotes
            doc: a body of text in string or data['body'][0]
        output: a list of sentences that contain the keyword and +1
    """
    import sys
    # insert at 1, 0 is the script path (or '' in REPL)
    sys.path.insert(1, r'C:\Users\ASUS\Desktop\policybot\policybot_venv\official_library')
    from policybot_sentiment import cut_sent
    sent_list = cut_sent(doc)
        #################### WITH NEW GOOGLE TRANSLATE API LIMIT 400 characters ################
    xi_indice = [i for i, s in enumerate(sent_list) if keyword in s]
    xi_indice=list(set(xi_indice))
    try:
        return [sent_list[i] for i in xi_indice]
    except IndexError:
        return [sent_list[i] for i in xi_indice[:-1]]


############################### Get Ready for HTML Codes ##########################################
#def get_today_xi_speech(data):
from googletrans import Translator
all_news = []
all_news_en = []
translator = Translator()
divider = str('<hr width="50%" size="8" align="center"> <hr yesshade>')

    # for attempt in range(5): # five attempts
    #     try:
for i in range(0,len(data)):
    #if data['body'][i]:
    all_phrases_of_doc = get_key_phrase('强调',data['body'][i])+get_key_phrase('指出',data['body'][i])+get_key_phrase('提出',data['body'][i])#+get_key_phrase('表示',data['body'][i])
    all_phrases_of_doc =list(set(all_phrases_of_doc))
    all_phrases_of_doc = ','.join(all_phrases_of_doc) #[0:200]
    #print(all_phrases_of_doc)
    all_news_en.append(['<h2 style="margin: 0;">'+ str(translator.translate(data['title'][i]).text) + '</h2>' + '<U><i> '+ str(translator.translate(data['article_source'][i]).text)+'</i></U>' + '<br>(KEY PHRASES): '+ str(translator.translate(str(all_phrases_of_doc)).text)+'...']) # 'title: '+ str(translator.translate(data['title'][i]).text),
    all_news.append(['<br><B>[中文] TITLE: '+ str(data['title'][i])+'</B>'+' by '+ str(data['article_source'][i]) + '(KEY PHRASES): '+ str(all_phrases_of_doc) + '（SOURCE）: '+str(data['link'][i])+'</p>'+ str(divider)+'</br>'])
    # else:
    #     pass
        # except AttributeError as e:
        #     break

    #return all_news, all_news_en

#result, result_en = get_today_xi_speech(data)

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



############################################# HTML CODE ######################################

html = """\
<!doctype html>
<html>
  <head>
    <meta name="viewport" content="width=device-width" />
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Simple Transactional Email</title>
    <style>
      /* -------------------------------------
          GLOBAL RESETS
      ------------------------------------- */

      /*All the styling goes here*/

      img {
        border: none;
        -ms-interpolation-mode: bicubic;
        max-width: 100%;
      }

      body {
        background-color: #f6f6f6;
        font-family: sans-serif;
        -webkit-font-smoothing: antialiased;
        font-size: 14px;
        line-height: 1.4;
        margin: 0;
        padding: 0;
        -ms-text-size-adjust: 100%;
        -webkit-text-size-adjust: 100%;
      }

      table {
        border-collapse: separate;
        mso-table-lspace: 0pt;
        mso-table-rspace: 0pt;
        width: 100%; }
        table td {
          font-family: sans-serif;
          font-size: 14px;
          vertical-align: top;
      }

      /* -------------------------------------
          BODY & CONTAINER
      ------------------------------------- */

      .body {
        background-color: #f6f6f6;
        width: 100%;
      }

      /* Set a max-width, and make it display as block so it will automatically stretch to that width, but will also shrink down on a phone or something */
      .container {
        display: block;
        margin: 0 auto !important;
        /* makes it centered */
        max-width: 580px;
        padding: 10px;
        width: 580px;
      }

      /* This should also be a block element, so that it will fill 100% of the .container */
      .content {
        box-sizing: border-box;
        display: block;
        margin: 0 auto;
        max-width: 580px;
        padding: 10px;
      }

      /* -------------------------------------
          HEADER, FOOTER, MAIN
      ------------------------------------- */
      .main {
        background: #ffffff;
        border-radius: 3px;
        width: 100%;
      }

      .wrapper {
        box-sizing: border-box;
        padding: 20px;
      }

      .content-block {
        padding-bottom: 10px;
        padding-top: 10px;
      }

      .footer {
        clear: both;
        margin-top: 10px;
        text-align: center;
        width: 100%;
      }
        .footer td,
        .footer p,
        .footer span,
        .footer a {
          color: #999999;
          font-size: 12px;
          text-align: center;
      }

      /* -------------------------------------
          TYPOGRAPHY
      ------------------------------------- */
      h1,
      h2,
      h3,
      h4 {
        color: #000000;
        font-family: sans-serif;
        font-weight: 400;
        line-height: 1.4;
        margin: 0;
        margin-bottom: 30px;
      }

      h1 {
        font-size: 35px;
        font-weight: 300;
        text-align: center;
        text-transform: capitalize;
      }

      p,
      ul,
      ol {
        font-family: sans-serif;
        font-size: 14px;
        font-weight: normal;
        margin: 0;
        margin-bottom: 15px;
      }
        p li,
        ul li,
        ol li {
          list-style-position: inside;
          margin-left: 5px;
      }

      a {
        color: #3498db;
        text-decoration: underline;
      }

      /* -------------------------------------
          BUTTONS
      ------------------------------------- */
      .btn {
        box-sizing: border-box;
        width: 100%; }
        .btn > tbody > tr > td {
          padding-bottom: 15px; }
        .btn table {
          width: auto;
      }
        .btn table td {
          background-color: #ffffff;
          border-radius: 5px;
          text-align: center;
      }
        .btn a {
          background-color: #ffffff;
          border: solid 1px #3498db;
          border-radius: 5px;
          box-sizing: border-box;
          color: #CC0000;
          cursor: pointer;
          display: inline-block;
          font-size: 14px;
          font-weight: bold;
          margin: 0;
          padding: 12px 25px;
          text-decoration: none;
          text-transform: capitalize;
      }

      .btn-primary table td {
        background-color: #3498db;
      }

      .btn-primary a {
        background-color: #3498db;
        border-color: #3498db;
        color: #ffffff;
      }

      /* -------------------------------------
          OTHER STYLES THAT MIGHT BE USEFUL
      ------------------------------------- */
      .last {
        margin-bottom: 0;
      }

      .first {
        margin-top: 0;
      }

      .align-center {
        text-align: center;
      }

      .align-right {
        text-align: right;
      }

      .align-left {
        text-align: left;
      }

      .clear {
        clear: both;
      }

      .mt0 {
        margin-top: 0;
      }

      .mb0 {
        margin-bottom: 0;
      }

      .preheader {
        color: transparent;
        display: none;
        height: 0;
        max-height: 0;
        max-width: 0;
        opacity: 0;
        overflow: hidden;
        mso-hide: all;
        visibility: hidden;
        width: 0;
      }

      .powered-by a {
        text-decoration: none;
      }

      hr {
        border: 0;
        border-bottom: 1px solid #f6f6f6;
        margin: 20px 0;
      }

      /* -------------------------------------
          RESPONSIVE AND MOBILE FRIENDLY STYLES
      ------------------------------------- */
      @media only screen and (max-width: 620px) {
        table[class=body] h1 {
          font-size: 28px !important;
          margin-bottom: 10px !important;
        }
        table[class=body] p,
        table[class=body] ul,
        table[class=body] ol,
        table[class=body] td,
        table[class=body] span,
        table[class=body] a {
          font-size: 16px !important;
        }
        table[class=body] .wrapper,
        table[class=body] .article {
          padding: 10px !important;
        }
        table[class=body] .content {
          padding: 0 !important;
        }
        table[class=body] .container {
          padding: 0 !important;
          width: 100% !important;
        }
        table[class=body] .main {
          border-left-width: 0 !important;
          border-radius: 0 !important;
          border-right-width: 0 !important;
        }
        table[class=body] .btn table {
          width: 100% !important;
        }
        table[class=body] .btn a {
          width: 100% !important;
        }
        table[class=body] .img-responsive {
          height: auto !important;
          max-width: 100% !important;
          width: auto !important;
        }
      }

      /* -------------------------------------
          PRESERVE THESE STYLES IN THE HEAD
      ------------------------------------- */
      @media all {
        .ExternalClass {
          width: 100%;
        }
        .ExternalClass,
        .ExternalClass p,
        .ExternalClass span,
        .ExternalClass font,
        .ExternalClass td,
        .ExternalClass div {
          line-height: 100%;
        }
        .apple-link a {
          color: inherit !important;
          font-family: inherit !important;
          font-size: inherit !important;
          font-weight: inherit !important;
          line-height: inherit !important;
          text-decoration: none !important;
        }
        #MessageViewBody a {
          color: inherit;
          text-decoration: none;
          font-size: inherit;
          font-family: inherit;
          font-weight: inherit;
          line-height: inherit;
        }
        .btn-primary table td:hover {
          background-color: #34495e !important;
        }
        .btn-primary a:hover {
          background-color: #34495e !important;
          border-color: #34495e !important;
        }
      }

    </style>
  </head>
  <body class="">
    <span class="preheader">Policybot.io: All rights Reserved 2020.</span>
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="body">
      <tr>
        <td>&nbsp;</td>
        <td class="container">
          <div class="content">

            <!-- START CENTERED WHITE CONTAINER -->
            <table role="presentation" class="main">

            <img src="https://static01.nyt.com/images/2018/05/03/business/03XITECH/merlin_136086774_f6642f25-a833-489f-9edc-945fa49bf4dd-superJumbo.jpg" alt="centered image" class="center"/>
            <p><small>Photo Credit: Chris Koehler</small></p>
              <!-- START MAIN CONTENT AREA -->
              <tr>
                <td class="wrapper">
                  <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                    <tr>
                      <td>
                        """ + str(content_txt) + """

                        <p>  ***  </p>
                        <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="btn btn-primary">
                          <tbody>
                            <tr>
                              <td align="left">
                                <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                  <tbody>
                                    <tr>
                                      <td> <a href="policyb0.team@gmail.com" target="_blank">Policybot.io</a> </td>
                                    </tr>
                                  </tbody>
                                </table>
                              </td>
                            </tr>
                          </tbody>
                        </table>
                        <p><i>Policybot.io the world's very first open-source Python library built for global citizens to analyze and audit government public-policy making. Built for the people, by the people. Please respond to this email if you have constructive feedback for the Traceur.</i></p>
                        <p><i>Thanks for your attention!</i></p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

            <!-- END MAIN CONTENT AREA -->
            </table>
            <!-- END CENTERED WHITE CONTAINER -->

            <!-- START FOOTER -->
            <div class="footer">
              <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                <tr>
                  <td class="content-block">
                    <span class="apple-link">Policybot.io, Milwaukee, Wisconsin, USA </span>
                    <br>  <a href="policyb0.team@gmail.com">GNU General Public License v3.0</a>.
                  </td>
                </tr>
                <tr>
                  <td class="content-block powered-by">
                    XJP Traceur (version 0.2) Powered by <a href="http://www.policybot.io">Policybot.io</a>.
                  </td>
                </tr>
              </table>
            </div>
            <!-- END FOOTER -->

          </div>
        </td>
        <td>&nbsp;</td>
      </tr>
    </table>
  </body>
</html>
"""

#part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')
#
#
# ######################################  SEND EMAIL ############################################
user = 'policyb0.team@gmail.com'
app_password = 'ppy2015!' # Lampe.Very.Hell.826
host = 'smtp.gmail.com'
port = 465 # port 587 is for

to  = ['jianyin.roachell@gmail.com','fabian.policybot@gmail.com','john.policybot@gmail.com','tammy.tian@policybot.io']
#toaddrs = [toaddr] + bcc #  cc +
rec =  ', '.join(to)
# ################################ Get randomized keywords for Subject Line ###############
list_0 = data['title']
subject = jieba.analyse.extract_tags(str(list_0), topK=10, withWeight=True, allowPOS=('n'))
lines = []
for i in subject:
    lines.append(i[0])

# for attempt in range(5): # five attempts
#     try:
translator = Translator()
topics = translator.translate(','.join(lines[:5])).text
# except AttributeError as e:
#     topics = lines
subject = str('XJP Traceur: '+str(date) + ' with ' + str(len(data)) + ' new posts about '+ str(topics))
    # except AttributeError as e:
    #     print('cannot translate')
    #     break

###################################################################################################
message = MIMEMultipart()
## add From
message['From'] = Header(user)
## add To
#message['To'] = Header(to)
message['To'] = rec
## add Subject

message['Subject'] = Header(subject)
## add content text
message.attach(part2)
## #######################################################################  add attachment #################################
# attachment = r'C:\Users\ASUS\Desktop\policybot\policybot_venv\projects\xi_speech\_'+str(date)+'_daily_xi_monitor.xlsx'
# att_name = os.path.basename(attachment)
# att1 = MIMEText(open(attachment, 'rb').read(), 'base64', 'utf-8')
# att1['Content-Type'] = 'application/octet-stream'
# att1['Content-Disposition'] = 'attachment; filename=' + att_name
# message.attach(att1)

## Send email ###
server = smtplib.SMTP_SSL(host, port)
server.ehlo()
#server.starttls()
server.ehlo
server.login(user, app_password)
server = server
print('login success!')
server.sendmail(user, to, message.as_string())
server.quit()
print('Sent email successfully to Friends')


# # Send email SUPCHINA ###
to = []
to = ['lucas@supchina.com','bob@supchina.com','jeremy@supchina.com','wzhou5@student.gsu.edu']
#toaddrs = [toaddr] + bcc #  cc +
rec =  ', '.join(to)

server = smtplib.SMTP_SSL(host, port)
server.ehlo()
#server.starttls()
server.ehlo
server.login(user, app_password)
server = server
print('login success!')
server.sendmail(user, to, message.as_string())
server.quit()
print('SupChina Sent email successfully')


### Send email POLITICO ###
to = []
to = ['davidwertime@politico.com'] #,'davidwertime@politico.com'
#toaddrs = [toaddr] + bcc #  cc +
rec =  ', '.join(to)
server = smtplib.SMTP_SSL(host, port)
server.ehlo()
#server.starttls()
server.ehlo
server.login(user, app_password)
server = server
print('login success!')
server.sendmail(user, to, message.as_string())
server.quit()
print('POLITICO Sent email successfully')


### Send email CCP watch ###
# to = []
# to = ['dgitter@ccpwatch.org'] #,
# #toaddrs = [toaddr] + bcc #  cc +
# rec =  ', '.join(to)
# server = smtplib.SMTP_SSL(host, port)
# server.ehlo()
# #server.starttls()
# server.ehlo
# server.login(user, app_password)
# server = server
# print('login success!')
# server.sendmail(user, to, message.as_string())
# server.quit()
# print('CCP watch Sent email successfully')


### Send email China guys watch ###
to = []
to = ['nhandwer@gmail.com','steve.hopkins@thechinaguys.com'] #,
#toaddrs = [toaddr] + bcc #  cc +
rec =  ', '.join(to)
server = smtplib.SMTP_SSL(host, port)
server.ehlo()
#server.starttls()
server.ehlo
server.login(user, app_password)
server = server
print('login success!')
server.sendmail(user, to, message.as_string())
server.quit()
print('TCG Sent email successfully')

################## MICELLANEOUS #######################
to = []
to = ['jorschneider@gmail.com','matt.m.schrader@gmail.com'] #,
#toaddrs = [toaddr] + bcc #  cc +
rec =  ', '.join(to)
server = smtplib.SMTP_SSL(host, port)
server.ehlo()
#server.starttls()
server.ehlo
server.login(user, app_password)
server = server
print('login success!')
server.sendmail(user, to, message.as_string())
server.quit()
print('China Talks et al Sent email successfully')


####################### bill@sinocism.com ################
to = []
to = ['bill@sinocism.com'] #,
#toaddrs = [toaddr] + bcc #  cc +
rec =  ', '.join(to)
server = smtplib.SMTP_SSL(host, port)
server.ehlo()
#server.starttls()
server.ehlo
server.login(user, app_password)
server = server
print('login success!')
server.sendmail(user, to, message.as_string())
server.quit()
print('Sinocism Sent email successfully')


######################## MacroPolo ######################## dma@paulsoninstitute.org
to = []
to = ['dma@paulsoninstitute.org','msheehan@paulsoninstitute.org'] #,
#toaddrs = [toaddr] + bcc #  cc +
rec =  ', '.join(to)
server = smtplib.SMTP_SSL(host, port)
server.ehlo()
#server.starttls()
server.ehlo
server.login(user, app_password)
server = server
print('login success!')
server.sendmail(user, to, message.as_string())
server.quit()
print('MacroPolo Sent email successfully')

######################## Triviumchina ########################
to = []
to = ['andy.chen@triviumchina.com','ks@triviumchina.com'] #,
#toaddrs = [toaddr] + bcc #  cc +
rec =  ', '.join(to)
server = smtplib.SMTP_SSL(host, port)
server.ehlo()
#server.starttls()
server.ehlo
server.login(user, app_password)
server = server
print('login success!')
server.sendmail(user, to, message.as_string())
server.quit()
print('Triviumchina Sent email successfully')

#######################  ########################
to = []
to = ['m.d.johnsonphd@gmail.com'] #,
#toaddrs = [toaddr] + bcc #  cc +
rec =  ', '.join(to)
server = smtplib.SMTP_SSL(host, port)
server.ehlo()
#server.starttls()
server.ehlo
server.login(user, app_password)
server = server
print('login success!')
server.sendmail(user, to, message.as_string())
server.quit()
print('Friends Sent email successfully')

########################## University of Claremontmckenna ######################

to = []
to = ['Minxin.Pei@claremontmckenna.edu'] #,
#toaddrs = [toaddr] + bcc #  cc +
rec =  ', '.join(to)
server = smtplib.SMTP_SSL(host, port)
server.ehlo()
#server.starttls()
server.ehlo
server.login(user, app_password)
server = server
print('login success!')
server.sendmail(user, to, message.as_string())
server.quit()
print('Friends Sent email successfully')
