import subprocess
import hashlib
import json
import threading
import time
from datetime import datetime
import curl_cffi.requests as cffirequests  # 使用curl_cffi.requests

num_requests = 1  # 请求数量
interval_ms = 800  # 间隔时间, 毫秒
acid = "1816854086004391938"  # 活动id
ackl = "茉莉奶绿 白月光"  # 口令
authorizations = [
    ''
]

def get_signature(url):
    result = subprocess.run(['node', 'signature.js', url], capture_output=True, text=True)
    signature = result.stdout.strip()  # 获取返回值并去掉首尾空白
    return signature

def md5_hash(text):
    m = hashlib.md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()

def getSign(d):
    sorted_items = sorted(d.items())
    formatted_string = '&'.join(f'{key}={value}' for key, value in sorted_items)
    return md5_hash(f'{formatted_string}c274bac6493544b89d9c4f9d8d542b84')

url = 'https://mxsa.mxbc.net/api/v1/h5/marketing/secretword/confirm'

def get_proxies():
    # 快代理获取代理
    api_url = ""
    proxy_ip = cffirequests.get(api_url).text.strip()  # 获取代理IP
    username = ""
    password = ""

    return {
        "http": f"http://{username}:{password}@{proxy_ip}",
        "https": f"http://{username}:{password}@{proxy_ip}",
        "timestamp": time.time()
    }

def make_request(authorization, index, _, proxies):
    try:
        headers = {'Access-Token': authorization,
                   'Content-Type': 'application/json'}

        payload = {
            "marketingId": acid,
            "round": f'{datetime.now().hour}:00',
            "secretword": ackl,
            "s": 2,
            "stamp": int(time.time() * 1000)
        }
        payload['sign'] = getSign(payload)

        type_value = get_signature(json.dumps(payload))  # 将payload转换为JSON字符串
        complete_url = f"{url}?type__1286={type_value}"

        # Debug output
        print(f'完整的URL: {complete_url}')

        response = cffirequests.post(
            complete_url,
            data=json.dumps(payload),
            headers=headers,
            proxies={
                "http": proxies["http"],
                "https": proxies["https"]
            }
        )

        curTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        proxy_url = proxies['https']

        print(f'账号{index + 1}，第{_ + 1}次请求，代理：{proxy_url}，时间：{curTime}，结果：{response.text}')
        if response.status_code != 200:
            print(f'账号{index + 1}，第{_ + 1}次请求，代理：{proxy_url}，时间：{curTime}，错误：{response.status_code} {response.reason}')

    except Exception as e:
        proxy_url = proxies['https']
        curTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f'账号{index + 1}，第{_ + 1}次请求，代理：{proxy_url}，时间：{curTime}，发生异常：{e}')

def make_threaded_requests(authorizations, interval_ms, num_requests):
    proxies_by_authorization = {}

    for index, authorization in enumerate(authorizations):
        proxies_by_authorization[authorization] = get_proxies()

    for _ in range(num_requests):
        for index, authorization in enumerate(authorizations):
            proxies = proxies_by_authorization[authorization]
            if time.time() - proxies.get('timestamp', 0) > 180:
                proxies_by_authorization[authorization] = get_proxies()
                proxies = proxies_by_authorization[authorization]

            threading.Thread(target=make_request, args=(authorization, index, _, proxies)).start()

        time.sleep(interval_ms / 1000)

if __name__ == "__main__":
    make_threaded_requests(authorizations, interval_ms, num_requests)
