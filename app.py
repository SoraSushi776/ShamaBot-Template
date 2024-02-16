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
import threading
import asyncio
import queue
import configparser

# 导入自定义包
import client
import console
import logging

# ========================================
# 以下是全局变量
# ========================================

# 创建一个队列，用于存储终端的输入
input_queue = queue.Queue()

# 创建一个队列，用于存储终端的输出
output_queue = queue.Queue()

# 实例化一个终端
window = console.MainWindow("Shama Bot", "800x400", input_queue, output_queue)


# 读取配置文件
try:
    config = configparser.ConfigParser()
    config.read("config.ini")

    ws_ip = config.get("websocket", "ip")
    ws_port = config.get("websocket", "port")
except Exception as e:
    config['websocket'] = {'ip': 'localhost', 'port': '8080'}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    ws_ip = "localhost"
    ws_port = "8080"

# 实例化一个全局变量
global_variable = client.GlobalVariable()

# 实例化一个客户端
app = client.Client(ws_ip,ws_port,global_variable,input_queue,output_queue)

# ========================================
# 以下是函数
# ========================================

# 客户端主程序
async def app_main():
    try:
        # 与服务器建立连接        
        # 建立永久连接，等待服务器推送消息
        await app.connect()

        global_variable.logger.info("成功连接到Websocket")

        # 接收消息 => 执行相应功能
        while True:
            # 接收机器人QQ消息
            status = await app.recv()
            if status == 1:
                await app.send("group", 563867774, "你好")
        
    except Exception as e:
        # 记录错误日志
        global_variable.logger.error(e)
        # 发送错误消息
        output_queue.put("log:error:" + str(e))

# 启动客户端
def run_app_main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(app_main())
    global_variable.logger.info("客户端已启动")

# 启动客户端等待输入
def run_app_wait():
    app.wait_input()

# 启动终端
def run_console_main():
    # 初始化终端
    window.init_main_window()
    window.update_resource_usage()
    window.run()
    global_variable.logger.info("终端已启动")

# 启动终端等待输入
def run_console_wait():
    window.wait_input()

# ========================================
# 以下是主程序
# ========================================
if __name__ == "__main__":
    # 初始化日志
    global_variable.init_logger()

    # 启动线程
    # 创建一个线程，用于终端的输入
    console_thread_wait = threading.Thread(target=run_console_wait,daemon=True)
    console_thread_wait.start()


    # 创建一个线程，用于启动客户端
    client_thread = threading.Thread(target=run_app_main,daemon=True)
    client_thread.start()

    # 创建一个线程，用于客户端的输入
    client_thread_wait = threading.Thread(target=run_app_wait,daemon=True)
    client_thread_wait.start()

    run_console_main()
