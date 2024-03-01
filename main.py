from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv
import os

load_dotenv()  # Загружает переменные окружения из файла .env, если он существует

app = FastAPI()

# Получаем переменные окружения
CHAT_ID = os.getenv("CHAT_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")

# Класс для парсинга входящего запроса
class ListIdRequest(BaseModel):
    idList: str

# Асинхронная функция для отправки сообщений в Telegram
async def send_text_to_telegram(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_notification": False
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=data)

# Функция для получения списка и карточек из Trello и отправки в Telegram
@app.post("/send-trello-list-to-telegram/")
async def send_trello_list_to_telegram(request: ListIdRequest):
    id_list = request.idList
    trello_list_url = f"https://api.trello.com/1/lists/{id_list}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    trello_cards_url = f"https://api.trello.com/1/lists/{id_list}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    
    async with httpx.AsyncClient() as client:
        list_response = await client.get(trello_list_url)
        if list_response.status_code != 200:
            raise HTTPException(status_code=list_response.status_code, detail="Error fetching list from Trello")
        list_data = list_response.json()
        
        cards_response = await client.get(trello_cards_url)
        if cards_response.status_code != 200:
            raise HTTPException(status_code=cards_response.status_code, detail="Error fetching cards from Trello")
        cards_data = cards_response.json()
        
        message = f"{list_data['name']}\n\n"
        for card in cards_data:
            card_name = card['name'].replace("\n\n+", "\n")
            message += f"{card_name}\n\n"
        
        await send_text_to_telegram(message)
        
        return {"message": "Success"}




# from dotenv import load_dotenv

# load_dotenv()  # Загружает переменные окружения из файла .env, если он существует

# import os
# import requests

# def send_telegram_message(bot_token, chat_id, message):
#     url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
#     data = {"chat_id": chat_id, "text": message}
#     response = requests.post(url, data=data)
#     return response.json()

# if __name__ == "__main__":
#     # Чтение значений из переменных окружения
#     bot_token = os.getenv('BOT_TOKEN')
#     chat_id = os.getenv('CHAT_ID')
    
#     # Чтение сообщения из переменной окружения
#     message = os.getenv('MESSAGE', 'Hello World!')  # Если MESSAGE не установлен, используется 'Hello World!'

#     if not bot_token or not chat_id:
#         print("Error: The BOT_TOKEN and CHAT_ID environment variables are required.")
#         sys.exit(1)

#     response = send_telegram_message(bot_token, chat_id, message)
#     print(response)
