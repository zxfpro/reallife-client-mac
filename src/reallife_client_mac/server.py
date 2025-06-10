from appscriptz.scripts.applescript import Display, ShortCut
from kanbanz.manager import KanBanManager
from kanbanz.manager import Pool
import requests
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pydantic import BaseModel # 导入 BaseModel
from typing import List
from fastapi import FastAPI


# 定义 FastAPI 服务的基础 URL
BASE_URL = "http://localhost:8020"  # 如果你的服务运行在不同的地址或端口，请修改这里


def update_task(tasks:list):
    # 定义要发送的任务数据
    tasks_data = {
        "tasks": tasks
    }

    # 构建完整的 API URL
    url = f"{BASE_URL}/update_tasks"

    try:
        # 发送 POST 请求
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"}, # 指定请求体的内容类型为 JSON
            json=tasks_data # 将 Python 字典转换为 JSON 并作为请求体发送
        )

        # 检查响应状态码
        if response.status_code == 200:
            print("Request successful!")
            # 解析并打印响应的 JSON 数据
            print("Response data:")
            print(response.json())
        else:
            print(f"Request failed with status code: {response.status_code}")
            print("Response text:")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")

def receive_task():
    """
    接收当前任务。

    Returns:
        dict or None: 当前任务数据（如果请求成功），否则为 None。
    """
    url = f"{BASE_URL}/receive"
    try:
        response = requests.get(url)
        response.raise_for_status() # 如果请求失败（非2xx状态码），抛出异常
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求 /receive 失败: {e}")
        return None

def complete_task():
    """
    完成当前任务。

    Returns:
        dict or None: 完成任务的响应数据（如果请求成功），否则为 None。
    """
    url = f"{BASE_URL}/complete"
    try:
        response = requests.get(url)
        response.raise_for_status() # 如果请求失败（非2xx状态码），抛出异常
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求 /complete 失败: {e}")
        return None

def task_with_time(task_name:str,time:int=1):
    """计时任务

    Args:
        task_name (str): 任务名
        time (int, optional): 费用. Defaults to 1.
    """
    ShortCut.run_shortcut(shortcut_name="Session计时",params=f"{task_name}${time}")
    Display.display_dialog("计时结束", "需要结束计时任务吗?",buttons = '"结束"',button_cancel=False)

def failed_safe():
    '''
    查询session状态
    如果 当前session 状态是 session
        放弃session
    否则
        pass
    结束
    '''
    ShortCut.run_shortcut(shortcut_name="Session停止计时")





def deal_task(task:str):
    print('deal_task->',task)
    if task.startswith("A!"):
        task = task[2:]
        #TOOD 持续太久会请求超时
        if task: # work
            # study and experiment and code and Optimization and design and meeting_and_talk and Organizeand
            result = Display.display_dialog("Task Start",f"请打开飞书会议, 标题为{task} 自我审视+ 反思 + 分析笔记",buttons = '"完成"',button_cancel=False)
            if result == '完成':
                task_with_time(task_name = task,time=60)
                failed_safe()
            else:
                return "任务已取消"


        else:
            # practice
            pass



class ReallifeClient():
    def __init__(self):
        self.pathlibs = ["/工程系统级设计/项目级别/数字人生/DigitalLife/DigitalLife.canvas",
                         "/工程系统级设计/项目级别/自动化工作/coder/coder.canvas",]
        self.kanban_path = "/Users/zhaoxuefeng/GitHub/obsidian/工作/事件看板/事件看板.md"
        self.manager = KanBanManager(self.kanban_path,self.pathlibs)

    def kanban(self):
        self.manager.sync_ready()
        self.manager.sync_order()
        # 调整时间和顺序 dig
        Display.display_dialog('调整','调整时间和顺序')
        self.manager.sync_run()
        tasks = self.manager.kanban.get_tasks_in(Pool.执行池)
        update_task(['A!'+i for i in tasks])

    def query_the_current_task(self):
        task = receive_task().get("message")
        return task

    def start(self):
        task = receive_task().get("message")
        if task:
            if "待办" in task:
                # print('todo',task)
                deal_task(task)
                complete_task() # 调试
                return f"task: {task} 进行中"
            return '没有任务可以开始或者任务正在进行中'


    def close(self):
        task = receive_task().get("message")
        if task:
            if "进行中" in task:
                # 从执行池移除 放到完成池
                # 从canvas 中移除
                complete_task()
                return f"task: {task} 已完成"
            return '没有任务可以结束'

    def tips(self,task:str):
        self.manager.add_tips(task)
        return 'success'




app = FastAPI()

scheduler = BackgroundScheduler()

reallife = ReallifeClient()
# 工作日 (周一到周五) 的 10:00
# 早上定时任务, -> 做收集

scheduler.add_job(reallife.kanban, CronTrigger(hour=10, minute=0, day_of_week='mon-fri'))

@app.get("/build_kanban")
async def receive():
    result = reallife.kanban()
    return {"message": result}

class TaskRequest(BaseModel):
    task: str

@app.post("/tips")
async def tips(task_request:TaskRequest):
    task = task_request.task
    reallife.tips(task)
    return {"message": '以添加'}

@app.get("/receive")
async def query_the_current_task():
    result = reallife.query_the_current_task()
    return {"message": result}

@app.get("/start")
async def morning():
    result = reallife.start()
    return {"message": result}

@app.get("/close")
async def close():
    result = reallife.close()
    return {"message": result}





if __name__ == "__main__":
    # 这是一个标准的 Python 入口点惯用法
    # 当脚本直接运行时 (__name__ == "__main__")，这里的代码会被执行
    # 当通过 python -m YourPackageName 执行 __main__.py 时，__name__ 也是 "__main__"
    import argparse
    import uvicorn
    parser = argparse.ArgumentParser(
        description="Start a simple HTTP server similar to http.server."
    )
    parser.add_argument(
        'port',
        metavar='PORT',
        type=int,
        nargs='?', # 端口是可选的
        default=8021,
        help='Specify alternate port [default: 8000]'
    )

    parser.add_argument(
        '--is-server',
        action='store_true', # 如果命令行中包含 --is-server，则将 args.is_server 设置为 True
        help='Set the server status for the receive function to True'
    )

    args = parser.parse_args()
    app.state.is_server_status = args.is_server

    # 使用 uvicorn.run() 来启动服务器
    # 参数对应于命令行选项
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=args.port,
        reload=False  # 启用热重载
    )
