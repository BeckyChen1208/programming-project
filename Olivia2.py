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
        sendString = scrape_viewpoints()
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
'''
# 設置日誌記錄
logging.basicConfig(filename='bot_log.log', level=logging.INFO)

def fetch_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logging.error(f"Error: Unable to fetch URL {url}. Status code: {response.status_code}")
            return None
        return response
    except requests.exceptions.RequestException as e:
        # 在出現網絡問題或其他問題時記錄錯誤
        logging.error(f"Request error for URL {url}: {e}")
        return None
'''
def scrape_viewpoints():
    url = "https://www.taiwan.net.tw/"
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")

    viewpoints = []

    if response.status_code == 200:
        container_elements = soup.find_all(class_='container-fluid theme-container')
        for container_element in container_elements:
            try:
                link_elements = container_element.find_all('a', class_='megamenu-btn')
                for link_element in link_elements:
                    link_text = link_element.get_text(strip=True)
                    link_url = link_element['href']
                    absolute_link_url = urljoin(url, link_url)  # 轉換為絕對路徑
                    viewpoints.append({
                        'title': link_text,
                        'url': absolute_link_url
                    })
            except Exception as e:
                print("連結提取失敗:", str(e))

        if viewpoints:
            random_viewpoint = random.choice(viewpoints)
            return f"隨機推薦的旅遊景點:\n名稱: {random_viewpoint['title']}\n連結: {random_viewpoint['url']}"

    else:
        print("無法取得網頁內容，狀態碼:", response.status_code)
        return None
        
if __name__ == "__main__":
    app.run()
