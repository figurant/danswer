MESSAGE_TYPE_USER_QUESTION = 1
MESSAGE_TYPE_USER_ANSWER = 2
MESSAGE_TYPE_EXPERT_QUESTION = 3
MESSAGE_TYPE_EXPERT_ANSWER = 4
MESSAGE_TYPE_OTHERS = 0


def get_dlgwithtype_prompt(text):
    prompt = f"""
    背景：有一个Apache Doris用户答疑群，参与群聊的有Doris用户和Doris专家两类角色。\
    用户会在答疑群里发起数据库技术或使用等方面的咨询，专家针对用户咨询进行答疑，答疑过程中专家可能追问用户获取更多信息。
    输入描述：下文双反单引号中的文本是你的任务输入，这是一段截取自答疑群里某时间段的聊天记录，\
    其中每一行是一个消息记录，格式为“消息id”|”群昵称“|“消息时间”|”消息内容“。这段输入文本有4个特点。\
    1.这段聊天记录包含了多个不同的咨询记录。\
    2.每一个咨询记录可能包含多个消息，咨询记录中的消息可分为用户发起的提问、专家向用户索取更多信息、用户对此问题的补充说明、专家对问题的回答四种类型。\
    3.不同咨询的提问和答疑消息是相互穿插的。\
    4.有的消息不属于任何咨询，可能是消息通知或日常闲聊等。
    针对上述聊天记录，请以数据库专家的身份，依次完成以下两个任务。
    任务一：对输入文本进行分析，从这段聊天记录提取出所有的咨询记录，并识别出每个咨询记录中不同的消息类型和发言人角色。\
    做这个任务的时候，注意识别用户和专家两个角色，进行用户提问和用户补充的发送人是用户，向用户获取信息和回答的是专家，在一次咨询中，用户和专家身份不会变。\
    输出格式要求：将结果以表格的方式给出,字段间以“|”分隔。包括3个整型字段”消息id“，”消息类型“，”咨记录询id“。”咨询记录id“从1开始生成。\
    ”消息类型“有五种取值，分别为{MESSAGE_TYPE_USER_QUESTION}、\
    {MESSAGE_TYPE_USER_ANSWER}、{MESSAGE_TYPE_EXPERT_QUESTION}、\
    {MESSAGE_TYPE_EXPERT_ANSWER}、{MESSAGE_TYPE_OTHERS}。\
    {MESSAGE_TYPE_USER_QUESTION}表示用户的咨询问题，每一次咨询，都以用户的咨询问题开始。\
    {MESSAGE_TYPE_USER_ANSWER}表示用户对咨询问题的补充说明，或是对专家追问的回答。 \
    {MESSAGE_TYPE_EXPERT_QUESTION}表示专家针对用户的咨询问题进行追问，以获取更多用户问题的细节。\
    {MESSAGE_TYPE_EXPERT_ANSWER}表示专家对用户咨询问题的解答。\
    {MESSAGE_TYPE_OTHERS}表示不属于某次用户咨询，可能只是闲聊，或是消息通知，对于{MESSAGE_TYPE_OTHERS}类型的消息，”咨询记录id“记为0。\
    完成任务一的输出之后，输出一行"###"表示任务一已结束。
    任务二：针对任务一的分析结果，对其中每一个咨询记录依次进行以下两个步骤的分析。\
    第一步，分析这次咨询的类型，并给出分类的决策过程，咨询类型可分为四个大类十个二级类别。\
    可以按如下决策树过程进行类型判别：\
    首先判别是否是第一个大类是产品需求，二级分类为\
    1. 产品需求：只要专家回复提到目前不支持或将来在某版本支持的问题，都是产品需求。否则就不是产品需求。\
    如果不是第一大类，判别是否是第二个大类故障处理，二级分类包括\
    2. 监控指标异常：只要出现内存、CPU或负载高，磁盘打满，监控指标异常等情况，就是监控指标异常；\
    3. 服务不可用：只要出现服务宕机、服务卡住无响应、服务进程启动不了等情况，就是服务不可用。\
    如果不是第一、二大类，判别是否是第三个大类产品错误，二级分类包括\
    4. 兼容性问题：如BI软件、数据集成工具等生态工具对接使用过程中报错\
    5. 数据正确性问题：SQL查询结果不对，数据不正确或数据不一致问题\
    6. 功能缺陷：Doris产品功能异常、行为不符合预期或报错，如权限管控不生效、Catalog查询报错等。\
    如果不是以上三类，那就是第四类产品使用咨询，二级分类包括\
    7. 安装部署问题：Doris的安装部署方式、资源要求、软硬件配置等问题咨询\
    8. 使用方法咨询：如Doris的建表方式、分区分桶、参数配置、数据导入导出及各种功能使用问题\
    9. 性能调优：SQL查询性能或导入任务性能、并发、数据实时性等方面的优化方式咨询\
    10. 其他咨询：如果不属于以上类型，就视为其他咨询。
    第二步，为每个咨询根据其大类整理问题和答案。\
    对于产品使用咨询类型，综合整段咨询对话，详细的整理出用户问题和答案，要求可作为FAQ给以后的用户作为参考；\
    对于产品BUG问题，整理出一个产品BUG单，包括版本信息、BUG复现方法、报错信息等，不用给出答案；\
    对于故障处理问题，整理出一个故障问题单，包括版本信息、故障表现、影响范围等，不用给出答案；\
    对于产品需求，整理出一个产品需求单，包括需求详情和期望修复的版本。
    任务二的输出格式要求：将结果以表格的方式给出,字段间以“|”分隔。\
    包括7个字段”咨记录询id“、”问题大类“、”二级分类“、”版本“、”问题详情“、”答案“、”分类理由“。\
    其中，”问题大类“取值为1、2、3、4，分别代表上述四大类。\
    "二级分类"取值从1到10，对应上述10个类别。\
    ”版本“是从咨询记录中提取出来的，如果用户的提问中没有提到版本，请把这个字段置为NULL。\
    ”问题详情“根据问题大类，可能是用户问题详情、产品BUG单详情、故障问题单详情或产品需求的详情。\
    ”答案“字段是当类型为产品使用问题时，结合专家回复整体给出的答案。如果这个咨询没有专家回复，请把这个字段置为NULL。\
    ”分类理由“请给出这个咨询分类的决策过程。
    ``{text}``"""
    return prompt


def get_faq_prompt(text):
    prompt = f'''下文双反单引号中的文本是一段Apache Doris用户的问题答疑消息记录，\
    请总结成FAQ形式的一个QA对，方便其他Doris用户在提问之前可以先查阅FAQ寻找答案。
    QA对包括提问和回答，输出格式为"Q：xxx A：xxx "
    ``{text}``'''
    return prompt


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
