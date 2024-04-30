from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction, CameraAction, CameraRollAction, LocationAction, PostbackEvent, PostbackAction, DatetimePickerAction
import configparser
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 處理用戶訊息
@handler.add(MessageEvent, message=TextMessage)
def prettyEcho(event):
    user_text = event.message.text.strip()
    
    # 處理"quick"訊息，返回帶有快速回復按鈕的訊息
    if 'quick' in user_text:
        quick_reply_buttons = [
            QuickReplyButton(
                action=CameraAction(label="開啟相機")
            ),
            QuickReplyButton(
                action=CameraRollAction(label="相機膠捲")
            ),
            QuickReplyButton(
                action=LocationAction(label="位置資訊")
            ),
            QuickReplyButton(
                action=PostbackAction(label="Postback 行為", data="postback")
            ),
            QuickReplyButton(
                action=MessageAction(label="一則訊息", text="這是一則訊息")
            ),
            QuickReplyButton(
                action=DatetimePickerAction(label="選擇日期", data="date_postback", mode="date")
            )
        ]

        quick_reply = QuickReply(items=quick_reply_buttons)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='請選擇您想使用的功能：',
                quick_reply=quick_reply
            )
        )
    elif user_text == "旅遊":
        # 處理旅遊查詢
        sendString = scrape_viewpoints()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=sendString))
    elif user_text == "天氣":
        # 處理天氣查詢
        sendString = scrape_weather()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=sendString))
    elif user_text == "星座":
        # 處理星座查詢
        sendString = "請輸入星座名稱："
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=sendString))
    elif user_text.endswith("座"):
        sign = user_text.split(" ")[0]
        signs = {
            "牡羊座": "aries",
            "金牛座": "taurus",
            "雙子座": "gemini",
            "巨蟹座": "cancer",
            "獅子座": "leo",
            "處女座": "virgo",
            "天秤座": "libra",
            "天蠍座": "scorpio",
            "射手座": "sagittarius",
            "摩羯座": "capricorn",
            "水瓶座": "aquarius",
            "雙魚座": "pisces"
        }
        sign_code = signs.get(sign)
        if sign_code:
            horoscope = get_horoscope(sign_code)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=horoscope))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入正確的星座名稱！"))
    elif "美食" in user_text:
        # 處理美食查詢
        # 創建食物類別的快速回覆按鈕
        quick_reply_buttons = [
            QuickReplyButton(action=MessageAction(label="飯食", text="飯食")),
            QuickReplyButton(action=MessageAction(label="麵食", text="麵食")),
            QuickReplyButton(action=MessageAction(label="穀物", text="穀物")),
            QuickReplyButton(action=MessageAction(label="蔬菜", text="蔬菜")),
            QuickReplyButton(action=MessageAction(label="海鮮", text="海鮮")),
            QuickReplyButton(action=MessageAction(label="奶製品", text="奶製品")),
            QuickReplyButton(action=MessageAction(label="肉類", text="肉類")),
            QuickReplyButton(action=MessageAction(label="飲料", text="飲料"))
        ]
        
        # 創建 QuickReply 並將按鈕列表添加到其中
        quick_reply = QuickReply(items=quick_reply_buttons1)
        
        # 創建 TextSendMessage 並將 QuickReply 添加到其中
        text_message = TextSendMessage(
            text="請選擇您想查詢的食物類別：",
            quick_reply=quick_reply
        )
        line_bot_api.reply_message(event.reply_token, text_message)
    elif user_text in ["飯食", "麵食", "穀物", "蔬菜", "海鮮", "奶製品", "肉類", "飲料"]:
        # 處理食物選單查詢
        food_options = {
            "飯食": ["炒飯", "焗烤飯", "油飯", "鹹粥"],
            "麵食": ["麵食", "拉麵", "義大利麵", "冬粉", "麵線"],
            "穀物": ["米", "糙米", "燕麥", "糯米"],
            "蔬菜": ["高麗菜", "青江菜", "菠菜", "芹菜"],
            "海鮮": ["蝦", "魚", "螃蟹", "蚵仔"],
            "奶製品": ["牛奶", "優格", "起司"],
            "肉類": ["牛肉", "雞肉", "豬肉", "羊肉"],
            "飲料": ["紅茶", "綠茶", "奶茶", "果汁"]
        }
        
        # 隨機選擇該類別中的食物
        random_food = random.choice(food_options[user_text])
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=random_food))
    else:
        # 預設回應：回復用戶原始訊息
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=user_text))

# 處理 Postback 事件
@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    if data == 'date_postback':
        date = event.postback.params['date']
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"您選擇的日期是：{date}"))

# 函數：隨機選擇食物
def drawStraws(options):
    return random.choice(options)

# 函數：獲取星座運勢
def get_horoscope(sign):
    url = f'https://astro.click108.com.tw/daily_{sign}.php?iAstro={sign}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    horoscope = soup.find('div', class_='TODAY_CONTENT').text.strip()
    return horoscope

# 函數：網絡請求
def fetch_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    return response.text

# 函數：抓取旅遊資訊
def scrape_viewpoints():
    url = "https://www.taiwan.net.tw/"
    response_text = fetch_url(url)
    if not response_text:
        return "無法獲取旅遊資訊。"
    
    soup = BeautifulSoup(response_text, "html.parser")
    viewpoints = soup.find_all("a", class_="megamenu-btn")

    all_itineraries = []
    for viewpoint in viewpoints:
        viewpoint_url = urljoin(url, viewpoint.get("href"))
        viewpoint_text = viewpoint.getText()
        
        viewpoint_response_text = fetch_url(viewpoint_url)
        if not viewpoint_response_text:
            continue
        
        viewpoint_soup = BeautifulSoup(viewpoint_response_text, "html.parser")
        itinerary_links = viewpoint_soup.find_all("a", class_="circularbtn")
        
        for itinerary_link in itinerary_links:
            itinerary_url = urljoin(url, itinerary_link.get("href"))
            itinerary_text = itinerary_link.find("span", class_="circularbtn-title").getText()
            
            itinerary_response_text = fetch_url(itinerary_url)
            if not itinerary_response_text:
                continue
            
            itinerary_soup = BeautifulSoup(itinerary_response_text, "html.parser")
            titles = itinerary_soup.find_all("div", class_="card-info")

            for title in titles:
                itinerary_title = title.find("div", class_="card-title").getText()
                all_itineraries.append({
                    "viewpoint": viewpoint_text,
                    "itinerary": itinerary_text,
                    "title": itinerary_title
                })

    # 隨機推薦一個行程
    if all_itineraries:
        random_itinerary = random.choice(all_itineraries)
        return f"地點: {random_itinerary['viewpoint']} - {random_itinerary['itinerary']}\n行程名稱: {random_itinerary['title']}"
    else:
        return "無法推薦行程。"

# 主程序入口
if __name__ == "__main__":
    app.run()
