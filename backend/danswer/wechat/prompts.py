MESSAGE_TYPE_USER_QUESTION = 1
MESSAGE_TYPE_USER_ANSWER = 2
MESSAGE_TYPE_EXPERT_QUESTION = 3
MESSAGE_TYPE_EXPERT_ANSWER = 4
MESSAGE_TYPE_OTHERS = 0


def get_ana_wx_prompt2(
        text: str
) -> str:
    prompt = f"""
下文双反单引号中的文本是一个数据库用户群的聊天记录，每一行是一个聊天消息，格式为：“消息id”|”发送人“|“消息时间”|”消息内容“。\
这些消息是用户对数据库的使用和技术方面的咨询，有数据库专家进行答疑。\
由于用户很多，不同用户的咨询和答疑消息相互穿插，你的任务是将聊天记录分成不同的咨询记录。\
将结果以表格的方式给出,字段间以“|”分隔。\
包括3个字段：”消息id“，”消息类型“，”咨询id“。\
”咨询记录id“从1开始生成，所有属于同一次咨询的消息有同一个咨询id。\
”消息类型“有五种取值，分别为{MESSAGE_TYPE_USER_QUESTION}、\
{MESSAGE_TYPE_USER_ANSWER}、{MESSAGE_TYPE_EXPERT_QUESTION}、\
{MESSAGE_TYPE_EXPERT_ANSWER}、{MESSAGE_TYPE_OTHERS}。\
{MESSAGE_TYPE_USER_QUESTION}表示用户的咨询问题，每一次咨询，都以用户的咨询问题开始。\
{MESSAGE_TYPE_USER_ANSWER}表示用户对咨询问题的补充说明，或是对专家追问的回答。 \
{MESSAGE_TYPE_EXPERT_QUESTION}表示专家针对用户的咨询问题进行追问，以获取更多用户问题的细节。\
{MESSAGE_TYPE_EXPERT_ANSWER}表示专家对用户咨询问题的解答。\
{MESSAGE_TYPE_OTHERS}表示不属于某次用户咨询，可能只是闲聊，或是消息通知，对于{MESSAGE_TYPE_OTHERS}类型的消息，”咨询id“记为0。\
做这个任务的时候，注意识别用户和专家两个角色，进行用户提问和用户补充的发送人是用户，追问和回答的是专家，在一次咨询中，用户和专家身份不会变。

``{text}``
"""
    return prompt


def get_ana_wx_prompt(
        text: str
) -> str:
    prompt = f"""
背景：有一个数据库用户答疑群，参与群聊的有数据库用户和数据库专家两类角色。\
用户会在答疑群里发起数据库技术或使用等方面的咨询，专家针对用户咨询进行答疑，答疑过程中专家可能追问用户获取更多信息。
输入描述：下文双反单引号中的文本是你的任务输入，这是一段截取自答疑群里某时间段的聊天记录，\
其中每一行是一个消息记录，格式为“消息id”|”群昵称“|“消息时间”|”消息内容“。这段输入文本有4个特点。\
1.这段聊天记录包含了多个不同的咨询记录。\
2.每一个咨询记录可能包含多个消息，咨询记录中的消息可分为用户发起的提问、专家向用户索取更多信息、用户对此问题的补充说明、专家对问题的回答四种类型。\
3.不同咨询的提问和答疑消息是相互穿插的。\
4.有的消息不属于任何咨询，可能是消息通知或日常闲聊等，这类消息占比很低，不超过20%。
任务：请你以数据库专家的身份，根据输入文本的特点，对输入文本进行分析，从这段聊天记录提取出所有的咨询记录，并识别出每个咨询记录中不同的消息类型和发言人角色。\
做这个任务的时候，注意识别用户和专家两个角色，进行用户提问和用户补充的发送人是用户，向用户获取信息和回答的是专家，在一次咨询中，用户和专家身份不会变。
输出格式要求：将结果以表格的方式给出,字段间以“|”分隔。包括3个整型字段”消息id“，”消息类型“，”咨记录询id“。”咨询记录id“从1开始生成。\
”消息类型“有五种取值，分别为{MESSAGE_TYPE_USER_QUESTION}、\
{MESSAGE_TYPE_USER_ANSWER}、{MESSAGE_TYPE_EXPERT_QUESTION}、\
{MESSAGE_TYPE_EXPERT_ANSWER}、{MESSAGE_TYPE_OTHERS}。\
{MESSAGE_TYPE_USER_QUESTION}表示用户的咨询问题，每一次咨询，都以用户的咨询问题开始。\
{MESSAGE_TYPE_USER_ANSWER}表示用户对咨询问题的补充说明，或是对专家追问的回答。 \
{MESSAGE_TYPE_EXPERT_QUESTION}表示专家针对用户的咨询问题进行追问，以获取更多用户问题的细节。\
{MESSAGE_TYPE_EXPERT_ANSWER}表示专家对用户咨询问题的解答。\
{MESSAGE_TYPE_OTHERS}表示不属于某次用户咨询，可能只是闲聊，或是消息通知，对于{MESSAGE_TYPE_OTHERS}类型的消息，”咨询记录id“记为0。
``{text}``
"""
    return prompt
