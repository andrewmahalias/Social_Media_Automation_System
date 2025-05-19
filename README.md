# InstaBot - Automated Instagram Interaction Bot
### Overview
InstaBot is an automated Instagram bot built using the instagrapi library. It can:

 - Fetch comments from a specified post and identify users who trigger predefined keywords.
 - Send direct messages (DMs) to these users.
 - Check if a user has responded with a specific command.
 - Verify if a user follows the bot’s account.
### Features
✔ Detects specific keywords in comments.

✔ Sends automatic replies to users.

✔ Checks if a user is subscribed before granting access.

✔ Provides commands for user interaction.

✔ Uses a configurable JSON file for easy customization.

### Installation
1. Clone the Repository
```bash
git clone https://github.com/yourusername/InstaBot.git  
cd InstaBot
```
2. Create a Virtual Environment (Optional but Recommended)
```bash
python3 -m venv venv  
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install Dependencies
```bash
pip install -r requirements.txt
```
4. Set Up Environment Variables
Create a ```.env``` file in the root directory and add:

```ini
INSTAGRAM_USERNAME=your_username  
INSTAGRAM_PASSWORD=your_password  
POST_URL=https://www.instagram.com/p/example/ 
```  
## Usage
### 1. Start the Bot
Run the main script:
```bash
python instabot/main.py
```
### 2. Functionality
 - The bot logs into Instagram.
 - It fetches comments from the specified post.
 - If a comment contains a trigger keyword, the bot sends a predefined message.
 - It monitors user replies and checks for a specific command.
 - The bot verifies if a user follows the account.
## Configuration
Modify ```config.json``` to change the bot's behavior:

```json
{
  "messages": {
    "greeting_message": "Hello! We noticed your comment. Reply 'Want' to continue.",
    "non_subscribed_messages": [
      "Hey! You are not subscribed yet!",
      "Please subscribe to our channel to get access to all our content.",
      "Click 'Subscribe' button to get access to all our content!"
    ],
    "subscribed_message": "Thank you you are with me! Please enter 'Watch' to get my content)",
    "await_message": "I`m still waiting for your action!"
  },
  "post_url": "https://www.instagram.com",
  "trigger_keywords": [
    "help",
    "support",
    "info"
  ],
  "commands": {
    "want": "want",
    "watch": "watch",
    "done": "done"
  }
}
```
### Parameters:

 - messages: Defines automated responses.

 - post_url: Specifies the Instagram post for monitoring.

 - trigger_keywords: List of keywords that activate bot responses.

 - commands: Predefined commands for user interaction.
## Troubleshooting
### 1. Rate Limits & Login Issues
 - If you encounter "Rate limit exceeded", wait a few minutes before retrying.
 - Ensure 2FA is disabled or use an App Password for better login reliability.
### 2. Message Retrieval Issues
 - If No active thread found appears, ensure the user has previously interacted via DM.
 - Use direct_threads() to check available conversations.
### 3. Subscription Check Not Working
 - ```is_followed_by``` might not exist. Try using user_info.following_viewer instead.
## Contributing
At this time, issues and pull requests are not accepted.

## License
This project is licensed under the MIT License.
