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
import tkinter as tk
import psutil
import datetime
import configparser

# ========================================
# 以下是类
# ========================================


# 主窗口类
class MainWindow:
    # 初始化
    def __init__(self, title, geometry, input_queue, output_queue):
        # 设置窗口
        self.window = tk.Tk()
        self.window.title(title)
        self.window.geometry(geometry)

        # 初始化一些变量
        self.last_bytes_sent = 0
        self.last_bytes_recv = 0
        self.command_list = []
        self.temp_command = ""
        self.command_index = 0

        self.input_queue = input_queue
        self.output_queue = output_queue

        # TODO: 设置窗口图标

        # 设置窗口大小限制
        self.window.minsize(800, 400)

    # 初始化主窗口
    def init_main_window(self):
        # 左边的主Frame
        self.frame_left = tk.Frame(self.window, borderwidth=0, relief="groove")
        self.frame_left.grid(row=0, column=0, sticky="nsew")

        # 右边的主Frame
        self.frame_right = tk.Frame(self.window, borderwidth=0, relief="groove")
        self.frame_right.grid(row=0, column=1, sticky="nsew")

        # 左上角（占用情况显示）
        self.frame_left_top = tk.LabelFrame(
            self.frame_left,
            text="资源占用",
            borderwidth=2,
            relief="groove",
            width=200,
            height=100,
        )
        self.frame_left_top.pack(
            side="top", expand=False, fill="both", padx=10, pady=10
        )
        #  显示CPU、内存、网速情况
        self.cpu_label = tk.Label(
            self.frame_left_top, text="CPU: 0%", width=10, height=1, pady=10
        )
        self.cpu_label.pack(side="left", expand=True, fill="both")
        self.memory_label = tk.Label(
            self.frame_left_top, text="内存: 0%", width=10, height=1
        )
        self.memory_label.pack(side="left", expand=True, fill="both")
        self.network_label = tk.Label(
            self.frame_left_top, text="网速: 0KB/s", width=10, height=1
        )
        self.network_label.pack(side="left", expand=True, fill="both")

        # 左下角（群聊消息显示）
        self.frame_left_bottom = tk.LabelFrame(
            self.frame_left,
            text="QQ消息",
            borderwidth=2,
            relief="groove",
            width=200,
            height=200,
        )
        self.frame_left_bottom.pack(
            side="bottom", expand=True, fill="both", padx=10, pady=10
        )
        # 添加滚动条和消息显示框
        self.msg_scrollbar = tk.Scrollbar(self.frame_left_bottom)
        self.msg_scrollbar.pack(side="right", fill="y")
        self.msg_text = tk.Text(
            self.frame_left_bottom,
            yscrollcommand=self.msg_scrollbar.set,
            width=1,
            height=1,
            state="disabled",
        )
        self.msg_text.pack(side="left", expand=True, fill="both")
        self.msg_scrollbar.config(command=self.msg_text.yview)

        # 右上角（机器人指令输出显示）
        self.frame_right_top = tk.LabelFrame(
            self.frame_right,
            text="机器人日志",
            borderwidth=2,
            relief="groove",
            width=200,
            height=200,
        )
        self.frame_right_top.pack(
            side="top", expand=True, fill="both", padx=10, pady=10
        )
        # 添加滚动条和消息显示框
        self.log_scrollbar = tk.Scrollbar(self.frame_right_top)
        self.log_scrollbar.pack(side="right", fill="y")
        self.log_text = tk.Text(
            self.frame_right_top,
            yscrollcommand=self.log_scrollbar.set,
            width=1,
            height=1,
            state="disabled",
        )
        self.log_text.pack(side="left", expand=True, fill="both")
        self.log_scrollbar.config(command=self.log_text.yview)

        # 右下角（机器人指令输入）
        self.frame_right_bottom = tk.LabelFrame(
            self.frame_right,
            text="发送指令",
            borderwidth=2,
            relief="groove",
            width=200,
            height=50,
        )
        self.frame_right_bottom.pack(
            side="bottom", expand=False, fill="both", padx=10, pady=10
        )
        # 添加输入框和发送按钮
        self.input_text = tk.Entry(self.frame_right_bottom)
        self.input_text.pack(side="left", expand=True, fill="both")
        # 绑定回车键
        self.input_text.bind("<Return>", self.send_message)
        # 绑定上下键
        self.input_text.bind("<Up>", self.previous_command)
        self.input_text.bind("<Down>", self.next_command)
        self.send_button = tk.Button(
            self.frame_right_bottom, text="发送", command=self.send_message
        )
        self.send_button.pack(side="right", expand=False, fill="both")

        # 配置行和列的权重
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

    # 更新资源占用情况
    def update_resource_usage(self):
        # 获取资源占用情况
        cpu_usage = psutil.cpu_percent(interval=None)
        memory_usage = psutil.virtual_memory().percent

        # 获取当前发送和接收的字节数
        current_bytes_sent = psutil.net_io_counters().bytes_sent
        current_bytes_recv = psutil.net_io_counters().bytes_recv

        # 计算网速
        network_speed = (
            current_bytes_sent
            - self.last_bytes_sent
            + current_bytes_recv
            - self.last_bytes_recv
        ) / 1024

        # 更新发送和接收的字节数
        self.last_bytes_sent = current_bytes_sent
        self.last_bytes_recv = current_bytes_recv

        # 更新资源占用情况
        self.cpu_label.config(text="CPU: " + str(cpu_usage) + "%")
        self.memory_label.config(text="内存: " + str(memory_usage) + "%")
        # 根据网速大小显示不同的单位
        if network_speed > 1024 * 1024:
            self.network_label.config(text="网速: 0KB/s")
        elif network_speed > 1024:
            self.network_label.config(
                text="网速: " + str(int((network_speed) / 1024)) + "MB/s"
            )
        else:
            self.network_label.config(text="网速: " + str(int(network_speed)) + "KB/s")

        # 循环调用
        self.window.after(1000, self.update_resource_usage)

    # 向消息框中添加消息
    def add_message(self, to, message):
        if to == "msg":
            self.msg_text.config(state="normal")
            self.msg_text.insert("end", message + "\n")
            self.msg_text.config(state="disabled")
        elif to == "log":
            self.log_text.config(state="normal")
            self.log_text.insert("end", message + "\n")
            self.log_text.config(state="disabled")

    # 发送消息
    def send_message(self, event=None):
        message = self.input_text.get()
        if message == "":
            return

        # 传递消息
        self.input_queue.put(message)

        # 清空输入框
        self.input_text.delete(0, "end")

        # 记录指令
        self.command_list.append(message)
        self.command_index += 1

    # 运行窗口
    def run(self):
        self.window.mainloop()

    # 上一条指令
    def previous_command(self, event):
        if len(self.command_list) == 0:
            return

        # 记录当前指令
        self.temp_command = self.input_text.get()

        # 获取上一条指令
        self.command_index = max(0, self.command_index - 1)
        self.input_text.delete(0, "end")
        self.input_text.insert(0, self.command_list[self.command_index])

    # 下一条指令
    def next_command(self, event):
        if len(self.command_list) == 0:
            return

        # 获取下一条指令
        self.command_index = min(len(self.command_list) - 1, self.command_index + 1)
        self.input_text.delete(0, "end")
        self.input_text.insert(0, self.command_list[self.command_index])

    # 等待接收输入的消息
    def wait_input(self):
        while True:
            output = self.output_queue.get()

            # 切割消息
            output_list = output.split(":")

            # 处理消息
            if output_list[0] == "log":
                # 将第二个元素往后的所有元素合并
                output_list[2] = ":".join(output_list[2:])
                now_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if output_list[1] == "error":
                    self.add_message("log", f"[{now_datetime}]错误：{output_list[2]}")
                elif output_list[1] == "warn":
                    self.add_message("log", f"[{now_datetime}]警告：{output_list[2]}")
                elif output_list[1] == "info":
                    self.add_message("log", f"[{now_datetime}]信息：{output_list[2]}")
            elif output_list[0] == "msg":
                # 将第一个元素往后的所有元素合并
                output_list[1] = ":".join(output_list[1:])
                now_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.add_message("msg", f"[{now_datetime}]{output_list[1]}")
