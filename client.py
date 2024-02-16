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
import websockets  # 用于websocket连接
import json  # 用于json格式的字符串
import logging  # 用于记录日志
import datetime  # 用于获取时间
import os  # 用于操作文件
import configparser  # 用于读取配置文件

# 导入自定义包
from modules.luck import luck  # 用于运势模块

# ========================================
# 以下是各种类，用于存储全局变量、发送消息、接收消息、配置文件、客户端
# ========================================


# 全局变量类 => 用于存储全局变量
class GlobalVariable:
    def __init__(self):
        self.logger = logging.getLogger(__name__)  # 日志记录器

    # 初始化日志记录器
    def init_logger(self):
        self.logger.setLevel(logging.INFO)
        if not os.path.exists("logs"):
            os.makedirs("logs")
        handler = logging.FileHandler(
            "logs/" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".log",
            encoding="UTF-8",
        )
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)


# 发送消息类（群聊消息、私聊消息） => 返回json格式的字符串，用于发送消息
class SendMessage:
    # 发送 => 判断在客户端那边，这里拆开两个函数
    # 发送私聊消息
    def private_message(message, user_id):
        message_type = "private"
        message = message
        user_id = user_id

        return json.dumps(
            {
                "action": "send_private_msg",
                "params": {"user_id": user_id, "message": message},
            }
        )

    # 发送群聊消息
    def group_message(message, group_id):
        message_type = "group"
        message = message
        group_id = group_id

        return json.dumps(
            {
                "action": "send_group_msg",
                "params": {"group_id": group_id, "message": message},
            }
        )


# 接收消息类（群聊消息、私聊消息） => 用于接收消息
class RecvMessage:
    # 发送者类
    class Sender:
        # 初始化Sender类（后三个变量为选填）
        def __init__(self, user_id, nickname, sex, age, card="", role="", title=""):
            # 通用属性
            self.user_id = user_id
            self.nickname = nickname
            self.sex = sex
            self.age = age
            # 群聊特有
            self.card = card
            self.role = role
            self.title = title

    # 消息类初始化
    # 解析私聊消息
    def private_message(self, time, message_id, user_id, message, raw_message, sender):
        self.time = time
        self.message_id = message_id
        self.user_id = user_id
        self.message = message
        self.raw_message = raw_message
        self.sender = self.Sender(
            sender["user_id"], sender["nickname"], sender["sex"], sender["age"]
        )

    # 解析群聊消息
    def group_message(
        self,
        time,
        message_id,
        sub_type,
        group_id,
        user_id,
        message,
        raw_message,
        sender,
    ):
        self.time = time
        self.message_id = message_id
        self.sub_type = sub_type
        self.group_id = group_id
        self.user_id = user_id
        self.message = message
        self.raw_message = raw_message
        self.sender = self.Sender(
            sender["user_id"], sender["nickname"], sender["sex"], sender["age"]
        )

    # TODO: 待续


# 客户端类 => 用于连接服务器、发送消息、接收消息
class Client:
    def __init__(
        self,
        ws_ip,
        ws_port,
        global_variable,
        input_queue,
        output_queue,
        ws_access_token="",
    ):
        self.ws_ip = ws_ip
        self.ws_port = ws_port
        self.ws_access_token = ws_access_token
        self.ws = None
        self.ws_url = (
            "ws://"
            + self.ws_ip
            + ":"
            + str(self.ws_port)
            + "/?access_token="
            + self.ws_access_token
        )

        self.global_variable = global_variable
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.recv_message = RecvMessage()

    # 建立连接
    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        return self.ws

    # 发送消息
    async def send(self, message_type, target, message):
        if message_type == "private":
            await self.ws.send(SendMessage.private_message(message, target))
        elif message_type == "group":
            await self.ws.send(SendMessage.group_message(message, target))
        else:
            return 0

    # 接收消息
    async def recv(self):
        # 接收消息
        recv_text = await self.ws.recv()
        recv_json = json.loads(recv_text)

        # 检查消息类型
        if recv_json.get("post_type") == None:
            return 0

        # self.output_queue.put("log:info:" + recv_text)

        # 处理聊天信息，加入消息列表
        if recv_json["post_type"] == "message":
            if recv_json["message_type"] == "private":
                self.recv_message.private_message(
                    recv_json["time"],
                    recv_json["message_id"],
                    recv_json["user_id"],
                    recv_json["message"],
                    recv_json["raw_message"],
                    recv_json["sender"],
                )
            elif recv_json["message_type"] == "group":
                self.recv_message.group_message(
                    recv_json["time"],
                    recv_json["message_id"],
                    recv_json["sub_type"],
                    recv_json["group_id"],
                    recv_json["user_id"],
                    recv_json["message"],
                    recv_json["raw_message"],
                    recv_json["sender"],
                )
                await self.group_message_handler()

    # TODO: 关闭连接
    async def close(self):
        await self.ws.close()
        return 0

    # 等待接收消息
    async def wait_input(self):
        while True:
            # 获取消息
            message = self.input_queue.get()
            self.output_queue.put(message)

            commands = message.split(" ")

            # 判断是否是指令
            if commands[0] == "send":
                # 发送消息到群聊/私聊
                message_type = commands[1]
                target = int(commands[2])
                msg = commands[3]
                await self.send(message_type, target, msg)

            self.global_variable.logger.info("终端输入指令：" + message)
            self.output_queue.put("log:info:终端输入指令：" + message)

    # 处理群聊消息
    async def group_message_handler(self):
        # 提取消息
        group_id = self.recv_message.group_id
        raw_message = self.recv_message.raw_message
        user_id = self.recv_message.user_id
        nickname = (
            self.recv_message.sender.nickname
            if self.recv_message.sender.card == ""
            else self.recv_message.sender.card
        )

        # 查找群聊
        config = configparser.ConfigParser()
        config.read("config.ini")
        group_list = config.items("group")
        group_name = ""
        for group in group_list:
            group_info = json.loads(group[1])
            if group_info["group_id"] == group_id:
                group_name = group_info["group_name"]

        # 判断是否是机器人
        if user_id == config.getint("bot", "id"):
            return 0

        # 发送到消息队列
        self.output_queue.put(f"msg:来自群{group_name}的{nickname}说：{raw_message}")
        self.global_variable.logger.info(
            f"来自群{group_name}的{nickname}说：{raw_message}"
        )

        # 如果以.开头
        if raw_message.startswith("."):
            commands = raw_message.split(" ")
            if commands[0] == ".今日运势":
                # 实例化运势模块
                luck_module = luck(self.recv_message)
                # 获取运势
                message = luck_module.dump()
                # 发送消息
                await self.send("group", group_id, message)

                # 记录日志
                self.global_variable.logger.info(
                    f"群聊{group_id}的{user_id}请求了今日运势"
                )
                self.output_queue.put(
                    f"log:info:群聊{group_name}的{nickname}请求了今日运势"
                )

    # TODO: 处理私聊消息
    async def private_message_handler(self):
        return 0
