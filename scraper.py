import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_zeus():
    """抓取 宙斯：傲慢之神 公告"""
    items = []
    try:
        url = "https://zeus.com2us.com/news/notice"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")
        
        rows = soup.select("ul.news_list li, .notice_list li, li")
        for row in rows[:20]:
            a_tag = row.select_one("a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)
            link = a_tag.get("href", "")
            if link and not link.startswith("http"):
                link = "https://zeus.com2us.com" + link
            
            date_tag = row.select_one(".date, span.date, .time")
            date_str = date_tag.get_text(strip=True) if date_tag else ""
            
            if title and link:
                items.append({"title": title, "link": link, "date": date_str, "site": "宙斯"})
    except Exception as e:
        print(f"宙斯抓取失败: {e}")
    return items

def fetch_dokkaebi():
    """抓取 鬼怪世界 公告"""
    items = []
    try:
        url = "https://forum.kakaogames.com/dokkaebi/postList/?code=notice"
        session = requests.Session()
        session.cookies.set("consent", "yes", domain=".kakaogames.com")
        resp = session.get(url, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")
        
        rows = soup.select(".board_list li, .list_area li, tr")
        for row in rows[:20]:
            a_tag = row.select_one("a.tit, .subject a, a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)
            link = a_tag.get("href", "")
            if link and not link.startswith("http"):
                link = "https://forum.kakaogames.com" + link
            
            date_tag = row.select_one(".date, .time")
            date_str = date_tag.get_text(strip=True) if date_tag else ""
            
            if title and link:
                items.append({"title": title, "link": link, "date": date_str, "site": "鬼怪世界"})
    except Exception as e:
        print(f"鬼怪世界抓取失败: {e}")
    return items

def fetch_eclipse():
    """抓取 日蚀觉醒 公告"""
    items = []
    try:
        url = "https://page.onstove.com/eclipse/kr/list/146438"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")
        
        rows = soup.select(".list_item, .board-row, article")
        for row in rows[:20]:
            a_tag = row.select_one("a.title, .subject a, a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)
            link = a_tag.get("href", "")
            if link and not link.startswith("http"):
                link = "https://page.onstove.com" + link
            
            date_tag = row.select_one(".date, .time")
            date_str = date_tag.get_text(strip=True) if date_tag else ""
            
            if title and link:
                items.append({"title": title, "link": link, "date": date_str, "site": "日蚀觉醒"})
    except Exception as e:
        print(f"日蚀觉醒抓取失败: {e}")
    return items

def build_rss(all_items):
    """生成标准RSS文件"""
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "韩游封号公告聚合RSS"
    ET.SubElement(channel, "link").text = "https://github.com/jasonhao1993/game-ban-rss"
    ET.SubElement(channel, "description").text = "自动抓取宙斯、鬼怪世界、日蚀觉醒官方公告"
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

if __name__ == "__main__":
    main()
