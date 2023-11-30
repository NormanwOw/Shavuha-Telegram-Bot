# Shavuha Telegram-Bot
![](https://img.shields.io/badge/Python-v3.9-green) ![](https://img.shields.io/badge/Aiogram-v2.25.1-blue) ![](https://img.shields.io/badge/SQLite-v3-white)

Actual version of this bot running here - [@za_uglom_bot](https://t.me/za_uglom_bot)

## About
This is the bot for ordering and payment some products with inline mode, product images, section of administration and database.
* Language **'RU'**

**Aiogram** is the main libriary for working with Telegram API in this project.

## Install
To get started with this BOT you should to edit constants `API_TOKEN` and `PAY_TOKEN` in the config file `config.py`.
* `API_TOKEN` and `PAY_TOKEN` you can get from the [@BotFather](https://t.me/BotFather) in the Telegram application.  
More information about this you can find [here](https://core.telegram.org/bots/tutorial)  

then

* `pip install -r requirements.txt`
* `python main.py`

## Commands
* `/start`, `/new` - starting message with a 'new order' button
* `/my_orders` - getting clients orders list
* `/error` - send message to developers about some problems
* `admin` - enter to the section of administration. Default password: '123'
* `personal` - authorization of a new employee. After this authorization all orders will be sent to emloyee by Telegram. *The password is in the administration panel, new for each employee*
  
____
![shava-1@0,75x](https://github.com/NormanwOw/Shavuha-telegram-bot/assets/118648914/df5b987e-879c-4155-b78d-97910855c5bf)
![shava-2@0,75x](https://github.com/NormanwOw/Shavuha-telegram-bot/assets/118648914/5372081a-6a5b-46fd-9293-12f3ba6eee31)
![shava-3@0,75x](https://github.com/NormanwOw/Shavuha-telegram-bot/assets/118648914/480a7480-03c8-4c04-88cd-be3ad71b79a3)
![shava-4@0,75x](https://github.com/NormanwOw/Shavuha-telegram-bot/assets/118648914/97ef51ee-58e3-46b8-9688-31467c615bff)
![shava-5@0,75x](https://github.com/NormanwOw/Shavuha-telegram-bot/assets/118648914/f1cf2914-b0e4-49fb-8428-a3348447417e)



