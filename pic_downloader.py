import requests
import os
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json
import base64

# 创建保存目录和下载记录文件
if not os.path.exists('pic2'):
    os.makedirs('pic2')

# 下载记录文件路径
DOWNLOAD_RECORD = 'downloaded_images.json'

def load_download_record():
    """加载已下载图片记录"""
    try:
        if os.path.exists(DOWNLOAD_RECORD):
            with open(DOWNLOAD_RECORD, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        return set()
    except Exception as e:
        print(f"加载下载记录时出错: {e}")
        return set()

def save_download_record(downloaded_images):
    """保存下载记录"""
    try:
        with open(DOWNLOAD_RECORD, 'w', encoding='utf-8') as f:
            json.dump(list(downloaded_images), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存下载记录时出错: {e}")

# 随机User-Agent列表
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
]

def get_random_headers():
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Referer': 'https://jandan.net/'
    }

def download_image(url, filename, downloaded_images):
    """下载图片并记录"""
    # 如果图片已下载过，跳过
    if url in downloaded_images:
        print(f'已存在，跳过: {filename}')
        return True
        
    try:
        response = requests.get(url, headers=get_random_headers(), timeout=10)
        if response.status_code == 200:
            with open(os.path.join('pic2', filename), 'wb') as f:
                f.write(response.content)
            # 添加到已下载记录
            downloaded_images.add(url)
            print(f'成功下载: {filename}')
            # 每下载10张图片保存一次记录
            if len(downloaded_images) % 10 == 0:
                save_download_record(downloaded_images)
            return True
    except Exception as e:
        print(f'下载失败 {url}: {str(e)}')
    return False

def is_valid_date(post_time):
    target_date = datetime(2025, 2, 18, 9, 0)
    try:
        post_datetime = datetime.strptime(post_time, '%Y-%m-%d %H:%M:%S')
        return post_datetime > target_date
    except:
        return False

def decode_image_url(encoded_string):
    """解码图片URL"""
    try:
        # 移除可能的 base64 前缀
        if ',' in encoded_string:
            encoded_string = encoded_string.split(',')[1]
        # 解码base64
        decoded = base64.b64decode(encoded_string).decode('utf-8')
        return decoded
    except:
        return None

def get_page_id(page_num):
    """生成页面ID"""
    # 格式：20250220-xxx，其中xxx是从219开始递减的页码
    start_page = 219  # 2月18日9点后的起始页
    current_page = start_page - (page_num - 1)
    date_str = "20250220"  # 固定日期
    page_str = f"{date_str}-{current_page}"
    # 转换为base64
    encoded = base64.b64encode(page_str.encode()).decode()
    return encoded

def get_post_time(soup):
    """获取页面中帖子的时间"""
    try:
        time_elements = soup.find_all('span', class_='time')
        if time_elements:
            for time_elem in time_elements:
                time_text = time_elem.text.strip()
                try:
                    post_time = datetime.strptime(time_text, '%Y-%m-%d %H:%M:%S')
                    return post_time
                except:
                    continue
    except Exception as e:
        print(f"获取时间出错: {e}")
    return None

def main():
    # 加载已下载记录
    downloaded_images = load_download_record()
    print(f"已下载图片数量: {len(downloaded_images)}")
    
    target_date = datetime(2025, 2, 18, 9, 0)  # 目标时间
    current_page = 219  # 从最新页面开始
    
    try:
        while True:
            try:
                url = f'https://jandan.net/pic/MjAyNTAyMjAtMTc{current_page}'
                print(f"\n正在处理页面: {url}")
                print(f"当前页码: {current_page}")
                
                response = requests.get(url, headers=get_random_headers())
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 检查页面时间
                page_time = get_post_time(soup)
                if page_time and page_time < target_date:
                    print(f"已到达目标时间（{target_date}），停止下载")
                    break
                
                # 查找所有图片链接
                image_links = []
                for link in soup.find_all('a', class_='view_img_link'):
                    if link.get('href'):
                        if link['href'].lower().endswith(('.jpg', '.png')):
                            image_links.append(link['href'])
                
                if not image_links:
                    print(f"页面 {current_page} 没有找到图片")
                    current_page -= 1
                    continue
                    
                print(f"找到 {len(image_links)} 张图片")
                
                # 下载图片
                for img_url in image_links:
                    if not img_url.startswith('http'):
                        img_url = 'https:' + img_url if img_url.startswith('//') else 'https://' + img_url
                    
                    filename = img_url.split('/')[-1]
                    if download_image(img_url, filename, downloaded_images):
                        time.sleep(random.uniform(3, 6))
                
                print(f"完成页面 {current_page}")
                current_page -= 1
                time.sleep(random.uniform(8, 12))
                
            except Exception as e:
                print(f'处理页面 {current_page} 时出错: {str(e)}')
                print("等待15-20秒后继续...")
                time.sleep(random.uniform(15, 20))
                current_page -= 1
                continue
    finally:
        save_download_record(downloaded_images)
        print(f"\n下载完成，共记录 {len(downloaded_images)} 张图片")

if __name__ == '__main__':
    main()