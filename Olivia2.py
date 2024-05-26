from __future__ import unicode_literals
import os
from flask import Flask, request, abort, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import *
import configparser
import time
import random
import logging
import requests
from bs4 import BeautifulSoup
import sqlite3
import math
app = Flask(__name__)

# LINE 聊天機器人的基本資料
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        print(body, signature)
        handler.handle(body, signature)

    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def prettyEcho(event):
    sendString = ""
    user_text = event.message.text.strip()  # 獲取用戶訊息並移除首尾空白

    # 處理系統功能
    if user_text == "系統功能":
        # 定義按鈕樣板
        buttons_template = ButtonsTemplate(
            title='按鈕樣板',
            thumbnail_image_url='https://i.pinimg.com/originals/ca/9a/a7/ca9aa7a0f9ae2e323bef8c553eda0d10.jpg',
            text='請選擇以下操作',
            actions=[
                MessageAction(label='旅遊', text='旅遊功能介紹'),
                MessageAction(label='星座', text='星座功能介紹'),
                MessageAction(label='穿搭', text='穿搭功能介紹'),
                MessageAction(label='美食', text='美食功能介紹')
            ]
        )

        # 回覆用戶
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='按鈕樣板',
                template=buttons_template
            )
        )
    
    # 處理星座查詢
    elif user_text == "星座":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='請選擇您的星座：',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(action=MessageAction(label="牡羊座", text="牡羊座")),
                        QuickReplyButton(action=MessageAction(label="金牛座", text="金牛座")),
                        QuickReplyButton(action=MessageAction(label="雙子座", text="雙子座")),
                        QuickReplyButton(action=MessageAction(label="巨蟹座", text="巨蟹座")),
                        QuickReplyButton(action=MessageAction(label="獅子座", text="獅子座")),
                        QuickReplyButton(action=MessageAction(label="處女座", text="處女座")),
                        QuickReplyButton(action=MessageAction(label="天秤座", text="天秤座")),
                        QuickReplyButton(action=MessageAction(label="天蠍座", text="天蠍座")),
                        QuickReplyButton(action=MessageAction(label="射手座", text="射手座")),
                        QuickReplyButton(action=MessageAction(label="摩羯座", text="摩羯座")),
                        QuickReplyButton(action=MessageAction(label="水瓶座", text="水瓶座")),
                        QuickReplyButton(action=MessageAction(label="雙魚座", text="雙魚座"))
                    ])))
    elif user_text in ["牡羊座", "金牛座", "雙子座", "巨蟹座", "獅子座", "處女座", "天秤座", "天蠍座", "射手座", "摩羯座", "水瓶座", "雙魚座"]:
        signs = {
            "牡羊座": 0,
            "金牛座": 1,
            "雙子座": 2,
            "巨蟹座": 3,
            "獅子座": 4,
            "處女座": 5,
            "天秤座": 6,
            "天蠍座": 7,
            "射手座": 8,
            "摩羯座": 9,
            "水瓶座": 10,
            "雙魚座": 11
        }
        sign_index = signs.get(user_text)
        if sign_index is not None:
            horoscope = get_horoscope(sign_index)  # 獲取星座運勢
            sendString = f"{horoscope}"
        else:
            sendString = "請輸入正確的星座名稱！"
    
    # 處理美食查詢
    elif user_text == "美食":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='請選擇您想查詢的食物類別：',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(action=MessageAction(label="飯食", text="飯食")),
                        QuickReplyButton(action=MessageAction(label="麵食", text="麵食")),
                        QuickReplyButton(action=MessageAction(label="穀物", text="穀物")),
                        QuickReplyButton(action=MessageAction(label="蔬菜", text="蔬菜")),
                        QuickReplyButton(action=MessageAction(label="海鮮", text="海鮮")),
                        QuickReplyButton(action=MessageAction(label="奶製品", text="奶製品")),
                        QuickReplyButton(action=MessageAction(label="肉類", text="肉類")),
                        QuickReplyButton(action=MessageAction(label="家常菜", text="家常菜")),
                        QuickReplyButton(action=MessageAction(label="飲料", text="飲料"))
                    ])))
    
    # 處理旅遊查詢
    elif user_text == "旅遊":
        buttons_template_message = TemplateSendMessage(
            alt_text='給你驚喜！',
            template=ButtonsTemplate(
                title='想找哪個地區呢？',
                text='暫不支援離島地區',
                actions=[
                    MessageAction(label='北部', text='北部'),
                    MessageAction(label='中部', text='中部'),
                    MessageAction(label='南部', text='南部'),
                    MessageAction(label='東部', text='東部')
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)

    # 選擇縣市
    elif user_text == '北部':
        flex_message = TextSendMessage(
            text='你想去北部的哪個縣市呢？',
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=PostbackTemplateAction(label="台北市", text="台北市", data='B&台北市')),
                QuickReplyButton(action=PostbackTemplateAction(label="新北市", text="新北市", data='B&新北市')),
                QuickReplyButton(action=PostbackTemplateAction(label="基隆市", text="基隆市", data='B&基隆市')),
                QuickReplyButton(action=PostbackTemplateAction(label="桃園市", text="桃園市", data='B&桃園市')),
                QuickReplyButton(action=PostbackTemplateAction(label="新竹市", text="新竹市", data='B&新竹市')),
                QuickReplyButton(action=PostbackTemplateAction(label="新竹縣", text="新竹縣", data='B&新竹縣')),
                QuickReplyButton(action=PostbackTemplateAction(label="宜蘭縣", text="宜蘭縣", data='B&宜蘭縣'))
            ])
        )
        line_bot_api.reply_message(event.reply_token, flex_message)

    elif user_text == '中部':
        flex_message = TextSendMessage(
            text='你想去中部的哪個縣市呢？',
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=PostbackTemplateAction(label="台中市", text="台中市", data='C&台中市')),
                QuickReplyButton(action=PostbackTemplateAction(label="苗栗縣", text="苗栗縣", data='C&苗栗縣')),
                QuickReplyButton(action=PostbackTemplateAction(label="彰化縣", text="彰化縣", data='C&彰化縣')),
                QuickReplyButton(action=PostbackTemplateAction(label="南投縣", text="南投縣", data='C&南投縣')),
                QuickReplyButton(action=PostbackTemplateAction(label="雲林縣", text="雲林縣", data='C&雲林縣'))
            ])
        )
        line_bot_api.reply_message(event.reply_token, flex_message)

    elif user_text == '南部':
        flex_message = TextSendMessage(
            text='你想去南部的哪個縣市呢？',
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=PostbackTemplateAction(label="高雄市", text="高雄市", data='S&高雄市')),
                QuickReplyButton(action=PostbackTemplateAction(label="台南市", text="台南市", data='S&台南市')),
                QuickReplyButton(action=PostbackTemplateAction(label="嘉義市", text="嘉義市", data='S&嘉義市')),
                QuickReplyButton(action=PostbackTemplateAction(label="嘉義縣", text="嘉義縣", data='S&嘉義縣')),
                QuickReplyButton(action=PostbackTemplateAction(label="屏東縣", text="屏東縣", data='S&屏東縣'))
            ])
        )
        line_bot_api.reply_message(event.reply_token, flex_message)

    elif user_text == '東部':
        flex_message = TextSendMessage(
            text='你想去東部的哪個縣市呢？',
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=PostbackTemplateAction(label="花蓮縣", text="花蓮縣", data='E&花蓮縣')),
                QuickReplyButton(action=PostbackTemplateAction(label="台東縣", text="台東縣", data='E&台東縣'))
            ])
        )
        line_bot_api.reply_message(event.reply_token, flex_message)

    # 具體縣市查詢
    elif user_text in ["台北市", "新北市", "基隆市", "桃園市", "新竹市", "新竹縣", "宜蘭縣", "台中市", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "高雄市", "台南市", "嘉義市", "嘉義縣", "屏東縣", "花蓮縣", "台東縣"]:
        recommendation = scrape_viewpoints(user_text)
        if recommendation:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=recommendation))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="目前無法找到旅遊資訊，請稍後再試。"))
            
    # 處理具體食物查詢
    elif user_text in ["飯食", "麵食", "穀物", "蔬菜", "海鮮", "奶製品", "肉類", "家常菜", "飲料"]:
        # 處理食物選單查詢
        food_options = {
            "飯食":  ["炒飯","燉飯","焗烤飯","油飯", "鹹粥", "小米粥","壽司"],
            "麵食":  ["刀削麵", "陽春麵", "冬粉","焗烤意麵","米粉","烏龍麵","水餃","麵包","辣炒年糕","鍋貼","拉麵","義大利麵","蛋餅","鹽水意麵","鍋燒意麵","筆管麵","排骨雞麵","排骨酥麵","泡麵"],
            "穀物": ["綠豆湯", "紅豆湯", "豆花", "燕麥片","燒仙草"],
            "蔬菜": ["青江菜", "空心菜", "高麗菜", "洋蔥炒蛋","番茄炒蛋","豆芽菜","蛋花湯"],
            "海鮮": ["蝦子", "蛤蠣絲瓜","魚湯","螃蟹","龍蝦"],
            "奶製品":  ["牛奶", "優若乳", "起司","乳清蛋白","冰淇淋","聖代","冰棒"],
            "肉類": ["牛排", "炸豬排", "雞排","羊肉爐"],
            "家常菜": ["青椒炒肉絲", "紅燒獅子頭","紅燒肉","糖醋里肌","番茄炒蛋","麻婆豆腐"],
            "飲料": ["珍珠奶茶", "現榨果汁","奶茶","紅茶","綠茶"]
        }
        # 隨機選擇該類別中的食物
        random_food = random.choice(food_options[user_text])
        # 回復隨機選擇的食物
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=random_food))

    elif user_text == "穿搭":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='請選擇今日溫度區間：',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(action=MessageAction(label="10°C以下", text="寒冷")),
                        QuickReplyButton(action=MessageAction(label="10°C-20°C", text="涼爽")),
                        QuickReplyButton(action=MessageAction(label="20°C-30°C", text="溫暖")),
                        QuickReplyButton(action=MessageAction(label="30°C-35°C", text="炎熱")),
                        QuickReplyButton(action=MessageAction(label="35°C以上", text="極熱")),
                    ])))
    
    # 預設回應：將用戶原始訊息回傳
    else:
        sendString = user_text

    # 使用 reply_message 方法將訊息回傳給用戶
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=sendString))

# Handle PostbackEvent
@handler.add(PostbackEvent)
def handle_message(event):
    data = event.postback.data
    if data == 'date_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['date']))

def get_horoscope(sign):
    url = f'https://astro.click108.com.tw/daily_{sign}.php?iAstro={sign}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    horoscope = soup.find('div', class_='TODAY_CONTENT').text.strip()
    return horoscope

def scrape_viewpoints(city):
    url = f'https://travel.yam.com/find/{city}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    viewpoints = []
    sections = soup.find_all('section', class_='article_list_box_content')
    for section in sections:
        box_info = section.find('div', class_='article_list_box_info')
        if box_info:
            href = box_info.find('a')['href']
            title = box_info.find('h3').text.strip()
            viewpoints.append({'title': title, 'href': f"https://travel.yam.com{href}"})
    return viewpoints
        
if __name__ == "__main__":
    app.run()
