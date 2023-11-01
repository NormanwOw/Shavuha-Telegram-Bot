# Shavuha-telegram-bot
![](https://img.shields.io/badge/Python-v3.9-green) ![](https://img.shields.io/badge/Aiogram-v2.25.1-blue) ![](https://img.shields.io/badge/SQLite-v3-white)

Actual version of this bot running here - [@za_uglom_bot](https://t.me/za_uglom_bot)

## About
  This is the bot for ordering and payment some products with inline mode, product images, section of administration and database.
* Language **'RU'**

Aiogram is the main libriary to working wiht Telegram API in this project.

## Install
To get started with this BOT you need to edit the config file `config.py` and edit the constants `API_TOKEN`, `PAY_TOKEN` and `DISK_TOKEN`
* `API_TOKEN` and `PAY_TOKEN` you can get from the [@BotFather](https://t.me/BotFather) in the Telegram application.  
More information about this you can find [here](https://core.telegram.org/bots/tutorial)

## Commands
* `/start`, `/new` - starting message with a 'new order' button
* `/my_orders` - getting clients orders list
* `/error` - send message to developers about some problems
* `admin` - enter to the section of administration. Default password: '123'
* `personal` - authorization of a new employee. After this authorization all orders will be sent to emloyee by Telegram. *The password is in the administration panel, new for each employee*
