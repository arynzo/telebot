from telethon.sync import TelegramClient
from telethon.tl.functions.messages import SendMessageRequest
from flask import Flask, jsonify

# Configuration
api_id = '29217793'
api_hash = '936dd3cb9bb2a708f96c0a3761150133'
bot_username = '@TrueCaller_Z_Bot'  # without @
bot_message = '7044992446'

# Telethon client setup
client = TelegramClient('session_name', api_id, api_hash)

app = Flask(__name__)

@app.route("/send", methods=['GET'])
def send_message():
    with client:
        # Bot ko message bhejna
        client.send_message(bot_username, bot_message)

        # Reply wait karna (last message fetch karna)
        messages = client.get_messages(bot_username, limit=2)
        reply = messages[0].message if messages else "No response"

        return jsonify({
            "sent": bot_message,
            "received": reply
        })

if __name__ == '__main__':
    app.run()
