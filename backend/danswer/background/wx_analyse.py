import sys
import os

# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.realpath(__file__))

# 将项目目录添加到Python路径
project_dir = os.path.join(current_dir, '../..')  # 假设项目目录是当前目录的上一级
sys.path.append(project_dir)

from sqlalchemy.orm import Session

from danswer.configs.app_configs import LOG_FILE_STORAGE
from danswer.db.engine import get_sqlalchemy_engine
from danswer.wechat.analyze_message import get_dialogs, preprocess_msgs
from danswer.wechat.file_logger import FileLogger

update_logger = FileLogger(f'{LOG_FILE_STORAGE}/wx_analyse.log', level='debug')
logger = update_logger.logger


def main(file_path):
    engine = get_sqlalchemy_engine()
    with Session(engine, expire_on_commit=False) as db_session:
        msgs = preprocess_msgs(db_session, file_path)
        dialogs = get_dialogs(db_session, msgs, file_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("请提供文件路径作为命令行参数.")
    else:
        file_path = sys.argv[1]
        main(file_path)
