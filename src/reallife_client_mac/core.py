""" core """
import threading
import requests
from appscriptz.scripts.applescript import Display, ShortCut
from kanbanz.manager import KanBanManager
from kanbanz.manager import Pool
from canvaz import Canvas,Color
from kanbanz.utils import controlKanban

# 定义 FastAPI 服务的基础 URL Server
BASE_URL = "http://101.201.244.227:8020"  # 如果你的服务运行在不同的地址或端口，请修改这里


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


class ReallifeClient():
    """ 23 """
    def __init__(self):
        self.pathlibs = ["/工程系统级设计/项目级别/数字人生/DigitalLife/DigitalLife.canvas",
                         "/工程系统级设计/项目级别/近期工作/近期工作.canvas",
                         "/工程系统级设计/能力级别/reallife-client-mac/reallife-client-mac.canvas",
                         "/工程系统级设计/能力级别/reallife/reallife.canvas",
                         "/工程系统级设计/能力级别/kanbanz/kanbanz.canvas",
                         "/工程系统级设计/能力级别/clientz/clientz.canvas",
                         "/工程系统级设计/能力级别/commender/commender.canvas",
                         "/工程系统级设计/能力级别/llmada/llmada.canvas",
                         "/工程系统级设计/能力级别/promptlibz/promptlibz.canvas",
                         ]
        self.pathlibs_dict = {
                        "DigitalLife":"/Users/zhaoxuefeng/GitHub/obsidian/工作/工程系统级设计/项目级别/数字人生/DigitalLife/DigitalLife.canvas",
                        "近期工作":"/Users/zhaoxuefeng/GitHub/obsidian/工作/工程系统级设计/项目级别/近期工作/近期工作.canvas",
                        "reallife-client-mac":"/Users/zhaoxuefeng/GitHub/obsidian/工作/工程系统级设计/能力级别/reallife-client-mac/reallife-client-mac.canvas",
                        "reallife":"/Users/zhaoxuefeng/GitHub/obsidian/工作/工程系统级设计/能力级别/reallife/reallife.canvas",
                        "kanbanz":"/Users/zhaoxuefeng/GitHub/obsidian/工作/工程系统级设计/能力级别/kanbanz/kanbanz.canvas",
                        "clientz":"/Users/zhaoxuefeng/GitHub/obsidian/工作/工程系统级设计/能力级别/clientz/clientz.canvas",
                        "commender":"/Users/zhaoxuefeng/GitHub/obsidian/工作/工程系统级设计/能力级别/commender/commender.canvas",
                        "llmada":"/Users/zhaoxuefeng/GitHub/obsidian/工作/工程系统级设计/能力级别/llmada/llmada.canvas",
                        "promptlibz":"/Users/zhaoxuefeng/GitHub/obsidian/工作/工程系统级设计/能力级别/promptlibz/promptlibz.canvas",
                    }
        self.kanban_path = "/Users/zhaoxuefeng/GitHub/obsidian/工作/事件看板/事件看板.md"
        self.manager = KanBanManager(self.kanban_path,self.pathlibs)

    def kanban(self): # 自动推送
        """ 2 """
        print('kanbans')
        self.manager.sync_ready()
        self.manager.sync_order()
        # 调整时间和顺序 dig
        Display.display_dialog('调整','调整时间和顺序')
        self.manager.sync_run()
        tasks = self.manager.kanban.get_tasks_in(Pool.执行池)
        self._update_task(['A!'+i for i in tasks])
        return ''
    
    def build_flexible(self,task:str = None,
                       type:str = 'flex',action = True)->str:
        if type == 'pool':
            tasks = self.manager.kanban.get_tasks_in(pool=Pool.酱油池)
        elif type == 'flex':
            tasks = [task]
        else:
            tasks = ['failed build']

        if action:
            tasks = ['A!'+i for i in tasks]


        self._update_task(tasks)

        return 'successed build'



    def _update_task(self,tasks:list):
        """ 2 """
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
                json=tasks_data, # 将 Python 字典转换为 JSON 并作为请求体发送
                timeout=10
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

    def _receive_task(self):
        """
        接收当前任务。

        Returns:
            dict or None: 当前任务数据（如果请求成功），否则为 None。
        """
        url = f"{BASE_URL}/receive"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status() # 如果请求失败（非2xx状态码），抛出异常
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求 /receive 失败: {e}")
            return None




    def _complete_task(self)->dict:
        """
        完成当前任务。

        Returns:
            dict or None: 完成任务的响应数据（如果请求成功），否则为 None。
        """
        url = f"{BASE_URL}/complete"
        try:
            response = requests.get(url,timeout=10)
            response.raise_for_status() # 如果请求失败（非2xx状态码），抛出异常
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求 /complete 失败: {e}")
            return {}

    def _deal_task(self,task:str):
        """ 2 """

        if task.startswith("A!") and task.endswith("(待办)"):
            task = task.replace('A!','').replace("(待办)",'').strip()
            #TOOD 持续太久会请求超时
            if task: # work
                times,task_info = task.split(' ',1)
                assert times.endswith('P')
                task_time = eval(times.replace('P','*20'))
                def do_task():
                    result = Display.display_dialog(
                        "Task Start", f"请打开飞书会议, 标题为{task_info} 自我审视+ 反思 + 分析笔记", 
                        buttons='"完成"',
                        button_cancel=False)
                    if result == '完成':
                        task_with_time(task_name=task_info.replace('$','--'), time=task_time)
                        failed_safe()

                        # TODO 移除任务
                        try:
                            with controlKanban(self.manager.kanban) as kb:
                                kb.pop(task,pool=Pool.执行池)
                                kb.insert(text=task,pool=Pool.完成池)
                        except Exception as e:
                            print('e',e)


                        # TODO 在对应位置修改任务颜色
                        repo,task_card = task_info.split('$',1)

                        file_path = self.pathlibs_dict.get(repo,None)
                        if not file_path:
                            return 'failed pathlibs_dict.get None'

                        canvas = Canvas(file_path=file_path)
                        nodes = canvas.select_nodes_by_text(task_card)
                        # 判断是否解决, 未完全解决设置为0 如果完全解决设置为4
                        result_callback = Display.display_dialog(
                            "Task End", f"标题为{task_info} 的任务是否彻底完成", 
                            buttons='"是"',
                            button_cancel=True)
                        if result_callback =="是":
                            color = "4"
                        else:
                            color = "0"
                        nodes[0].color = color
                        canvas.to_file(file_path)


                    else:
                        # 线程中不能直接 return, 可以考虑设置某种状态或日志
                        print("任务已取消")
                    


                t = threading.Thread(target=do_task)
                t.start()


            else:
                # practice
                pass


    def query_the_current_task(self):
        """ 2 """
        task = self._receive_task().get("message")
        return task

    def start(self):
        """ 2 """
        task = self._receive_task().get("message")
        if task:
            if "待办" in task:
                # print('todo',task)
                self._deal_task(task)
                self._complete_task() # 调试
                return f"task: {task} 进行中"
            return '没有任务可以开始或者任务正在进行中'

    def close(self):
        """ 2 """
        task = self._receive_task().get("message")
        if task:
            if "进行中" in task:
                # 从执行池移除 放到完成池
                # 从canvas 中移除
                self._complete_task()
                return f"task: {task} 已完成"
            return '没有任务可以结束'

    def run(self):
        """ 2 """
        task = self._receive_task().get("message")
        if task:
            if "待办" in task:
                self._deal_task(task)
                result = self._complete_task()
            elif "进行中" in task:
                result = self._complete_task()
            else:
                result = {'message':'所有任务已完成'}
            info = result.get('message')
            return info

    def tips(self,task:str):
        """ 添加内容到管理中 """
        # 做交互窗口, 选择到对应的仓库 -> clientz
        # 选择工作模式 -> prefer bug research 
        # 提交问题和详细描述(可以填无,富文本-理想 ) 以问题为主要导向


        # 合并并加入到指定的位置
        # tast_mock = "prefer:clientz:优化问题路线:具体的问题路线如下,1 设置工作空间"
        types,repo,quesion,detail = task.split(':',3)
        
        file_path = self.pathlibs_dict.get(repo,None)
        if not file_path:
            return 'failed pathlibs_dict.get None'

        canvas = Canvas(file_path=file_path)
        if types == 'bug':
            color = "3"
        elif types == 'prefer':
            color = "2"
        else:
            color = "0"

        canvas.add_node(types + ":" + quesion +'\n'+ detail,color=color)
        canvas.to_file(file_path)
        # self.manager.add_tips(task)
        return 'success'
