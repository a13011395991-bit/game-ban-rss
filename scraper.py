import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9"
}

def fetch_zeus():
    """抓取 宙斯：傲慢之神 官方公告"""
    items = []
    try:
        url = "https://zeus.com2us.com/news/notice"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        # 精准定位公告列表区域，排除顶部导航
        list_area = soup.select_one("ul.news_list, .notice_list, .board_list")
        if not list_area:
            print("宙斯：未找到公告列表")
            return items
        
        rows = list_area.select("li")
        for row in rows[:30]:
            a_tag = row.select_one("a")
            if not a_tag:
                continue
            
            title = a_tag.get_text(strip=True)
            link = a_tag.get("href", "")
            if link and not link.startswith("http"):
                link = "https://zeus.com2us.com" + link
            
            date_tag = row.select_one(".date, .time, span.date")
            date_str = date_tag.get_text(strip=True) if date_tag else ""
            
            if title and link and len(title) > 5:
                items.append({"title": title, "link": link, "date": date_str, "site": "宙斯"})
    except Exception as e:
        print(f"宙斯抓取失败: {e}")
    return items

def fetch_dokkaebi():
    """抓取 鬼怪世界 官方公告"""
    items = []
    try:
        url = "https://forum.kakaogames.com/dokkaebi/postList/?code=notice"
        session = requests.Session()
        # 模拟正常访问，先请求首页种下Cookie
        session.get("https://forum.kakaogames.com/", headers=HEADERS, timeout=10)
        resp = session.get(url, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        rows = soup.select(".board_list li, .list_item, tr")
        for row in rows[:30]:
            a_tag = row.select_one("a.tit, .subject a, a.title")
            if not a_tag:
                continue
            
            title = a_tag.get_text(strip=True)
            link = a_tag.get("href", "")
            if link and not link.startswith("http"):
                link = "https://forum.kakaogames.com" + link
            
            date_tag = row.select_one(".date, .time")
            date_str = date_tag.get_text(strip=True) if date_tag else ""
            
            if title and link and len(title) > 5:
                items.append({"title": title, "link": link, "date": date_str, "site": "鬼怪世界"})
    except Exception as e:
        print(f"鬼怪世界抓取失败: {e}")
    return items

def fetch_eclipse():
    """日蚀觉醒：Stove动态页面无法直接抓取，返回空列表
       建议用媒体专区RSS兜底，在n8n里合并源即可"""
    return []

def build_rss(all_items):
    """生成标准RSS 2.0文件"""
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "韩游封号公告聚合RSS"
    ET.SubElement(channel, "link").text = "https://github.com/a13011395991-bit/game-ban-rss"
    ET.SubElement(channel, "description").text = "自动抓取宙斯、鬼怪世界官方公告"
    ET.SubElement(channel, "language").text = "ko-kr"

    for item in all_items[:60]:
        item_node = ET.SubElement(channel, "item")
        ET.SubElement(item_node, "title").text = f"[{item['site']}] {item['title']}"
        ET.SubElement(item_node, "link").text = item["link"]
        ET.SubElement(item_node, "description").text = item["title"]
        ET.SubElement(item_node, "pubDate").text = item["date"]
        ET.SubElement(item_node, "guid").text = item["link"]

    rough_string = ET.tostring(rss, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def main():
    all_items = []
    all_items += fetch_zeus()
    all_items += fetch_dokkaebi()
    all_items += fetch_eclipse()
    
    rss_content = build_rss(all_items)
    with open("ban-notice.rss", "w", encoding="utf-8") as f:
        f.write(rss_content)
    print(f"✅ 生成完成，共抓取 {len(all_items)} 条公告")
    print(f"   - 宙斯: {len([i for i in all_items if i['site']=='宙斯'])} 条")
    print(f"   - 鬼怪世界: {len([i for i in all_items if i['site']=='鬼怪世界'])} 条")

if __name__ == "__main__":
    main()
