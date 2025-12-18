# coding: utf-8
from __future__ import print_function

import base64
import os
from volcengine.visual.VisualService import VisualService

if __name__ == '__main__':
    visual_service = VisualService()
    visual_service.set_ak('')
    visual_service.set_sk('')

    form = {
        "req_key": "jimeng_t2i_v40",
        "task_id":"15211283572580955195"
    }

    try:
        resp = visual_service.cv_get_result(form)
        print("✅ API 调用成功！")

        # 检查返回状态
        if resp.get("code") != 10000:
            print(f"❌ API 返回错误: {resp.get('message')}")
            exit(1)

        data = resp.get("data", {})
        base64_list = data.get("binary_data_base64", [])

        if not base64_list:
            print("⚠️ 未找到图片数据（binary_data_base64 为空）")
            exit(1)

        # 保存第一张图片（通常只有一张）
        img_b64 = base64_list[0]
        img_data = base64.b64decode(img_b64)

        # 设置保存路径
        output_path = "output—2创.jpg"  # 也可改为 output.png，但内容仍是 JPEG
        with open(output_path, "wb") as f:
            f.write(img_data)

        print(f"✅ 图片已保存到: {os.path.abspath(output_path)}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")
