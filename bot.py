# bot.py
import requests
import time
import random
from datetime import datetime
from config import bot_token, owner_id, group_link  # Importing configurations

# Telegram API URLs
get_updates_url = f'https://api.telegram.org/bot{bot_token}/getUpdates'
send_message_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
registered_users = {}

# List of emojis for user selection
allowed_emojis = ["👍", "❤", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🎉", "🤩", 
                  "🙏", "👌", "😍", "❤‍🔥", "🌚", "💯", "🤣", "💔", "🇮🇳", 
                  "😈", "😭", "🤓", "😇", "🤝", "🤗", "🫡", "🤪", "🗿", "💀"]

default_emoji = "😊"  # Default emoji for users who don't choose one

# To keep track of the last update so we don't repeat reactions
last_update_id = None

def get_new_messages():
    """Fetch new messages from the bot."""
    global last_update_id
    params = {'timeout': 100}
    if last_update_id:
        params['offset'] = last_update_id + 1

    response = requests.get(get_updates_url, params=params)
    
    if response.status_code == 200:
        return response.json()
    return None

def send_message(chat_id, text, reply_markup=None):
    """Send a message to the specified chat."""
    data = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": reply_markup,
        "parse_mode": "Markdown"
    }
    response = requests.post(send_message_url, json=data)
    return response

def start_command(chat_id):
    """Handle the /start command."""
    welcome_text = "Welcome to the bot! Please join our group to use the bot features: " + group_link
    send_message(chat_id, welcome_text)

def register_user(user_id, username, chat_id):
    """Register a new user if they are in the group."""
    if user_id not in registered_users:
        registration_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        registered_users[user_id] = {
            "username": username,
            "chat_id": chat_id,
            "registration_time": registration_time,
            "emoji": default_emoji  # Assign default emoji
        }
        send_message(chat_id, f"Successfully registered!\nYour ID: {user_id}\nUsername: {username}\nTime: {registration_time}\nYour Emoji: {default_emoji}")
    else:
        send_message(chat_id, "You are already registered!")

def set_user_emoji(user_id, emoji):
    """Set a custom emoji for the user."""
    if user_id in registered_users and emoji in allowed_emojis:
        registered_users[user_id]["emoji"] = emoji
        send_message(registered_users[user_id]["chat_id"], f"Your emoji has been updated to: {emoji}")
    else:
        send_message(registered_users[user_id]["chat_id"], f"Invalid emoji choice! Please choose from: {', '.join(allowed_emojis)}")

def remove_user_emoji(user_id):
    """Remove the user's custom emoji, reverting to the default."""
    if user_id in registered_users:
        registered_users[user_id]["emoji"] = default_emoji
        send_message(registered_users[user_id]["chat_id"], f"Your emoji has been removed. Default emoji set to: {default_emoji}")

def broadcast_message(text):
    """Send a message to all registered users."""
    for user in registered_users.values():
        send_message(user['chat_id'], text)

def set_group_link(new_link):
    """Set the group link for the owner."""
    global group_link
    group_link = new_link
    send_message(owner_id, f"Group link updated to: {group_link}")

def handle_new_member(chat_id, username):
    """Send a welcome message to new group members."""
    welcome_message = f"Welcome {username}! Glad to have you here. Enjoy your stay! Please remember to register using /register."
    send_message(chat_id, welcome_message)

def main():
    global last_update_id

    while True:
        updates = get_new_messages()
        
        if updates and updates.get('ok'):
            for update in updates['result']:
                if 'message' in update:
                    message = update['message']
                    chat_id = message['chat']['id']
                    message_id = message['message_id']
                    user_id = message['from']['id']
                    username = message['from'].get('username', 'unknown_user')

                    if message.get('text') == '/start':
                        start_command(chat_id)

                    elif message.get('text') == '/register':
                        # Check if the user is in the group (force requirement)
                        if message['chat']['type'] == 'supergroup':
                            register_user(user_id, username, chat_id)
                        else:
                            send_message(chat_id, "You must join the group to use the bot. " + group_link)

                    elif message.get('text').startswith('/setemoji'):
                        _, emoji = message['text'].split(' ', 1)  # Extract the emoji
                        set_user_emoji(user_id, emoji)

                    elif message.get('text') == '/removeemoji':
                        remove_user_emoji(user_id)

                    elif message.get('text').startswith('/setgrouplink') and str(user_id) == owner_id:
                        _, new_link = message['text'].split(' ', 1)  # Extract the new group link
                        set_group_link(new_link)

                    elif message.get('text').startswith('/broadcast') and str(user_id) == owner_id:
                        _, broadcast_text = message['text'].split(' ', 1)
                        broadcast_message(broadcast_text)

                    if 'new_chat_members' in message:
                        for new_member in message['new_chat_members']:
                            new_user_id = new_member['id']
                            new_username = new_member.get('username', 'unknown_user')
                            handle_new_member(chat_id, new_username)

                    last_update_id = update['update_id']

        time.sleep(2)

if __name__ == "__main__":
    main()
