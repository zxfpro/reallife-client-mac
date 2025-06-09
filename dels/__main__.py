import requests
import json

class ReallifeClient:
    def __init__(self, base_url):
        """
        初始化 Reallife 客户端。

        Args:
            base_url (str): API 的基础 URL。
        """
        self.base_url = base_url

    def list_tasks(self):
        """
        获取任务列表。

        Returns:
            dict or None: 任务列表数据（如果请求成功），否则为 None。
        """
        url = f"{self.base_url}/list_tasks"
        try:
            response = requests.get(url)
            response.raise_for_status() # 如果请求失败（非2xx状态码），抛出异常
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求 /list_tasks 失败: {e}")
            return None

    def receive_task(self):
        """
        接收当前任务。

        Returns:
            dict or None: 当前任务数据（如果请求成功），否则为 None。
        """
        url = f"{self.base_url}/receive"
        try:
            response = requests.get(url)
            response.raise_for_status() # 如果请求失败（非2xx状态码），抛出异常
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求 /receive 失败: {e}")
            return None

    def complete_task(self):
        """
        完成当前任务。

        Returns:
            dict or None: 完成任务的响应数据（如果请求成功），否则为 None。
        """
        url = f"{self.base_url}/complete"
        try:
            response = requests.get(url)
            response.raise_for_status() # 如果请求失败（非2xx状态码），抛出异常
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求 /complete 失败: {e}")
            return None

    def morning(self):
        """
        执行“早”操作。

        Returns:
            dict or None: “早”操作的响应数据（如果请求成功），否则为 None。
        """
        url = f"{self.base_url}/morning"
        try:
            response = requests.get(url)
            response.raise_for_status() # 如果请求失败（非2xx状态码），抛出异常
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求 /morning 失败: {e}")
            return None

    def clear_tasks(self):
        """
        清除任务。

        Returns:
            dict or None: 清除任务的响应数据（如果请求成功），否则为 None。
        """
        url = f"{self.base_url}/clear"
        try:
            response = requests.get(url)
            response.raise_for_status() # 如果请求失败（非2xx状态码），抛出异常
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求 /clear 失败: {e}")
            return None

if __name__ == "__main__":
    # 示例用法：
    # 请将 'http://your_server_address' 替换为实际的服务器地址
    client = ReallifeClient('http://127.0.0.1:8020')

    tasks = client.list_tasks()
    if tasks:
        print("任务列表:", tasks)

    current_task = client.receive_task()
    if current_task:
        print("当前任务:", current_task)

    complete_res = client.complete_task()
    if complete_res:
        print("完成任务结果:", complete_res)

    morning_res = client.morning()
    if morning_res:
        print("早操作结果:", morning_res)

    clear_res = client.clear_tasks()
    if clear_res:
        print("清除任务结果:", clear_res)







# 编码与迭代
# 练习与优化
# 整理与设计与实验摸索学习
# 开会与对齐




# 1 做看板的动作
# 2 将看板的结论上传到服务器 来管理和维护