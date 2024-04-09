from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
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
def prettyEcho(event):    #這個好像只能執行一個  不知道為什麼，我還沒研究出來  我的意思是我沒有辦法把系統功能跟食物分開來寫兩個判斷(if else)
    sendString = ""
    if "系統功能" in event.message.text:
        sendString = "這是我們系統的功能介紹\n請輸入您想查看的功能名稱：\n星座\n美食\n天氣"
    elif event.message.text == "星座":
        sendString = "以下是我們的星座選單功能介紹\n請輸入星座"
    elif event.message.text.endswith("座"):
        sign = event.message.text.split(" ")[0]  # 提取用戶輸入的星座
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
    elif event.message.text ==  "美食" in event.message.text:
        sendString = "以下是我們的美食選單功能介紹"
    elif event.message.text == "天氣" in event.message.text:
        sendString = "以下是我們的天氣選單功能介紹"
    elif event.message.text True:
        city = event.message.text.split(" ")[0]
        date = event.message.text.split(" ")[1]
        date = date.replace("/", "-")
        weather = get_weather_forecast(city, date)
        sendString = f"{weather}"
    elif "食物" in event.message.text:
         sendString = "請回傳以下食物種類\n(數字或文字都可)：\n1. 飯食\n2. 麵食\n3. 穀物\n4. 蔬菜\n5. 海鮮\n6. 奶製品\n7. 肉類\n8. 家常菜\n9. 飲料"
    elif "飯食" in event.message.text or "飯" in event.message.text or "1" in event.message.text:
        sendString = drawStraws()
    elif "麵食" in event.message.text or "麵" in event.message.text or "2" in event.message.text:
        sendString = drawStraws1()
    elif "穀物" in event.message.text or "穀" in event.message.text or "3" in event.message.text:
        sendString = drawStraws2()
    elif "蔬菜" in event.message.text or "4" in event.message.text:
        sendString = drawStraws3()
    elif "海鮮" in event.message.text or "5" in event.message.text:
        sendString = drawStraws4()
    elif "奶製品" in event.message.text or "奶" in event.message.text or "6" in event.message.text:
        sendString = drawStraws5()
    elif "肉類" in event.message.text or "肉" in event.message.text or "7" in event.message.text:
        sendString = drawStraws6()
    elif "家常菜" in event.message.text or "8" in event.message.text:
        sendString = drawStraws7()
    elif "飲料" in event.message.text or "9" in event.message.text:
        sendString = drawStraws8()
    else:
        sendString = event.message.text

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=sendString)
    )
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

def get_weather_forecast(city, date):
    # 定義 API 連結
    url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=CWA-346E911F-5413-4B38-A93D-8879F3E3E200&format=JSON&locationName={city}'
    try:
        # 發送 API 請求
        response = requests.get(url)

        # 檢查回應狀態碼
        if response.status_code == 200:
            # 解析 JSON 資料
            data_json = response.json()

            # 取得天氣資料
            locations = data_json['records']['location']
            for location in locations:
                print(f"地點：{location['locationName']}")
                for weather_element in location['weatherElement']:
                    if weather_element['elementName'] == 'Wx':
                        print(f"天氣：{weather_element['time'][0]['parameter']['parameterName']}")
                    elif weather_element['elementName'] == 'PoP':
                        print(f"降雨機率：{weather_element['time'][0]['parameter']['parameterName']}%")
                        if int(weather_element['time'][0]['parameter']['parameterName']) > 50:
                            print("建議攜帶雨具！")
                        else:
                            print("天氣晴朗，不需攜帶雨具。")
                    elif weather_element['elementName'] == 'MinT':
                        print(f"最低溫度：{weather_element['time'][0]['parameter']['parameterName']}°C")
                    elif weather_element['elementName'] == 'MaxT':
                        print(f"最高溫度：{weather_element['time'][0]['parameter']['parameterName']}°C")
                        max_temp = int(weather_element['time'][0]['parameter']['parameterName'])
                        if max_temp >= 30:
                            print("天氣很熱，建議穿輕便服裝。")
                        elif max_temp >= 20:
                            print("天氣適中，可穿著舒適服裝。")
                        elif max_temp >= 10:
                            print("天氣較涼，建議穿長袖保暖。")
                        else:
                            print("天氣寒冷，請注意保暖。")
        else:
            print("請求失敗:", response.status_code)
    except Exception as e:
        print("發生錯誤:", e)

if __name__ == "__main__":
    app.run()
