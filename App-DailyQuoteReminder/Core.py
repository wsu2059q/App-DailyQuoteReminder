from datetime import datetime
from .DFA.dfa import DFA
import random
import asyncio

class DailyQuoteReminder:
    def __init__(self, sdk):
        self.sdk = sdk
        self.logger = sdk.logger
        self.env = sdk.env
        self.dfa = DFA()
        
        if hasattr(self.sdk, "RemindCore"):
            def dailyquote_time():
                return datetime.now().strftime('%H:%M')
            
            def dailyquote_content(self):
                custom_quotes = self.env.get("dailyquote_custom_messages", [])
                if not custom_quotes:
                    return "每天一句，点亮灵感之光～"
                return random.choice(custom_quotes)

            self.sdk.RemindCore.AddPlaceholder("dailyquote_time", dailyquote_time)
            self.sdk.RemindCore.AddPlaceholder("dailyquote_content", dailyquote_content)
            self.logger.info("成功注册 RemindCore 提醒器")
        else:
            self.logger.warning("未找到 RemindCore 模块")
            raise RuntimeError("未找到 RemindCore 模块，而每日语录提醒器依赖其运行")

        # 注册消息处理器
        if hasattr(sdk, "YunhuNormalHandler"):
            sdk.YunhuNormalHandler.AddHandle(self.handle_yunhu_message)
            self.logger.info("成功注册 Yunhu 消息处理器")
        if hasattr(sdk, "YunhuCommandHandler"):
            sdk.YunhuCommandHandler.AddHandle(self.handle_yunhu_command, "1432") # /提交语录 指令id
            sdk.YunhuCommandHandler.AddHandle(self.handle_yunhu_command, "1433") # /查看所有语录 指令id
            sdk.YunhuCommandHandler.AddHandle(self.handle_yunhu_command, "1435") # /获取语录 指令id
            # 如果您需要应用到您自己的机器人中，请修改上处的指令id（1432 1433 1435）为您机器人的指令id
            # 这里除了提交语录指令，其它都是直发指令 ， 提交语录是普通命令

            self.logger.info("成功注册 Yunhu 指令处理器")
        if hasattr(sdk, "YunhuBotFollowed"):
            sdk.YunhuBotFollowed.AddHandle(self.handle_bot_followed)
            self.logger.info("成功注册 YunhuBotFollowed 事件处理器")
        if hasattr(sdk, "OneBotMessageHandler"):
            sdk.OneBotMessageHandler.AddHandle(self.handle_onebot_message)
            self.logger.info("成功注册 OneBot 消息处理器")

        self.logger.info("每日灵感语录模块已加载")
    
    async def handle_yunhu_message(self, data):
        try:
            event = data.get("event", {})
            chat = event.get("chat", {})
            chat_type = chat.get("chatType")
            target_id = None

            if chat_type == "bot":
                sender = event.get("sender", {})
                target_id = sender.get("senderId")
                chat_type = "user"
            elif chat_type == "group":
                target_id = chat.get("chatId")
            elif chat_type == "user":
                target_id = chat.get("userId")

            self.logger.debug(f"收到 Yunhu 消息: {chat_type}({target_id})")
            if target_id:
                await self.register_reminder(target_id, chat_type, platform="ALL")

        except Exception as e:
            self.logger.error(f"处理 Yunhu 消息失败: {e}")

    async def handle_bot_followed(self, data):
        try:
            event = data.get("event", {})
            chat = event.get("chat", {})
            chat_type = chat.get("chatType")
            user_id = event.get("userId")
            nickname = event.get("nickname", "匿名用户")

            self.logger.debug(f"注册每日灵感提醒: {chat_type}(user_id={user_id}), 用户名={nickname}")

            if user_id:
                await self.register_reminder(target_id=user_id, chat_type="user", platform="ALL")
        except Exception as e:
            self.logger.error(f"注册每日灵感提醒失败: {e}")

    async def handle_yunhu_command(self, data):
        try:
            event = data.get("event", {})
            message = event.get("message", {})
            chat = event.get("chat", {})
            sender = event.get("sender", {})

            command_name = message.get("commandName")
            sender_id = sender.get("senderId")
            sender_nickname = sender.get("senderNickname", "匿名用户")
            chat_type = chat.get("chatType")
            content = message.get("content", {}).get("text", "").strip()

            self.logger.debug(f"收到指令: {command_name}, 内容: {content}, 用户: {sender_id}")

            custom_quotes = self.env.get("dailyquote_custom_messages", [])
            
            if command_name == "提交语录":
                if not content:
                    reply_html = """
                    <div style="font-family: Arial, sans-serif; padding: 10px; border-radius: 8px; background-color: #f9f9f9;">
                        <p>请在指令后输入你要提交的语录，例如：</p>
                        <code style="background:#eee;padding:4px;border-radius:4px;">/提交语录 每天一句，点亮灵感</code>
                    </div>
                    """
                elif self.dfa.exists(content):
                    reply_html = """
                    <div style="font-family: Arial, sans-serif; padding: 10px; border-radius: 8px; background-color: #fffbe6; border-left: 4px solid #faad14;">
                        <p>提交的语录包含敏感词，请重新提交！</p>
                    </div>
                    """
                elif len(content) > 250:
                    current_length = len(content)
                    reply_html = f"""
                    <div style="font-family: Arial, sans-serif; padding: 10px; border-radius: 8px; background-color: #fffbe6; border-left: 4px solid #faad14;">
                        <p>提交的语录内容过长（当前{current_length}字），请保持在250字以内～</p>
                    </div>
                    """
                else:
                    record = {
                        "content": content,
                        "sender_id": sender_id,
                        "sender_nickname": sender_nickname,
                        "timestamp": datetime.now().isoformat()
                    }
                    if any(item["content"] == content for item in custom_quotes):
                        reply_html = """
                        <div style="font-family: Arial, sans-serif; padding: 10px; border-radius: 8px; background-color: #fffbe6; border-left: 4px solid #faad14;">
                            <p>这条语录已经存在啦～换句更有意思的吧！</p>
                        </div>
                        """
                    else:
                        custom_quotes.append(record)
                        self.env.set("dailyquote_custom_messages", custom_quotes)
                        reply_html = f"""
                        <div style="font-family: Arial, sans-serif; padding: 10px; border-radius: 8px; background-color: #f6ffed; border-left: 4px solid #52c41a;">
                            <h3>成功收录新语录：</h3>
                            <p>{content}</p>
                            <p>感谢贡献！✨</p>
                        </div>
                        """
            elif command_name == "查看所有语录":
                if not custom_quotes:
                    reply_html = """
                    <div style="font-family: Arial, sans-serif; padding: 10px; border-radius: 8px; background-color: #f9f9f9;">
                        <p>目前还没有人投稿语录呢，快来第一条！</p>
                    </div>
                    """
                else:
                    recent_quotes = custom_quotes[-25:][::-1]
                    
                    lines = []
                    for i, msg in enumerate(recent_quotes):
                        time_str = datetime.fromisoformat(msg["timestamp"]).strftime("%Y-%m-%d %H:%M")
                        item_html = f"""
                            <div style="background: #fff; padding: 12px; border-left: 4px solid #4096ff; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                                <span style='color:#888;font-size:12px;'>{time_str}</span>
                                <strong style='color:#333;margin-left: 8px;'>{msg['sender_nickname']}</strong>
                                <p style='margin-top: 6px;color: #222;'>{msg['content']}</p>
                            </div>
                        """
                        if i < 5:
                            lines.append(item_html)
                        else:
                            if i == 5:
                                fold_content = ""
                            fold_content += item_html

                    if 'fold_content' in locals():
                        fold_block = f"""
                            <details style="margin-top: 10px;">
                                <summary style="cursor: pointer; color: #4096ff; font-weight: bold;">展开更多语录（共 {len(recent_quotes) - 5} 条）</summary>
                                <div style="margin-top: 10px;">
                                    {fold_content}
                                    <div style="text-align:center; margin-top: 10px; color: #888;">
                                        长度受限
                                    </div>
                                </div>
                            </details>
                        """
                    else:
                        fold_block = ""

                    message_items = "".join(lines)
                    reply_html = f"""
                    <div style="font-family: 'Segoe UI', Arial, sans-serif; padding: 15px; border-radius: 10px; background-color: #f9f9f9; max-width: 600px; margin: auto;">
                        <h3 style="color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px;">【当前语录库】</h3>
                        <div style="display: flex; flex-direction: column; gap: 12px;">
                            {message_items}
                            {fold_block}
                        </div>
                    </div>
                    """
            elif command_name == "获取语录":
                custom_quotes = self.env.get("dailyquote_custom_messages", [])
                if not custom_quotes:
                    reply_html = """
                    <div style="font-family: Arial, sans-serif; padding: 10px; border-radius: 8px; background-color: #f9f9f9;">
                        <p>目前还没有人投稿语录呢，快来第一条！</p>
                    </div>
                    """
                else:
                    quote = random.choice(custom_quotes)
                    time_str = datetime.fromisoformat(quote["timestamp"]).strftime("%Y-%m-%d %H:%M")
                    reply_html = f"""
                    <div style="font-family: 'Segoe UI', Arial, sans-serif; padding: 15px; border-radius: 10px; background-color: #f6ffed; max-width: 600px; margin: auto;">
                        <blockquote style="margin: 10px 0; font-size: 1.1em; color: #222; border-left: 4px solid #52c41a; padding-left: 12px;">
                            {quote['content']}
                        </blockquote>
                        <p style="color: #888; font-size: 0.9em;">—— {quote['sender_nickname']} · {time_str}</p>
                    </div>
                    """
            
            chat_type_for_send = "user"
            if chat_type == "bot":
                target_id = sender_id
            elif chat_type == "group":
                chat_type_for_send = "group"
                target_id = chat.get("chatId")
            else:
                target_id = chat.get("userId")

            await self.sdk.YunhuMessageSender.Html(recvId=target_id, recvType=chat_type_for_send, content=reply_html)
            self.logger.info(f"[Yunhu] 已发送指令回复到 {chat_type_for_send}({target_id})")

        except Exception as e:
            self.logger.error(f"处理 Yunhu 指令失败: {e}")

    async def handle_onebot_command(self, content: str, sender_id: str, sender_nickname: str):
        custom_quotes = self.env.get("dailyquote_custom_messages", [])

        if content.startswith("/提交语录"):
            msg_text = content[len("/提交语录"):].strip()
            if not msg_text:
                return "请在指令后输入你要提交的语录，例如：\n/提交语录 每天一句，点亮灵感"
            elif len(msg_text) > 250:
                return f"提交的语录内容过长（当前{len(msg_text)}字），请保持在250字以内～"

            record = {
                "content": msg_text,
                "sender_id": sender_id,
                "sender_nickname": sender_nickname,
                "timestamp": datetime.now().isoformat()
            }
            if any(item["content"] == msg_text for item in custom_quotes):
                return "这条语录已经存在啦～换句更有意思的吧！"
            else:
                custom_quotes.append(record)
                self.env.set("dailyquote_custom_messages", custom_quotes)
                return f"成功收录新语录：\n{msg_text}\n感谢贡献！✨"

        elif content == "/查看所有语录":
            if not custom_quotes:
                return "目前还没有人投稿语录呢，快来第一条！"
            
            recent_quotes = custom_quotes[-10:][::-1]
            
            lines = []
            for i, msg in enumerate(recent_quotes):
                time_str = datetime.fromisoformat(msg["timestamp"]).strftime("%Y-%m-%d %H:%M")
                line = f"{i+1}. [{time_str}] {msg['sender_nickname']}：{msg['content']}"
                lines.append(line)
            
            return "【当前语录库】\n" + "\n".join(lines)
        
        elif content == "/获取语录":
            if not custom_quotes:
                return "目前还没有人投稿语录呢，快来第一条！"
            quote = random.choice(custom_quotes)
            time_str = datetime.fromisoformat(quote["timestamp"]).strftime("%Y-%m-%d %H:%M")
            return f"{quote['content']}\n—— {quote['sender_nickname']} · {time_str}"
    async def handle_onebot_message(self, data):
        try:
            message_type = data.get("message_type", "private")
            user_id = data.get("user_id")
            group_id = data.get("group_id")
            chat_type = "user" if message_type == "private" else "group"
            content = data.get("raw_message", "").strip()

            self.logger.debug(f"收到 OneBot 消息: {chat_type}({user_id or group_id}), 内容: {content}")

            if content.startswith("/"):
                nickname = data.get("sender", {}).get("nickname", "匿名用户")
                reply = await self.handle_onebot_command(
                    content=content,
                    sender_id=str(user_id),
                    sender_nickname=nickname
                )
                if reply:
                    params = {"user_id": user_id, "message": reply}
                    await self.sdk.OneBotAdapter.send_action("send_private_msg", params)
                    self.logger.info(f"[OneBot] 已发送回复给用户 {user_id}")

            target_id = user_id if message_type == "private" else group_id
            await self.register_reminder(target_id, chat_type, platform="onebot")

        except Exception as e:
            self.logger.error(f"处理 OneBot 消息失败: {e}")

    async def register_reminder(self, target_id, chat_type, platform="ALL"):
        now = datetime.now().isoformat()
        is_first_time = False

        # 如果未注册过，则注册提醒任务
        if not self.env.get(f"dailyquote_registered_{target_id}", False):
            is_first_time = True
            self.env.set(f"dailyquote_registered_{target_id}", True)

            # 注册每日随机提醒（使用 RemindCore）
            self.sdk.RemindCore.AddRandomRemind(
                target_id=target_id,
                chat_type=chat_type,
                messages=["{dailyquote_time}：\n{dailyquote_content}\n✨"],
                interval=(9, 21),
                platform=platform
            )
        if is_first_time:
            asyncio.create_task(self.send_welcome_message(target_id, chat_type, platform))

    async def send_welcome_message(self, target_id, target_type, platform="ALL"):
        message = (
            "【每日一言提醒服务已激活】\n"
            "每天我会随机时间为你推送一句来自大家的语录，\n"
            "帮助你放松心情，激发创意！\n\n"
            "【使用指南】\n"
            "你可以随时取消订阅，也可以投稿自己的语录，\n"
            "让更多人看到你的智慧火花！✨\n"
            "另外：群聊内超过三天没互动的话，我会自动安静闭嘴哒，放心不会刷屏！"
        )
        try:
            if platform == "onebot" and hasattr(self.sdk, "OneBotAdapter") and target_type in ["user", "group"]:
                action = "send_private_msg" if target_type == "user" else "send_group_msg"
                params = {"user_id" if target_type == "user" else "group_id": target_id, "message": message}
                await self.sdk.OneBotAdapter.send_action(action, params)
                self.logger.info(f"[OneBot] 已发送欢迎语到 {target_type}({target_id})")
            elif hasattr(self.sdk, "YunhuMessageSender"):
                await self.sdk.YunhuMessageSender.Text(recvId=target_id, recvType=target_type, content=message)
                self.logger.info(f"[Yunhu] 已发送欢迎语到 {target_type}({target_id})")
            else:
                self.logger.warning("未找到任何可用的消息发送模块")
        except Exception as e:
            self.logger.error(f"发送欢迎语失败: {e}")