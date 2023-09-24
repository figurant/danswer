from typing import List
from uuid import UUID

from danswer.db.dwd_wx_dialog import create_dwd_wx_dialog
from danswer.wechat.prompts import MESSAGE_TYPE_USER_QUESTION, MESSAGE_TYPE_USER_ANSWER
from sqlalchemy.orm import Session


class Message:
    id: int
    sender: str
    send_time: str
    content: str
    type: int

    def __init__(self, id, sender, send_time, content, type):
        self.id = id
        self.sender = sender
        self.send_time = send_time
        self.content = content
        self.type = type

    def get_msg_txt(self):
        return f"{self.id}|{self.sender}|{self.send_time}|{self.content}"


class Dialog:
    messages: List[Message]
    has_answer: bool
    uuid: UUID

    def __init__(self, uuid, messages, has_answer: bool = False):
        self.uuid = uuid
        self.messages = messages
        self.has_answer = has_answer

    def add_message(self, message):
        self.messages.append(message)

    def set_has_answer(self):
        self.has_answer = True

    def get_qa_block(self):
        qa_block = ""
        for msg in self.messages:
            if int(msg.type) == MESSAGE_TYPE_USER_QUESTION or int(msg.type) == MESSAGE_TYPE_USER_ANSWER:
                qa = "Question"
            else:
                qa = "Answer"
            qa_block += f"{qa}: {msg.content}\n"
        return qa_block

    def commit_dwd_wx_dialog(self, db_session: Session):
        for m in self.messages:
            create_dwd_wx_dialog(db_session, m.id, m.type, str(self.uuid))
