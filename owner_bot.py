import requests
import time
from config import owner_bot_token, owner_id  # Import owner bot token and owner ID

# Telegram API URL
get_updates_url = f'https://api.telegram.org/bot{owner_bot_token}/getUpdates'
send_message_url = f'https://api.telegram.org/bot{owner_bot_token}/sendMessage'

def get_updates(offset=None):
    """Fetch new updates from the owner bot."""
    params = {'timeout': 100}
    if offset:
        params['offset'] = offset

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

def handle_commands(update):
    """Handle incoming commands from the owner."""
    message = update['message']
    chat_id = message['chat']['id']
    
    if 'text' in message:
        command = message['text'].strip()
        
        if command.startswith('/broadcast'):
            _, broadcast_text = command.split(' ', 1)
            # Broadcast a message to all users of the main bot
            send_message(chat_id, f"Broadcasting message: {broadcast_text}")
            # Implement broadcasting logic here
            
        elif command.startswith('/setgrouplink'):
            _, new_link = command.split(' ', 1)
            # Store the new group link in the main bot or configuration
            send_message(chat_id, f"Group link updated to: {new_link}")

def main():
    last_update_id = None

    while True:
        updates = get_updates(last_update_id)
        if updates and updates.get('ok'):
            for update in updates['result']:
                if 'message' in update:
                    last_update_id = update['update_id']
                    handle_commands(update)
        time.sleep(2)

if __name__ == "__main__":
    main()
