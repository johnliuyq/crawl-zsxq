import requests
import json
import os
import pdfkit
from bs4 import BeautifulSoup
from urllib.parse import quote

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>
<h1>{title}</h1>
<p>{text}</p>
</body>
</html>
"""
htmls = []

def get_data(url):

    global htmls
        
    headers = {
        'Authorization': 'F375A8D1-2120-5880-FDCD-8E550ECBxxxx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36'
    }
    rsp = requests.get(url, headers=headers)
    with open('stormzhang.json', 'w', encoding='utf-8') as f:        # 将返回数据写入 a.json 方便查看
        f.write(json.dumps(rsp.json(), indent=2, ensure_ascii=False))

    with open('stormzhang.json', encoding='utf-8') as f:
        for topic in json.loads(f.read()).get('resp_data').get('topics'):
            content = topic.get('question', topic.get('talk', topic.get('task')))
            # print(content)
            text = content.get('text')
            title = text[:6]

            if content.get('images'):
                soup = BeautifulSoup(html_template, 'html.parser')
                for img in content.get('images'):
                    url = img.get('large').get('url')
                    img_tag = soup.new_tag('img', src=url)
                    soup.body.append(img_tag)
                    html_img = str(soup)
                    html = html_img.format(title=title, text=text)
            else:
                html = html_template.format(title=title, text=text)

            if topic.get('question'):
                answer = topic.get('answer').get('text')
                soup = BeautifulSoup(html, 'html.parser')
                answer_tag = soup.new_tag('p')
                answer_tag.string = answer
                soup.body.append(answer_tag)
                html_answer = str(soup)
                html = html_answer.format(title=title, text=text)

            htmls.append(html)

    next_page = rsp.json().get('resp_data').get('topics')
    if next_page:
        create_time = next_page[-1].get('create_time')
        end_time = create_time[:20]+str(int(create_time[20:23])-1)+create_time[23:]
        end_time = quote(end_time)
        next_url = start_url + '&end_time=' + end_time
        print(next_url)
        get_data(next_url)


    return htmls

def make_pdf(htmls):
    html_files = []
    for index, html in enumerate(htmls):
        file = str(index) + ".html"
        html_files.append(file)
        with open(file, "w", encoding="utf-8") as f:
            f.write(html)

    options = {
        "page-size": "Letter",
        "margin-top": "0.75in",
        "margin-right": "0.75in",
        "margin-bottom": "0.75in",
        "margin-left": "0.75in",
        "encoding": "UTF-8",
        "custom-header": [("Accept-Encoding", "gzip")],
        "cookie": [
            ("cookie-name1", "cookie-value1"), ("cookie-name2", "cookie-value2")
        ],
        "outline-depth": 10,
    }
    try:
        pdfkit.from_file(html_files, "stormzhang.pdf", options=options)
    except Exception as e:
        print(e)

    for file in html_files:
        os.remove(file)

    print("已制作电子书 stormzhang.pdf 在当前目录！")
    
if __name__ == '__main__':
    start_url = 'https://api.zsxq.com/v1.10/groups/2421112121/topics?scope=digests&count=20'
    make_pdf(get_data(start_url))