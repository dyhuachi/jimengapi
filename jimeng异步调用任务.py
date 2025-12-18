import json
import sys
import os
import base64
import datetime
import hashlib
import hmac
import requests

method = 'POST'
host = 'visual.volcengineapi.com'
region = 'cn-north-1'
endpoint = 'https://visual.volcengineapi.com'
service = 'cv'


def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(key.encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'request')
    return kSigning


def formatQuery(parameters):
    request_parameters_init = ''
    for key in sorted(parameters):
        request_parameters_init += key + '=' + parameters[key] + '&'
    request_parameters = request_parameters_init[:-1]
    return request_parameters


def signV4Request(access_key, secret_key, service, req_query, req_body):
    if access_key is None or secret_key is None:
        print('No access key is available.')
        sys.exit()

    t = datetime.datetime.utcnow()
    current_date = t.strftime('%Y%m%dT%H%M%SZ')
    # current_date = '20210818T095729Z'
    datestamp = t.strftime('%Y%m%d')  # Date w/o time, used in credential scope
    canonical_uri = '/'
    canonical_querystring = req_query
    signed_headers = 'content-type;host;x-content-sha256;x-date'
    payload_hash = hashlib.sha256(req_body.encode('utf-8')).hexdigest()
    content_type = 'application/json'
    canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + host + \
                        '\n' + 'x-content-sha256:' + payload_hash + \
                        '\n' + 'x-date:' + current_date + '\n'
    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + \
                        '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
    # print(canonical_request)
    algorithm = 'HMAC-SHA256'
    credential_scope = datestamp + '/' + region + '/' + service + '/' + 'request'
    string_to_sign = algorithm + '\n' + current_date + '\n' + credential_scope + '\n' + hashlib.sha256(
        canonical_request.encode('utf-8')).hexdigest()
    # print(string_to_sign)
    signing_key = getSignatureKey(secret_key, datestamp, region, service)
    # print(signing_key)
    signature = hmac.new(signing_key, (string_to_sign).encode(
        'utf-8'), hashlib.sha256).hexdigest()
    # print(signature)

    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + \
                           credential_scope + ', ' + 'SignedHeaders=' + \
                           signed_headers + ', ' + 'Signature=' + signature
    # print(authorization_header)
    headers = {'X-Date': current_date,
               'Authorization': authorization_header,
               'X-Content-Sha256': payload_hash,
               'Content-Type': content_type
               }
    # print(headers)

    # ************* SEND THE REQUEST *************
    request_url = endpoint + '?' + canonical_querystring

    print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
    print('Request URL = ' + request_url)
    try:
        r = requests.post(request_url, headers=headers, data=req_body)
    except Exception as err:
        print(f'error occurred: {err}')
        raise
    else:
        print('\nRESPONSE++++++++++++++++++++++++++++++++++++')
        print(f'Response code: {r.status_code}\n')
        # 使用 replace 方法将 \u0026 替换为 &
        resp_str = r.text.replace("\\u0026", "&")
        print(f'Response body: {resp_str}\n')


if __name__ == "__main__":
    # 请求凭证，从访问控制申请
    access_key = ''
    secret_key = ''
    # 请求Query，按照接口文档中填入即可
    query_params = {
        'Action': 'CVSync2AsyncSubmitTask',
        'Version': '2022-08-31',
    }
    formatted_query = formatQuery(query_params)

    def image_to_base64_with_prefix(image_path_or_url):
        """将图片（本地路径或网络 URL）转为带 data:image/...;base64, 前缀的字符串"""
        if image_path_or_url.startswith(("http://", "https://")):
            # 网络图片
            response = requests.get(image_path_or_url)
            response.raise_for_status()
            content = response.content
            # 推断 MIME 类型（简单判断）
            if image_path_or_url.lower().endswith('.png'):
                mime = 'png'
            elif image_path_or_url.lower().endswith(('.jpg', '.jpeg')):
                mime = 'jpeg'
            else:
                # 保守默认为 png
                mime = 'png'
        else:
            # 本地文件
            with open(image_path_or_url, "rb") as f:
                content = f.read()
            ext = os.path.splitext(image_path_or_url)[-1].lower()
            if ext == '.png':
                mime = 'png'
            elif ext in ('.jpg', '.jpeg'):
                mime = 'jpeg'
            else:
                mime = 'png'  # 默认

        b64_str = base64.b64encode(content).decode('utf-8')
        return f"data:image/{mime};base64,{b64_str}"
    image_input = "/home/dieu/桌面/03_155836_413.png"  # 也可以用本地路径
    image_b64_with_prefix = image_to_base64_with_prefix(image_input)
    # 请求Body，按照接口文档中填入即可
    body_params = {
        "req_key": "jimeng_t2i_v40",
        "image_urls": ["https://vcg03.cfp.cn/creative/vcg/800/new/VCG41N695939918.jpg",
    ],
        "prompt": "优化生成二创漫画风格图片"
    }
    formatted_body = json.dumps(body_params)

    signV4Request(access_key, secret_key, service,
                  formatted_query, formatted_body)


"""
BEGIN REQUEST++++++++++++++++++++++++++++++++++++
Request URL = https://visual.volcengineapi.com?Action=CVSync2AsyncSubmitTask&Version=2022-08-31

RESPONSE++++++++++++++++++++++++++++++++++++
Response code: 200

Response body: {"code":10000,"data":{"task_id":"16013983710365462014"},"message":"Success","request_id":"20251120172434C3772FA8E2287000DA80","status":10000,"time_elapsed":"31.122275ms"}

"""
