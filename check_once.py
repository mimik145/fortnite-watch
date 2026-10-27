"""
Одна проверка магазина Fortnite для GitHub Actions.
Название скина и топик ntfy берутся из переменных окружения
(их задаёт файл fortnite.yml).
"""
import os

import requests

SKIN_NAME = os.environ["SKIN_NAME"]
NTFY_TOPIC = os.environ["NTFY_TOPIC"]
API_URL = "https://fortnite-api.com/v2/shop"


def collect_names(node, out: set) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "name" and isinstance(value, str):
                out.add(value)
            else:
                collect_names(value, out)
    elif isinstance(node, list):
        for item in node:
            collect_names(item, out)


def set_output(key: str, value: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")


def main() -> None:
    try:
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()
        names = set()
        collect_names(response.json(), names)
    except Exception as e:
        # Временные ошибки API не должны ронять запуск и слать письма об ошибке
        print("Ошибка при запросе магазина:", e)
        return

    hits = sorted(n for n in names if SKIN_NAME.lower() in n.lower())
    if not hits:
        print("Пока нет в магазине.")
        return

    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=f"Скин в магазине: {', '.join(hits)}".encode("utf-8"),
        headers={"Title": "Fortnite shop", "Priority": "high"},
        timeout=15,
    )
    print("Найдено, уведомление отправлено:", hits)
    set_output("found", "true")


if __name__ == "__main__":
    main()
