from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
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

@handler.add(MessageEvent, message=TextMessage)
def prettyEcho(event):
    user_text = event.message.text.strip()  # 獲取用戶訊息並移除首尾空白
    sendString = ""

    # 處理系統功能
    if "系統功能" in user_text:
        sendString = "這是我們系統的功能介紹\n請輸入您想查看的功能名稱：\n星座\n美食\n天氣"

    # 處理星座查詢
    elif user_text == "星座":
        sendString = "請輸入星座名稱："
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
            sendString = horoscope
        else:
            sendString = "請輸入正確的星座名稱！"
    
    # 處理美食查詢
    elif "美食" in user_text:
        sendString = "請輸入食物種類：\n1. 飯食\n2. 麵食\n3. 穀物\n4. 蔬菜\n5. 海鮮\n6. 奶製品\n7. 肉類\n8. 飲料"
    
    # 處理食物選單查詢
    elif user_text in ["飯食", "麵食", "穀物", "蔬菜", "海鮮", "奶製品", "肉類", "飲料"]:
        food_response = {
            "飯食": drawStraws(["炒飯", "焗烤飯", "油飯", "鹹粥"]),
            "麵食": drawStraws(["麵食", "拉麵", "義大利麵", "冬粉", "麵線"]),
            "穀物": drawStraws(["米", "糙米", "燕麥", "糯米"]),
            "蔬菜": drawStraws(["高麗菜", "青江菜", "菠菜", "芹菜"]),
            "海鮮": drawStraws(["蝦", "魚", "螃蟹", "蚵仔"]),
            "奶製品": drawStraws(["牛奶", "優格", "起司"]),
            "肉類": drawStraws(["牛肉", "雞肉", "豬肉", "羊肉"]),
            "飲料": drawStraws(["紅茶", "綠茶", "奶茶", "果汁"])
        }
        sendString = food_response[user_text]
    
    # 處理天氣查詢
    elif user_text == "天氣":
        sendString = scrape_weather()
    
    # 處理旅遊查詢
    elif user_text == "旅遊":
        sendString = scrape_viewpoints()

    # 預設回應：將用戶原始訊息回傳
    else:
        sendString = user_text

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=sendString))

@handler.add(PostbackEvent)
def handle_message(event):
    data = event.postback.data
    if data == 'date_postback':
        date = event.postback.params['date']
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"您選擇的日期是：{date}"))

def drawStraws(options):
    return random.choice(options)

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
        return None
    return response.text

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

if __name__ == "__main__":
    app.run()
