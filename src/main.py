import os
import sys
import time
import pytz
import requests
import traceback

from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from src.common.config import env, Env, config
from src.common.logger import Logger, Color

logger = Logger()

webhook_url = config.get("webhook_url")
product_name = config.get("product_name")
file_id = config.get("file_id")
version_file_path = os.path.join(config.get("version_file_path"), f"figma_version_{product_name}.txt")

headers = {
    "X-FIGMA-TOKEN": f'{config.get("personal_access_token")}',
}


def run():
    try:
        with open(version_file_path, "r") as f:
            last_sent_version_id = f.read()
    except FileNotFoundError:
        last_sent_version_id = None

    try:
        response = requests.get(f"https://api.figma.com/v1/files/{file_id}/versions", headers=headers)

        if response.status_code == 200:
            data = response.json()
            versions = data.get("versions", [])

            if versions:
                latest_version = versions[0]

                if latest_version["id"] != last_sent_version_id:
                    figma_time = latest_version["created_at"]
                    figma_datetime = datetime.strptime(figma_time, "%Y-%m-%dT%H:%M:%SZ")
                    seoul_timezone = pytz.timezone("Asia/Seoul")
                    figma_datetime = figma_datetime.replace(tzinfo=pytz.utc).astimezone(seoul_timezone)
                    formatted_time = figma_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
                    payload = {
                        "content": "새로운 버전 업데이트가 있습니다.",
                        "embeds": [
                            {
                                "title": "버전 업데이트",
                                "description": f'담당자: {latest_version["user"]["handle"]}\n'
                                f"수정한 시간: {formatted_time}\n"
                                f'변경 사항: {latest_version["description"]}\n'
                                f'링크: [바로가기](https://www.figma.com/file/{file_id}?version-id={latest_version["id"]}) \n',
                                "thumbnail": {"url": latest_version["user"]["img_url"]},
                                "color": 2680256,
                                "author": {
                                    "name": product_name,
                                    "url": f"https://www.figma.com/file/{file_id}",
                                    "icon_url": "https://imagestorage.pcor.me/images/2023/10/07/Group-3.png",
                                },
                                "image": {"url": latest_version["thumbnail_url"]},
                            }
                        ],
                        "username": "UI Figma",
                        "avatar_url": "https://imagestorage.pcor.me/images/2023/10/07/Group-3.png",
                    }

                    response = requests.post(webhook_url, json=payload)
                    if response.status_code == 204:
                        logger.debug("새로운 Figma 파일 버전이 성공적으로 전송되었습니다.")

                    with open(version_file_path, "w") as f:
                        f.write(latest_version["id"])
                else:
                    logger.debug("새로운 버전이 없습니다.")
            else:
                logger.debug("Figma 파일 버전을 찾을 수 없습니다.", color=Color.RED)
                exit(1)
        else:
            logger.debug("Figma API 요청에 실패했습니다.", color=Color.RED)
            logger.error(response.text)
    except Exception:
        logger.debug("Figma API 요청에 실패했습니다.", color=Color.RED)
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    run()
    while env == Env.PROD:
        time.sleep(60)
