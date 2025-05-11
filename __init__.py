moduleInfo = {
    "meta": {
        "name": "DailyQuoteReminder",
        "version": "1.0.0",
        "description": "每日随机时间推送用户投稿的灵感语录，支持多平台消息处理",
        "author": "WSu2059",
        "license": "MIT",
        "homepage": "",
    },
    "dependencies": {
        "requires": ["RemindCore"],
        "optional": ["OneBotMessageHandler", ["NormalHandler", "CommandHandler", "BotFollowed"]],
        "pip": []
    }
}

from .Core import DailyQuoteReminder as Main