""" server """
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pydantic import BaseModel # 导入 BaseModel
from fastapi import FastAPI
from .core import ReallifeClient

async def perform_startup_tasks():
    """ 1 """
    print("Performing startup tasks...")
    scheduler.start()
    print("APScheduler 启动")
    # Your existing startup logic here

async def perform_shutdown_tasks():
    """ 1 """
    print("Performing shutdown tasks...")
    scheduler.shutdown()
    print("APScheduler 关闭")
    # Your existing shutdown logic here

class TaskRequest(BaseModel):
    """ 1 """
    task: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    """_summary_

    Args:
        app (FastAPI): _description_
    """
    await perform_startup_tasks()
    yield
    await perform_shutdown_tasks()


app = FastAPI(lifespan=lifespan)

scheduler = BackgroundScheduler()

reallife = ReallifeClient()

scheduler.add_job(reallife.kanban, CronTrigger(hour=10, minute=3, day_of_week='mon-fri'))


@app.get("/build_kanban")
async def receive():
    """_summary_

    Args:
        app (FastAPI): _description_
    """
    result = reallife.kanban()
    return {"message": result}

class BuildFlexibleConfigRequest(BaseModel):
    """ 1 """
    task: str = None
    type: str = 'flex' # or pool
    action: bool = True

@app.post("/build_flexible")
async def build_flexible(build_flexible_config: BuildFlexibleConfigRequest):
    """_summary_

    Args:
        build_flexible_config (BuildFlexibleConfigRequest): _description_
    """
    result = reallife.build_flexible(
        task=build_flexible_config.task,
        type=build_flexible_config.type,
        action=build_flexible_config.action
    )
    return {"message": result}

@app.post("/tips")
async def tips(task_request:TaskRequest):
    """_summary_

    Args:
        task_request (TaskRequest): _description_

    Returns:
        _type_: _description_
    """
    task = task_request.task
    reallife.tips(task)
    return {"message": '以添加'}

@app.get("/receive")
async def query_the_current_task():
    """_summary_

    Returns:
        _type_: _description_
    """
    result = reallife.query_the_current_task()
    # return {"message": result}
    return {"message":result.split(' ',1)[1]}


@app.get("/start")
async def start():
    """_summary_

    Returns:
        _type_: _description_
    """
    result = reallife.start()
    # return {"message": result}
    return {"message":result.split(' ',1)[1]}

@app.get("/close")
async def close():
    """_summary_

    Returns:
        _type_: _description_
    """
    result = reallife.close()
    return {"message": result}

@app.get("/run")
async def run():
    """_summary_

    Returns:
        _type_: _description_
    """
    result = reallife.run()
    return {"message": result}
    



if __name__ == "__main__":
    import argparse
    import uvicorn
    from .log import Log

    parser = argparse.ArgumentParser(
        description="Start a simple HTTP server similar to http.server."
    )
    parser.add_argument(
        'port',
        metavar='PORT',
        type=int,
        nargs='?',  # 端口是可选的
        default=8021,
        help='Specify alternate port [default: 8000]'
    )

    parser.add_argument(
        '--is-server',
        action='store_true',  # 如果命令行中包含 --is-server，则将 args.is_server 设置为 True
        help='Set the server status for the receive function to True'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        default='info',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help='Set the logging level [default: info]'
    )

    args = parser.parse_args()

    Log.reset_level(args.log_level)
    app.state.is_server_status = args.is_server

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=args.port,
        reload=False  # 启用热重载
    )
