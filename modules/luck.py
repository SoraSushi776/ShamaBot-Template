# coding: utf-8
# author: SoraSushi776
# github: https://www.github.com/SoraSushi776
# repository: https://www.github.com/SoraSushi776/Shama-Bot
# description: 一个简单的QQ机器人客户端
# init date: 2024年02月14日

# ========================================
# 以下是导入包
# ========================================

# 导入pip包
import random


# 主类
class luck:
    def __init__(self, recv_message):
        self.recv_message = recv_message
        self.raw_message = recv_message.raw_message
        self.group_id = recv_message.group_id
        self.user_id = recv_message.user_id
        self.nickname = (
            recv_message.sender.nickname
            if recv_message.sender.card == ""
            else recv_message.sender.card
        )

    def dump(self):
        # 幸运值
        luck = random.randint(0, 100)

        # 返回消息
        message = f"[CQ:at,qq={self.user_id}] 你的幸运值是：{luck}%"

        if luck == 100:
            message += "\n恭喜你，今天是你的幸运日！"
        elif luck >= 90:
            message += "\n你今天的运气真好！"
        elif luck >= 80:
            message += "\n你今天的运气不错！"
        elif luck >= 70:
            message += "\n你今天的运气还行！"
        elif luck >= 60:
            message += "\n你今天的运气一般！"
        elif luck >= 50:
            message += "\n你今天的运气不太好！"
        elif luck >= 40:
            message += "\n你今天的运气不好！"
        elif luck >= 30:
            message += "\n你今天的运气很差！"
        elif luck >= 20:
            message += "\n你今天的运气真差！"
        elif luck >= 10:
            message += "\n你今天的运气非常差！"
        elif luck >= 1:
            message += "\n你今天的运气糟糕透了！"
        elif luck == 0:
            message += "\n是的...0%的概率也是有的..."

        return message
