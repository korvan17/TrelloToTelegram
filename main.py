from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI()

# Класс для парсинга входящего запроса
class ListIdRequest(BaseModel):
    idList: str

# Асинхронная функция для отправки сообщений в Telegram
async def send_text_to_telegram(text: str, chat_id: str, bot_token: str):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_notification": False
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=data)

# Функция для получения списка и карточек из Trello и отправки в Telegram
@app.post("/send-trello-list-to-telegram/")
async def send_trello_list_to_telegram(request: ListIdRequest, chat_id: str, bot_token: str, trello_key: str, trello_token: str):
    id_list = request.idList
    trello_list_url = f"https://api.trello.com/1/lists/{id_list}?key={trello_key}&token={trello_token}"
    trello_cards_url = f"https://api.trello.com/1/lists/{id_list}/cards?key={trello_key}&token={trello_token}"
    
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
        
        await send_text_to_telegram(message, chat_id, bot_token)
        
        return {"message": "Success"}
