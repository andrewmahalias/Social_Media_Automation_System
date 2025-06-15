import logging
import os

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi import Response

from bot_instance import (bot,
                          messages_handler,
                          load_config,
                          comments_handler)
from instabot.main import handle_comment, handle_direct_message

from instabot.state_manager import BotState, state_manager

app = FastAPI()
config = load_config("insta_config.json")

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")  # todo: get the token on Meta for Developers?

logging.basicConfig(level=logging.INFO)


@app.get("/webhook")
async def verify_webhook(request: Request):
    """ Verify webhook endpoint. """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logging.info("Webhook verified successfully.")
        return Response(content=challenge, media_type="text/plain")
    else:
        raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook/comments")
async def receive_comments(request: Request):
    """Comments webhook handler."""
    data = await request.json()
    logging.info(f"Received Comment Webhook: {data}")

    if data.get("field") == "comments":
        value = data.get("value", {})
        comment_message = value.get("text")
        user_id = int(value["from"]["id"])
        username = value["from"]["username"]

        # logging.info(f"New comment from @{username}: {comment_message}")

        bot.get_target_id(user_id)
        bot.get_username(username)

        # Filter comments based on keywords
        if comments_handler.filter_comments_by_keywords(comment_message):
            current_state = state_manager.get_state(user_id)

            if current_state == BotState.IDLE:
                handle_comment(user_id, comment_message, username)

    return {"status": "ok"}


@app.post("/webhook/messages")
async def receive_messages(request: Request):
    """Messages webhook handler."""
    data = await request.json()
    logging.info(f"Received Direct Message Webhook: {data}")

    if "entry" in data:
        for entry in data["entry"]:
            if "messaging" in entry:
                for event in entry["messaging"]:
                    sender_id = event["sender"]["id"]
                    message_text = event.get("message", {}).get("text", "")
                    messages_handler.find_command(message_text)
                    logging.info(f"New message from {sender_id}: {message_text}")
                    handle_direct_message(sender_id, message_text)

    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
