import requests
import time
import random
from datetime import datetime
from config import bot_token, owner_bot_token, owner_id

# Telegram API URLs
get_updates_url = f'https://api.telegram.org/bot{bot_token}/getUpdates'
send_message_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

# Owner bot API URL
owner_message_url = f'https://api.telegram.org/bot{owner_bot_token}/sendMessage'

# List of emojis
default_emoji = "👍"  # Default emoji for users
my_emoji = ["👍", "❤", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🎉", "🤩", 
            "🙏", "👌", "😍", "❤‍🔥", "🌚", "💯", "🤣", "💔", "🇮🇳", 
            "😈", "😭", "🤓", "😇", "🤝", "🤗", "🫡", "🤪", "🗿", "💀"]

# To keep track of the last update and user data
last_update_id = None
user_data = {}

def get_new_messages():
    """Fetch new messages from the bot."""
    global last_update_id
    params = {'timeout': 100}  # Wait for 100 seconds for new updates
    if last_update_id:
        params['offset'] = last_update_id + 1

    response = requests.get(get_updates_url, params=params)
    
    if response.status_code == 200:
        return response.json()
    return None

def send_message(chat_id, text):
    """Send a message to the specified chat."""
    owner_credit = "\n\n*Owner: @Jukerhenapadega*"
    data = {
        "chat_id": chat_id,
        "text": text + owner_credit,
        "parse_mode": "Markdown"
    }
    requests.post(send_message_url, json=data)

def notify_owner(username, user_id, registration_time):
    """Send registration details to the owner bot."""
    owner_message = (
        f"New user registered:\n"
        f"- Username: {username}\n"
        f"- User ID: {user_id}\n"
        f"- Time: {registration_time}\n\n"
        f"*Owner: @Jukerhenapadega*"
    )
    
    data = {
        "chat_id": owner_id,
        "text": owner_message,
        "parse_mode": "Markdown"
    }
    requests.post(owner_message_url, json=data)

def register_user(user_id, username):
    """Register a new user."""
    registration_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_data[user_id] = {
        "username": username,
        "registration_time": registration_time,
        "emoji": default_emoji  # Set default emoji
    }
    notify_owner(username, user_id, registration_time)
    return f"Welcome {username}! You have been registered."

def handle_commands(update):
    """Handle incoming commands."""
    message = update['message']
    chat_id = message['chat']['id']
    user_id = message['from']['id']
    username = message['from'].get('username', 'Unknown User')

    if 'text' in message:
        command = message['text'].strip()

        if command == '/start':
            # Automatically register the user
            response_message = register_user(user_id, username)
            send_message(chat_id, response_message)

        elif command == '/register':
            response_message = register_user(user_id, username)
            send_message(chat_id, response_message)

        elif command.startswith('/setemoji'):
            _, emoji = command.split(' ', 1)
            if emoji in my_emoji:
                user_data[user_id]["emoji"] = emoji
                send_message(chat_id, f"Emoji set to: {emoji}")
            else:
                send_message(chat_id, "Invalid emoji. Please select from the predefined list.")

        elif command == '/removeemoji':
            user_data[user_id]["emoji"] = default_emoji
            send_message(chat_id, "Emoji removed. Reset to default.")

        elif command.startswith('/setgrouplink'):
            _, new_link = command.split(' ', 1)
            send_message(chat_id, f"Group link updated to: {new_link}")
            # You can add functionality to store this link in a variable or database

        elif command.startswith('/broadcast'):
            _, broadcast_text = command.split(' ', 1)
            # Implement broadcasting logic here
            send_message(chat_id, f"Broadcasting message: {broadcast_text}")

        elif command == '/help':
            help_message = (
                "Available commands:\n"
                "/start - Register yourself\n"
                "/register - Register your username\n"
                "/setemoji <emoji> - Set your own emoji\n"
                "/removeemoji - Remove your emoji\n"
                "/setgrouplink <link> - Set the group link\n"
                "/broadcast <message> - Send a message to all users\n"
                "/help - Show this help message"
            )
            send_message(chat_id, help_message)

def main():
    global last_update_id

    while True:
        updates = get_new_messages()
        
        if updates and updates.get('ok'):
            for update in updates['result']:
                if 'message' in update:
                    message = update['message']
                    handle_commands(update)
                    last_update_id = update['update_id']

        time.sleep(2)

if __name__ == "__main__":
    main()
