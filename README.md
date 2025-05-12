# 每日灵感语录提醒器（Daily Quote Reminder）

> 每天一句灵感语录，点亮创意火花  
> 本插件支持 Yunhu 和 OneBot 平台，可自动每日随机时间推送用户投稿的语录。

---

## 安装方法

请确保你已安装 Python（版本 ≥ 3.7）并推荐使用虚拟环境。以下是安装步骤：

### 创建虚拟环境（推荐）

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

### 安装 ErisPulse 框架

```bash
pip install erispulse
```

### 安装模块

该模块已上传至官方模块库，可通过命令行工具直接安装：

```bash
# 添加官方源
epsdk origin add https://sdkframe.anran.xyz/

# 更新模块源信息
epsdk update

# 安装本应用模块
epsdk install App-DailyQuoteReminder
```

#### 安装适配器模块

- **OneBot 平台**：安装以下模块以支持 OneBot：
  ```bash
  epsdk install OneBotAdapter OneBotMessageHandler
  ```

- **Yunhu 平台**：安装以下模块以支持 Yunhu：
  ```bash
  epsdk install YunhuNormalHandler YunhuCommandHandler YunhuBotFollowed YunhuMessageSender
  ```

---

## 启动机器人

安装完成后，运行你的主程序启动机器人服务：

```bash
python main.py
```

---

## 配置说明

本模块支持 Yunhu 和 OneBot 两个平台，需要在 env.py 文件中进行配置。这个文件是你项目根目录下的配置文件，用于设置机器人的行为。

### Yunhu 平台配置示例

```python
from ErisPulse import sdk

sdk.env.set('YunhuAdapter', {
    "Server": {
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
```

### OneBot 平台配置示例

```python
from ErisPulse import sdk

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
```

> 注意：OneBot 平台不需要设置指令 ID，只有 Yunhu 平台才需要配置这些指令 ID。

---

## 使用说明

安装并正确配置后，重启机器人服务即可生效。以下是可用指令：

| 指令 | 功能 |
|------|------|
| `/提交语录 内容` | 提交一条新语录（长度不超过 250 字） |
| `/查看所有语录` | 查看最近的投稿语录列表 |
| `/获取语录` | 获取一条随机语录 |

> 用户首次在群聊发言或关注机器人后，将自动开启每日语录提醒功能。

---

## 参考链接

- [ErisPulse 主库](https://github.com/ErisPulse/ErisPulse/)
- [ErisPulse 模块开发指南](https://github.com/ErisPulse/ErisPulse/tree/main/docs/DEVELOPMENT.md)