from reallife_client_mac import log



def test_log():
    logger = log().logger

    # logger = setup_logging()

    logger.debug("这是一个 DEBUG 级别的日志消息。")
    logger.info("程序启动成功，正在加载配置。")
    logger.warning("发现一个潜在问题：磁盘空间不足。")
    logger.error("处理用户请求时发生错误，用户ID: 123。")
    logger.critical("数据库连接失败，程序即将退出！")

    try:
        result = 10 / 0
    except Exception as e:
        logger.exception("除零错误发生！") # logger.exception() 会自动包含 traceback 信息

    logger.info("程序运行结束。")

