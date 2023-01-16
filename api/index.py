from http.server import BaseHTTPRequestHandler
import re
import requests
from bs4 import BeautifulSoup

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        print("request from", self.client_address)

        url = 'https://tenki.jp/forecast/3/16/4410/13210/1hour.html'
        # 解析済みのhtmlデータ
        r = requests.get(url)
        html = r.text.encode(r.encoding)
        s = BeautifulSoup(html, 'html.parser')
        # keyとvalue格納用辞書
        data = {}
        response={}

        # 辞書に要素追加
        loc_cand_1 = r"(.+)の1時間天気"
        loc_cand_2 = s.title.text
        data['location'] = re.findall(loc_cand_1, loc_cand_2)[0]#一致するか確認
        response += data['location'] + "の天気\n"
        soup_today = s.find(id='forecast-point-1h-today')

        # 日付処理
        d_date = r"(\d+)年(\d+)月(\d+)日"
        d_src = s.select('.head p')
        date = re.findall(d_date, d_src[0].text)[0]
        data["date"] = "%s年%s月%s日" % (date[0], date[1], date[2])
        response += "=====" + data["date"] + "====="
        response += "時刻      気温(C)   天気"

        # 一時間ごとのデータを取得する
        hour          = s.select('.hour > td')
        weather       = s.select('.weather > td')
        temperature   = s.select('.temperature > td')

        # 格納
        data["forecasts"] = []
        for num in range(0, 24):
            forecast = {}
            forecast["hour"] = hour[num].text.strip()
            forecast["weather"] = weather[num].text.strip()
            forecast["temperature"] = temperature[num].text.strip()

            response += (
                "時刻         : " + forecast["hour"] + "時" + "\n"
                "天気         : " + forecast["weather"] + "\n"
                "気温(C)      : " + forecast["temperature"] + "\n\n"
            )
            # response += (
            #     "%-9s%-10s%s"%(forecast["hour"] + "時", forecast["temperature"], forecast["weather"])
            # )
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
        return