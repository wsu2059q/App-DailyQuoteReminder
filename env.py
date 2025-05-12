from ErisPulse import sdk


sdk.env.set('YunhuAdapter',{
    "Server":{
        "host": "0.0.0.0",
        "port": 11452,
        "path": "/"
    },
    "token": ""
})

sdk.env.set("DailyQuoteReminderConfig", {
    "SubmitCommandId": "1432",   # /提交语录 的指令 ID
    "ListCommandId": "1433",     # /查看所有语录 的指令 ID
    "GetCommandId": "1435"       # /获取语录 的指令 ID
})

sdk.env.set("OneBotAdapter", {
    "mode": "connect",  # 可选 connect 或 server
    "WSServer": {
        "host": "127.0.0.1",
        "port": 8080,
        "path": "/",
        "token": ""
    },
    "WSConnect": {
        "url": "ws://127.0.0.1:3001/",
        "token": ""
    }
})