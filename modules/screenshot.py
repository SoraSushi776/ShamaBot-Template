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
        return 0
