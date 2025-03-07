import os

import uvicorn
from fastapi import FastAPI, Request, HTTPException
import logging

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

logging.basicConfig(level=logging.INFO)


@app.get("/webhook")
async def verify_webhook(request: Request):
    """ Верифікація вебхука під час налаштування в Meta. """
    params = await request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logging.info("Webhook verified successfully.")
        return int(challenge)
    else:
        raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook/comments")
async def receive_comments(request: Request):
    """ Обробка отриманих коментарів під постами. """
    data = await request.json()
    logging.info(f"Received Comment Webhook: {data}")

    if "entry" in data:
        for entry in data["entry"]:
            if "changes" in entry:
                for change in entry["changes"]:
                    if change["field"] == "comments":
                        comment_id = change["value"]["id"]
                        comment_message = change["value"]["message"]
                        logging.info(f"New comment: {comment_message} (ID: {comment_id})")

    return {"status": "ok"}


@app.post("/webhook/messages")
async def receive_messages(request: Request):
    """ Обробка отриманих повідомлень у Direct. """
    data = await request.json()
    logging.info(f"Received Direct Message Webhook: {data}")

    if "entry" in data:
        for entry in data["entry"]:
            if "messaging" in entry:
                for event in entry["messaging"]:
                    sender_id = event["sender"]["id"]
                    message_text = event.get("message", {}).get("text", "")
                    logging.info(f"New message from {sender_id}: {message_text}")

    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
