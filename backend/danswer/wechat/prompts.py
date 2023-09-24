MESSAGE_TYPE_USER_QUESTION = 1
MESSAGE_TYPE_USER_ANSWER = 2
MESSAGE_TYPE_EXPERT_QUESTION = 3
MESSAGE_TYPE_EXPERT_ANSWER = 4
MESSAGE_TYPE_OTHERS = 0


def get_ana_wx_prompt(
        text: str
    ) -> str:
    prompt = f"""
下文双反单引号中的文本是一个数据库用户群的聊天记录，每一行是一个聊天消息，格式为：“消息id”|”发送人“|“消息时间”|”消息内容“。\
这些消息是用户对数据库的使用和技术方面的咨询，有数据库专家进行答疑。\
由于用户很多，不同用户的咨询和答疑消息相互穿插，你的任务是将聊天记录分成不同的咨询记录。\
将结果以表格的方式给出,字段间以“|”分隔。\
包括3个字段：”消息id“，”消息类型“，”咨询id“。\
”咨询记录id“从1开始生成，所有属于同一次咨询的消息有同一个咨询id。\
”消息类型“有五种取值，分别为：”用户提问“记为{MESSAGE_TYPE_USER_QUESTION}、\
“用户补充”记为{MESSAGE_TYPE_USER_ANSWER}、“专家追问”记为{MESSAGE_TYPE_EXPERT_QUESTION}、\
“专家回答”记为{MESSAGE_TYPE_EXPERT_ANSWER}、“其他”记为{MESSAGE_TYPE_OTHERS}。\
”用户提问“表示用户的咨询问题，每一次咨询，都以用户的咨询问题开始。\
“用户补充”表示用户对咨询问题的补充说明，或是对“专家追问”的回答。 \
“专家追问”表示专家针对用户的咨询问题进行追问，以获取更多用户问题的细节。\
“专家回答”表示专家对用户咨询问题的解答。\
“其他”表示不属于某次用户咨询，可能只是闲聊，或是消息通知，对于“其他”类型的消息，”咨询id“记为0。\
做这个任务的时候，注意识别用户和专家两个角色，进行用户提问和用户补充的发送人是用户，追问和回答的是专家，在一次咨询中，用户和专家身份不会变。

``{text}``
"""
    return prompt
