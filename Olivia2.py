from __future__ import unicode_literals
import os
from flask import Flask, request, abort, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import *
import configparser
import random
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
    if "系統功能" in user_text:
        sendString = "這是我們系統的功能介紹\n請輸入您想查看的功能名稱：\n星座\n美食\n天氣"
    
    # 處理星座查詢
    elif user_text == "星座":
        sendString = "以下是我們的星座選單功能介紹\n請輸入星座"
    elif user_text.endswith("座"):
        sign = user_text.split(" ")[0]  # 提取用戶輸入的星座
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
        sign_index = signs.get(sign)
        if sign_index is not None:
            horoscope = get_horoscope(sign_index)  # 獲取星座運勢
            sendString = f"{horoscope}"
        else:
            sendString = "請輸入正確的星座名稱！"
    
    # 處理美食查詢
    elif "美食" in user_text:
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
    
    # 處理天氣查詢
    elif "旅遊" in user_text:
        sendString = scrape_viewpoints()
        
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

def divinationBlocks():
    divinationBlocksList = ["飯食","麵食","穀物","蔬菜","海鮮","奶製品","肉類"]
    return divinationBlocksList[random.randint(0, len(divinationBlocksList) - 1)]
def drawStraws():
    drawStrawsList = ["炒飯","燉飯","焗烤飯","油飯", "鹹粥", "小米粥","壽司"]
    return drawStrawsList[random.randint(0, len(drawStrawsList) - 1)]
def drawStraws1():
    drawStrawsList = ["刀削麵", "陽春麵", "冬粉","焗烤意麵","米粉","烏龍麵","水餃","麵包","辣炒年糕","鍋貼","拉麵","義大利麵","蛋餅","鹽水意麵","鍋燒意麵","筆管麵","排骨雞麵","排骨酥麵","泡麵"]
    return drawStrawsList[random.randint(0, len(drawStrawsList) - 1)]
def drawStraws2():
    drawStrawsList = ["綠豆湯", "紅豆湯", "豆花", "燕麥片","燒仙草"]
    return drawStrawsList[random.randint(0, len(drawStrawsList) - 1)]
def drawStraws3():
    drawStrawsList = ["青江菜", "空心菜", "高麗菜", "洋蔥炒蛋","番茄炒蛋","豆芽菜","蛋花湯"]
    return drawStrawsList[random.randint(0, len(drawStrawsList) - 1)]
def drawStraws4():
    drawStrawsList = ["蝦子", "蛤蠣絲瓜","魚湯","螃蟹","龍蝦"]
    return drawStrawsList[random.randint(0, len(drawStrawsList) - 1)]
def drawStraws5():
    drawStrawsList = ["牛奶", "優若乳", "起司","乳清蛋白","冰淇淋","聖代","冰棒"]
    return drawStrawsList[random.randint(0, len(drawStrawsList) - 1)]
def drawStraws6():
    drawStrawsList = ["牛排", "炸豬排", "雞排","羊肉爐"]
    return drawStrawsList[random.randint(0, len(drawStrawsList) - 1)]
def drawStraws7():
    drawStrawsList = ["青椒炒肉絲", "紅燒獅子頭","紅燒肉","糖醋里肌","番茄炒蛋","麻婆豆腐"]
    return drawStrawsList[random.randint(0, len(drawStrawsList) - 1)]
def drawStraws8():
    drawStrawsList = ["珍珠奶茶", "現榨果汁","奶茶","紅茶","綠茶"]
    return drawStrawsList[random.randint(0, len(drawStrawsList) - 1)]


def get_horoscope(sign):
    url = f'https://astro.click108.com.tw/daily_{sign}.php?iAstro={sign}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    horoscope = soup.find('div', class_='TODAY_CONTENT').text.strip()
    return horoscope

def fetch_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: Unable to fetch URL {url}. Status code: {response.status_code}")
        return None
    return response

def scrape_viewpoints():
    response = fetch_url("https://www.taiwan.net.tw/")
    if response is None:
        return
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    viewpoints = soup.find_all("a", class_="megamenu-btn")
    all_itineraries = []
    
    for viewpoint in viewpoints:
        url = urljoin(BASE_URL, viewpoint.get("href"))
        url_response = fetch_url(url)
        if url_response is None:
            continue
        
        url_soup = BeautifulSoup(url_response.text, "html.parser")
        
        de_viewpoints = url_soup.find_all("a", class_="circularbtn")
        for de_viewpoint in de_viewpoints:
            viewpoint_text = viewpoint.getText()
            de_viewpoint_text = de_viewpoint.find("span", class_="circularbtn-title").getText()
            
            de_url = urljoin(BASE_URL, de_viewpoint.get("href"))
            de_url_response = fetch_url(de_url)
            if de_url_response is None:
                continue
            
            de_url_soup = BeautifulSoup(de_url_response.text, "html.parser")
            
            titles = de_url_soup.find_all("div", class_="card-info")
            for title in titles:
                itinerary_title = title.find("div", class_="card-title").getText()
                all_itineraries.append({
                    "viewpoint": viewpoint_text,
                    "de_viewpoint": de_viewpoint_text,
                    "title": itinerary_title
                })
                
    # 隨機推薦一個行程
    if all_itineraries:
        random_itinerary = random.choice(all_itineraries)
        print("隨機推薦的行程:")
        print(f"地點: {random_itinerary['viewpoint']} - {random_itinerary['de_viewpoint']}")
        print(f"行程名稱: {random_itinerary['title']}")

if __name__ == "__main__":
    app.run()
