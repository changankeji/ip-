import requests
import time
import json
import threading

api_url = "这是你的api"

result_file = "api_result.txt"
all_proxies = set()
all_proxies_lock = threading.Lock()

# 如果文件已存在，先读取已有内容，避免重复
def load_existing_proxies():
    try:
        with open(result_file, "r", encoding="utf-8") as f:
            for line in f:
                all_proxies.add(line.strip())
    except FileNotFoundError:
        pass

def fetch_and_save_proxies(sleep_enable=True, mode="txt", thread_id=1):
    i = 0
    while True:
        i += 1
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                if mode == "json":
                    try:
                        data = response.json()
                    except json.JSONDecodeError:
                        print(f"[线程{thread_id}] 第{i}次返回内容不是有效JSON")
                        if sleep_enable:
                            time.sleep(1)
                        continue
                    if data.get("code") == 200 and "data" in data and "proxies" in data["data"]:
                        proxies = data["data"]["proxies"]
                        with all_proxies_lock:
                            new_proxies = [p.strip() for p in proxies if p.strip() and p.strip() not in all_proxies]
                            if new_proxies:
                                with open(result_file, "a", encoding="utf-8") as f:
                                    for proxy in new_proxies:
                                        f.write(proxy + "\n")
                                        all_proxies.add(proxy)
                                print(f"[线程{thread_id}] 第{i}次API内容已保存 {len(new_proxies)} 条新代理")
                            else:
                                print(f"[线程{thread_id}] 第{i}次API无新代理")
                    else:
                        print(f"[线程{thread_id}] 第{i}次API返回格式不符或无代理")
                else:  # txt模式
                    content = response.text
                    with all_proxies_lock:
                        lines = [line.strip() for line in content.splitlines() if line.strip() and line.strip() not in all_proxies]
                        if lines:
                            with open(result_file, "a", encoding="utf-8") as f:
                                for line in lines:
                                    f.write(line + "\n")
                                    all_proxies.add(line)
                            print(f"[线程{thread_id}] 第{i}次API内容已保存 {len(lines)} 条新代理")
                        else:
                            print(f"[线程{thread_id}] 第{i}次API无新代理")
            else:
                print(f"[线程{thread_id}] 第{i}次请求失败，状态码：{response.status_code}")
        except Exception as e:
            print(f"[线程{thread_id}] 第{i}次请求异常: {e}")
        if sleep_enable:
            time.sleep(1)  # 间隔1秒

def start_threads(thread_count, sleep_enable, mode):
    threads = []
    for t_id in range(1, thread_count + 1):
        t = threading.Thread(target=fetch_and_save_proxies, args=(sleep_enable, mode, t_id))
        t.daemon = True
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == "__main__":
    load_existing_proxies()
    user_input = input("是否开启每次请求间隔1秒？(y/n): ").strip().lower()
    sleep_enable = user_input == 'y'
    mode_input = input("请选择模式（txt/json）：").strip().lower()
    if mode_input not in ["txt", "json"]:
        print("输入有误，默认使用txt模式")
        mode_input = "txt"
    thread_input = input("是否启用多线程？(y/n): ").strip().lower()
    if thread_input == 'y':
        while True:
            try:
                thread_count = int(input("请输入线程数(1-5): ").strip())
                if 1 <= thread_count <= 5:
                    break
                else:
                    print("线程数必须在1到5之间！")
            except ValueError:
                print("请输入有效数字！")
        start_threads(thread_count, sleep_enable, mode_input)
    else:
        fetch_and_save_proxies(sleep_enable=sleep_enable, mode=mode_input, thread_id=1)
