# Shavuha-telegram-bot

  This is the bot for ordering and payment some products with inline mode, product images, section of administration and database.
Language 'RU'

  Aiogram is the main libriary to working wiht Telegram API in this project.
To get started with this BOT you need to edit the config file (config.py), and fill in the constants API_TOKEN, PAY_TOKEN and DISK_TOKEN
  API_TOKEN, PAY_TOKEN you can take from the @BotFather in the Telegram app.
More information about start you can find here - https://core.telegram.org/bots/tutorial

#Commands
/start, /new - starting message with a 'new order' button
/my_orders - getting clients orders list
admin - enter to the section of administration. Default password: '123'
personal - authorization of a new employee, after which all orders will be sent to him by Telegram. 
The password is in the section of administration, new for each employee
