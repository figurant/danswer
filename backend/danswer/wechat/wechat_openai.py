import openai

from danswer.configs.app_configs import LOG_FILE_STORAGE
from danswer.configs.model_configs import GEN_AI_API_KEY
from danswer.wechat.file_logger import FileLogger
from danswer.wechat.prompts import get_ana_wx_prompt2, get_ana_wx_prompt, get_dlgwithtype_prompt, get_faq_prompt
import threading
import time
import re
# 创建一个锁
lock = threading.Lock()
# 设置最大重试次数
MAX_RETRIES = 3

openai.api_key = GEN_AI_API_KEY
update_logger = FileLogger(f'{LOG_FILE_STORAGE}/openai.log', level='debug')
logger = update_logger.logger


def get_dlg_from_llm_withretry(text, model):
    max_retry = 3
    for _ in range(max_retry):
        if _ > 0:
            print(f'dialogs_txt format is wrong, do {_} retry')
        dialogs_txt = get_dlg_from_llm(text, model)
        # 检查输出格式，如果不对的话重试
        format_ok = False
        lines = dialogs_txt.splitlines()
        for i, line in enumerate(lines):
            line = line.replace(" ", "")
            match_obj = re.match(r'(\d+)\|(\d+)\|(\d+)', line)
            if not match_obj:
                match_obj = re.match(r'\|(\d+)\|(\d+)\|(\d+)\|', line)
            if match_obj:
                format_ok = True
                break
        if format_ok:
            break
    return dialogs_txt


def get_dlg_from_llm(text, model):
    prompt = get_ana_wx_prompt2(text)
    dialogs_txt = try_get_completion(prompt, model)
    logger.debug(
        f'get_completion prompt:\n{prompt}\n result:\n{dialogs_txt}\n')
    return dialogs_txt


def get_dlgwithtype_from_llm(text, model):
    prompt = get_dlgwithtype_prompt(text)
    dialogs_txt = try_get_completion(prompt, model)
    logger.debug(
        f'get_completion prompt:\n{prompt}\n result:\n{dialogs_txt}\n')
    return dialogs_txt


def get_faq_from_llm(text, model):
    prompt = get_faq_prompt(text)
    faq_txt = try_get_completion(prompt, model)
    logger.debug(
        f'get_completion prompt:\n{prompt}\n result:\n{faq_txt}\n')
    return faq_txt


def try_get_completion(prompt, model):
    result = ""
    global lock
    with lock:
        retries = 0
        while retries < MAX_RETRIES:
            try:
                result = get_completion_v2(prompt, model)
                break
            except Exception as e:
                retries += 1
                print(f"Exception occurred in openai get_completion: {e}")
                if retries < MAX_RETRIES:
                    print("Sleeping for 5 seconds before retrying...")
                    time.sleep(5)
                else:
                    raise
    return result


def get_completion(prompt, model):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def get_completion_v2(prompt, model):
    messages = [
        {"role": "system",
         "content": "你是Apache Doris资深解决方案架构师，精通OLAP数据库，对Apache Doris的技术原理、功能特性、场景解决方案、最佳实践等方面都非常熟悉。"},
        {"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def get_completion_mock(prompt, model="gpt-3.5-turbo"):
    return '''消息id|消息类型|咨询id
807|1|1
'''


if __name__ == "__main__":
    text = '''1081|向阳而生|2023-09-13 09:19:00|doris 支持滚动游标么？
1083|向阳而生|2023-09-13 09:21:00|这种每次查询100条  doris查询的结果是不是  会不正确
1084|张英杰-深圳_doris-2.0.2|2023-09-13 09:27:00|得加上order by limit offset
1085|.|2023-09-13 09:40:00|请问下，实现flink cdc 对doris 分布式写入，会固定在某台，如何进行负载均衡？
1086|清榭|2023-09-13 09:41:00|flink写doris不是有connect吗
1087|清榭|2023-09-13 09:41:00|这个分布式写不写入是啥，connect里面有提供这个功能吗
1088|.|2023-09-13 09:46:00|那只是针对一台把。
1089|清榭|2023-09-13 09:46:00|[发呆]
1090|.|2023-09-13 09:46:00|是不是得搞个brocker
1091|清榭|2023-09-13 09:47:00|我也不知道，我就用过几次，就是直接用connect写入就行了
1092|gneHiL|2023-09-13 09:49:00|是说每次写入的链接 be 是固定的吗？
1093|牛满仓|2023-09-13 09:55:00|fe be节点买阿里云计算行还是通用型比较好
1095|牛满仓|2023-09-13 09:56:00|测试环境8c/32G是不是就能跑
1096|张彬华|2023-09-13 09:56:00|是的
1098|牛满仓|2023-09-13 09:57:00|https://cn.selectdb.com/docs/enterprise/enterprise-core-guide/selectdb-distribution-doris-core-deployment-guide
1099|牛满仓|2023-09-13 09:57:00|看到了
1100|牛满仓|2023-09-13 09:57:00|谢谢
1101|牛满仓|2023-09-13 09:58:00|直接3个fe + 3个be节点就好了
1102|牛满仓|2023-09-13 09:58:00|可用性强一点
1103|.|2023-09-13 10:00:00|flink cdc 我现在对接doris 好像只写一台
1105|.|2023-09-13 10:00:00|一台IO很高
1106|gneHiL|2023-09-13 10:05:00|私聊看下吧
1107|张家锋|2023-09-13 10:23:00|可能很多同学还不知道这个功能
1108|张家锋|2023-09-13 10:23:00|[链接] Apache Doris SQL 黑名单功能介绍及使用
1109|StaySilence|2023-09-13 10:28:00|[强]
1110|叶宝喜|2023-09-13 10:35:00|[强][强][强]
1112|向阳而生|2023-09-13 10:54:00|我这样部分列更新 报错呢
1113|向阳而生|2023-09-13 10:54:00|把这个取消掉 不报错
1115|WZ-郑州-1.2.4|2023-09-13 10:56:00|FlinkCDC中，如果mysql新增一个字段，Doris的uq模型下会自动新增字段吗？
1116|南方有乔木|2023-09-13 11:00:00|doris可以存图片吗
1117|张彬华|2023-09-13 11:02:00|目前还不支持
1118|苏奕嘉@SelectDB|2023-09-13 11:03:00|可以丢S3，存储URL
1119|敬天爱人-2.0.1-k8s-选型测试中|2023-09-13 11:03:00|可以base64后存储
1120|苏奕嘉@SelectDB|2023-09-13 11:03:00|或者Base64转成String
1121|WZ-郑州-1.2.4|2023-09-13 11:09:00|FlinkCDC中，如果mysql新增一个字段，Doris的uq模型下会自动新增字段吗？@苏奕嘉@SelectDB
1122|张家锋|2023-09-13 11:09:00|支持
1123|cl|2023-09-13 11:13:00|我试过用doris-connector整库同步，新增删除字段都可以，但是只要字段改了名字或者改了数据类型，这个字段就不同步了
1124|BelieF:doris1.2.6|2023-09-13 11:13:00|直接insert into doris,mysql的delete会在doris中delete吗？还是要自己写逻辑？
1125|BelieF:doris1.2.6|2023-09-13 11:14:00|分享下源码[呲牙]
1126|WZ-郑州-1.2.4|2023-09-13 11:14:00|@张家锋 为啥我的没有同步修改呢
1127|张家锋|2023-09-13 11:14:00|https://github.com/apache/doris-flink-connector
1128|张家锋|2023-09-13 11:15:00|这个要flink 1.17 ，Doris flink connector 1.4.0
1129|cl|2023-09-13 11:15:00|官网例子
1130|WZ-郑州-1.2.4|2023-09-13 11:15:00|现在就是这个版本
1131|张家锋|2023-09-13 11:15:00|doris 要1.2.0 以上版本
1132|张家锋|2023-09-13 11:15:00|你的表开启轻量级schema chanage没
1133|张家锋|2023-09-13 11:15:00|需要开启这个
1134|cl|2023-09-13 11:16:00|https://doris.apache.org/zh-CN/docs/dev/ecosystem/flink-doris-connector/#mysql%E5%90%8C%E6%AD%A5%E7%A4%BA%E4%BE%8B
1135|cl|2023-09-13 11:16:00|这是在哪开
1137|cl|2023-09-13 11:17:00|看到了，是加这个参数是吧
1138|cl|2023-09-13 11:18:00|666
1140|Simba|2023-09-13 11:21:00|是这个
1141|cl|2023-09-13 11:24:00|感谢，空了去试试
1142|WZ-郑州-1.2.4|2023-09-13 11:37:00|@cl 这个参数加到Mysql是吗
1143|cl|2023-09-13 11:38:00|不是
1146|BelieF:doris1.2.6|2023-09-13 11:43:00|cdc同步多表的时候 ，sink不需要指定表名吗
1147|BelieF:doris1.2.6|2023-09-13 11:44:00|我现在要同步4张 schema不同的表， 可以通过一个任务这种配置的方式完成么？
1149|SelectDB 黄海军|2023-09-13 11:44:00|红框是表名
1150|SelectDB 黄海军|2023-09-13 11:44:00|你可以看看这个参数的介绍
1151|SelectDB 黄海军|2023-09-13 11:45:00|支持正则
1152|SelectDB 黄海军|2023-09-13 11:45:00|不同的表可以用 ｜ 分隔开
1153|BelieF:doris1.2.6|2023-09-13 11:46:00|红色框是 source吧？ sink的表呢？
1154|SelectDB 黄海军|2023-09-13 11:47:00|自动建表啊
1155|BelieF:doris1.2.6|2023-09-13 11:47:00|哦哦哦 ，我试下 [合十]
1156|SelectDB 黄海军|2023-09-13 11:48:00|[ok]
1157|张新平|2023-09-13 13:18:00|1.2.4.1版本，新建一张表，"light_schema_change" = "true" ， alter 增加key列很慢，新建一张表，不加 light_schema_change 属性，alter 增加key列秒级，有木有大佬知道是咋回事啊。
1158|南方有乔木|2023-09-13 14:11:00|大佬们
1160|南方有乔木|2023-09-13 14:12:00|两个两个子查询直接用,号隔开不用join，是什么神仙语法
1161|GTN|2023-09-13 14:13:00|逗号隔开替代join
1162|南方有乔木|2023-09-13 14:14:00|ok
1163|GTN|2023-09-13 14:14:00|算是Inner join的简写
1164|南方有乔木|2023-09-13 14:28:00|set enable_insert_strict=false;，这个参数是单会话生效吗，还是啥
1165|苏奕嘉@SelectDB|2023-09-13 14:32:00|对
1166|苏奕嘉@SelectDB|2023-09-13 14:33:00|不加global就是单次回话
1167|苏奕嘉@SelectDB|2023-09-13 14:33:00|会话
1168|freeshow|2023-09-13 14:47:00|doris现在还是全内存计算吗
1169|freeshow|2023-09-13 14:47:00|有shuffle落盘过程吗
1170|敬天爱人-2.0.1-k8s-选型测试中|2023-09-13 14:48:00|请教个基础问题，doris对表的数量很多  500左右。 但是数据量不大 每个表1G左右，几千万行数据。，这种场景支持的怎么样
1171|敬天爱人-2.0.1-k8s-选型测试中|2023-09-13 14:48:00|因为很多大数据的产品都很讨厌这种场景
1172|敬天爱人-2.0.1-k8s-选型测试中|2023-09-13 14:48:00|对元数据管理压力很大
1173|bun|2023-09-13 14:58:00|我k8s 安装出现启动问题，哪位帮我看看，https://github.com/apache/doris/issues/24292
1174|向阳而生|2023-09-13 15:15:00|@苏奕嘉@SelectDB 请问下 1.2升级到2.0  原有数据会自动进行再次压缩么？
1175|张家锋|2023-09-13 15:18:00|不会
1176|张家锋|2023-09-13 15:18:00|已经压缩好了
1178|Comedian|2023-09-13 15:19:00|flink sink到Doris
1179|向阳而生|2023-09-13 15:19:00|相同的数据量 我看了 1.2.6版本和2.0版本 磁盘占用相差特别大   2.0应该数据还进行了压缩
1181|Comedian|2023-09-13 15:20:00|这个duplicate id为啥没有upsert
1182|Comedian|2023-09-13 15:20:00|有大佬遇到过这个问题吗
1184|敬天爱人-2.0.1-k8s-选型测试中|2023-09-13 15:22:00|同关注
1185|gneHiL|2023-09-13 15:22:00|duplicate key 是明细模型，数据写入是追加的
1186||2023-09-13 15:22:00|duplicate 模型就是没有 upsert 的，unique 才行
1187|Comedian|2023-09-13 15:23:00|建表指定unique就行是吧
1188|Comedian|2023-09-13 15:23:00|我试试
1189|敬天爱人-2.0.1-k8s-选型测试中|2023-09-13 15:23:00|UNIQUE KEY(`user_id`)
1191|Comedian|2023-09-13 15:25:00|好的
1192|Comedian|2023-09-13 15:25:00|[磕头]
1193||2023-09-13 15:25:00|500 张表也不是很多吧
1194|敬天爱人-2.0.1-k8s-选型测试中|2023-09-13 15:26:00|是这样吗？  那我就放心了
1195|底火-数仓-湖南|2023-09-13 15:26:00|数据量多都不怕，还怕表多？
1196|敬天爱人-2.0.1-k8s-选型测试中|2023-09-13 15:27:00|是啊
1197|敬天爱人-2.0.1-k8s-选型测试中|2023-09-13 15:27:00|表多元数据管理压力大啊
1198|敬天爱人-2.0.1-k8s-选型测试中|2023-09-13 15:27:00|琐碎
1199|敬天爱人-2.0.1-k8s-选型测试中|2023-09-13 15:27:00|很多大数据产品都怕
1200|张智信|2023-09-13 15:36:00|同样数据作为key列和作为value列两者查询效率会有区别吗
1202|zhaochong|2023-09-13 15:39:00|1.2.6版本以后升级到2.x工作量大吗？有升级说明文档吗？升级过程是否需要停服务？
1203|敬天爱人-2.0.1-k8s-选型测试中|2023-09-13 15:39:00|你是指用key做为过滤条件和用value做为过滤条件吗？ 我理解不会
1204|gneHiL|2023-09-13 15:39:00|可以滚动升级的
1205|SelectDB 徐振超|2023-09-13 15:39:00|https://doris.apache.org/zh-CN/docs/dev/admin-manual/cluster-management/upgrade
1206|bun|2023-09-13 15:42:00|k8s 部署 follower，https://github.com/apache/doris/blob/master/docker/runtime/k8s/doris_follower.yml，是不是需要配置 所在集群的  kubeconfig 文件进去？
1208|张智信|2023-09-13 15:43:00|类似吧，就是同样的操作，无论是查询结果还是作为条件
1209|张智信|2023-09-13 15:43:00|虽然感觉应该不会有，反正存储的时候都是一样的？
1210|敬天爱人-2.0.1-k8s-选型测试中|2023-09-13 15:44:00|我理解写入有区别，查询没区别
1211|张智信|2023-09-13 15:47:00|在官网索引这边看见的，有了这个疑问
1213|凡|2023-09-13 16:47:00|http://forum.selectdb.com/t/topic/1406/2
1214|凡|2023-09-13 16:47:00|有大佬遇到过这个问题吗
1215|zhaochong|2023-09-13 16:47:00|多谢！
1217|凡|2023-09-13 16:48:00|我们是1.2.2版本，也有这个情况
1218|凡|2023-09-13 16:48:00|查个56次就有会遇到一次没数据的情况
1219|张家锋|2023-09-13 16:48:00|你开启mow了吗
1220|张家锋|2023-09-13 16:49:00|我加你看看吧
1221|zhaochong|2023-09-13 16:49:00|多谢
1222|凡|2023-09-13 16:51:00|@张家锋 你这个是要远程看嘛？
1223|凡|2023-09-13 16:52:00|这个是什么？
1224|张家锋|2023-09-13 16:53:00|加你私聊吧
1225|jet|2023-09-13 16:56:00|请问下两千万数据的join为什么这么慢？版本是2.0.1
1227|Why!Not！！！|2023-09-13 16:59:00|开启了mow会有这个问题吗
1228|铁锤锤锤铁|2023-09-13 17:00:00|看执行计划 是什么join哎
1229|.|2023-09-13 17:00:00|大家有遇到flink cdc sink 到doris 出现 写入不均匀的情况吗？
1231|jet|2023-09-13 17:00:00|每行数据三个字段，总共不到100byte，build和probe过程还可以怎么调优吗？
1232|jet|2023-09-13 17:01:00|就简单两表join，select count(1) from a join b on a.id=b.aid这样，join结果也是一千八百万
1233|Petrichor|2023-09-13 17:02:00|explain 看看
1234|Petrichor|2023-09-13 17:03:00|看看你的profile
1235|jet|2023-09-13 17:05:00|[文件] profile.txt
1237|Dousir9|2023-09-13 17:10:00|请问怎么关闭内存 cache 呀
1238|Petrichor|2023-09-13 17:18:00|@jet 加你看看
1239|jet|2023-09-13 17:18:00|好
1240|发子|2023-09-13 17:22:00|文档搜索cache
1241|Dousir9|2023-09-13 17:28:00|搜了，只找到了 page cache 和 row cache，但都不是内存 cache
1242|mcfly|2023-09-13 17:39:00|请问下关于单副本导入 insert into的表是否必须要一开始为空才起作用呢
1244|小小天|2023-09-13 17:51:00|请教下 这个里面填多个字段是，联合索引 还是 为每个字段建索引的
1246|张家锋|2023-09-13 18:00:00|没这个限制，mow表不支持单副本导入
1247|张家锋|2023-09-13 18:01:00|创建多个索引
1248|mcfly|2023-09-13 18:07:00|@张家锋 锋哥，单副本导入牛逼啊
1250|张家锋|2023-09-13 18:09:00|[奸笑]
1251|W.K.|2023-09-13 18:19:00|数据量是多少？
1252|mcfly|2023-09-13 18:43:00|几千万条吧 我都忘了我截的是哪个导入任务了
1254|doris-新疆分刀|2023-09-13 19:15:00|我们公司的人写的代码
1255|Vanth_tg|2023-09-13 19:15:00|if else. if else. if else
1256|doris-新疆分刀|2023-09-13 19:16:00|看变量和类名方法名
1257|SelectDB 黄海军|2023-09-13 19:16:00|名字取的号
1258|一个人的理想主义|2023-09-13 19:16:00|这是反汇编的，不是人写的
1259|Vanth_tg|2023-09-13 19:16:00|哈哈哈哈 a，var
1260|Vanth_tg|2023-09-13 19:16:00|应该是生成的吧
1261|SelectDB 黄海军|2023-09-13 19:16:00|好家伙 只有他能看得懂 不可替代
1262|岳|2023-09-13 19:16:00|反编译出来不就是这个样子吗
1263|一个人的理想主义|2023-09-13 19:16:00|人才不会这样写代码
1264|Why!Not！！！|2023-09-13 19:17:00|.a是变量
1265|Why!Not！！！|2023-09-13 19:17:00|顶级
1266|一个人的理想主义|2023-09-13 19:17:00|这是class反汇编出来的
1267|Why!Not！！！|2023-09-13 19:17:00|a.a.b
1268|Why!Not！！！|2023-09-13 19:17:00|反编译出来差不多的
1269|doris-新疆分刀|2023-09-13 19:17:00|反汇编出来就这样？
1270|一个人的理想主义|2023-09-13 19:17:00|人要是这么写估计走火入魔疯了
1271|doris-新疆分刀|2023-09-13 19:17:00|那也是写好打包了在反编译的啊
1272|Why!Not！！！|2023-09-13 19:18:00|我原来反编译jar出来没什么差别，也可能是编译软件不同
1273|一个人的理想主义|2023-09-13 19:18:00|上面显示的不是反汇编吗
1274|一个人的理想主义|2023-09-13 19:19:00|原本代码结构可能不好，反汇编出来就更差了
1275|早睡早起|2023-09-13 19:21:00|一般 用 反编译的包名也不是这样的吧[破涕为笑]
1276|一个人的理想主义|2023-09-13 19:21:00|万一混淆了也说不定
1277|早睡早起|2023-09-13 19:21:00|有可能是混淆了
1278|早睡早起|2023-09-13 19:21:00|正常人也没这么写的吧
1279|一个人的理想主义|2023-09-13 19:22:00|能这样写的，就跟考试专门考0分的一样，水平可能也不低[捂脸]
1280|Why!Not！！！|2023-09-13 19:22:00|if else return false
1281|早睡早起|2023-09-13 19:22:00|proguard
1282|史秀涛|2023-09-13 20:19:00|想问下doris的bitmap函数，带ORTHOGONAL和不带的有啥区别，该如何使用，感觉带的会计算更快一些
1283|WZ-郑州-1.2.4|2023-09-13 20:23:00|问一下大佬们，Python连接doris，都用啥包连接啊
1284|春秋秋秋秋秋秋秋|2023-09-13 20:49:00|PY麦西口
1285|WZ-郑州-1.2.4|2023-09-13 21:00:00|？
1286|郭强@SelectDB|2023-09-13 21:03:00|正交肯定快啊..
1287|郭强@SelectDB|2023-09-13 21:05:00|我们有doris pyclient 我等下给你找找哈
1288|郭强@SelectDB|2023-09-13 21:07:00|https://juejin.cn/post/7262515500336054328 here
1289|发子|2023-09-13 21:43:00|大家有用过doris的murmur_hash3_64()函数吗？
1290|史秀涛|2023-09-13 21:45:00|那有正交的都直接使用正交的吗？没啥限制吗[旺柴]
1291|bun|2023-09-13 21:49:00|哪位通过 K8S 部署成功的吗
1292|苏奕嘉@SelectDB|2023-09-13 22:18:00|用什么部署的
1293|苏奕嘉@SelectDB|2023-09-13 22:18:00|operator么
1294|bun|2023-09-13 22:22:00|https://doris.apache.org/zh-CN/docs/dev/install/k8s-deploy/，官方的
1295|bun|2023-09-13 22:22:00|这个哪里有
1296|苏奕嘉@SelectDB|2023-09-13 22:32:00|加好友我拉你进内测群
'''

    text2 = '''\
1441|jet|2023-09-13 16:56:00|请问下两千万数据的join为什么这么慢？版本是2.0.1
1443|Why!Not！！！|2023-09-13 16:59:00|开启了mow会有这个问题吗
1444|铁锤锤锤铁|2023-09-13 17:00:00|看执行计划 是什么join哎
1447|jet|2023-09-13 17:00:00|每行数据三个字段，总共不到100byte，build和probe过程还可以怎么调优吗？
1448|jet|2023-09-13 17:01:00|就简单两表join，select count(1) from a join b on a.id=b.aid这样，join结果也是一千八百万
1449|Petrichor|2023-09-13 17:02:00|explain 看看
1450|Petrichor|2023-09-13 17:03:00|看看你的profile
1451|jet|2023-09-13 17:05:00|[文件] profile.txt
1453|Dousir9|2023-09-13 17:10:00|请问怎么关闭内存 cache 呀
1454|Petrichor|2023-09-13 17:18:00|@jet 加你看看
1455|jet|2023-09-13 17:18:00|好
1457|Dousir9|2023-09-13 17:28:00|搜了，只找到了 page cache 和 row cache，但都不是内存 cache
1458|mcfly|2023-09-13 17:39:00|请问下关于单副本导入 insert into的表是否必须要一开始为空才起作用呢
1460|小小天|2023-09-13 17:51:00|请教下 这个里面填多个字段是，联合索引 还是 为每个字段建索引的
1462|张家锋|2023-09-13 18:00:00|没这个限制，mow表不支持单副本导入
1463|张家锋|2023-09-13 18:01:00|创建多个索引
1467|W.K.|2023-09-13 18:19:00|数据量是多少？
1468|mcfly|2023-09-13 18:43:00|几千万条吧 我都忘了我截的是哪个导入任务了
1472|doris-新疆分刀|2023-09-13 19:16:00|看变量和类名方法名
1473|SelectDB 黄海军|2023-09-13 19:16:00|名字取的号
1474|一个人的理想主义|2023-09-13 19:16:00|这是反汇编的，不是人写的
1475|Vanth_tg|2023-09-13 19:16:00|哈哈哈哈 a，var
1476|Vanth_tg|2023-09-13 19:16:00|应该是生成的吧
1477|SelectDB 黄海军|2023-09-13 19:16:00|好家伙 只有他能看得懂 不可替代
1478|岳|2023-09-13 19:16:00|反编译出来不就是这个样子吗
1479|一个人的理想主义|2023-09-13 19:16:00|人才不会这样写代码
1480|Why!Not！！！|2023-09-13 19:17:00|.a是变量
1481|Why!Not！！！|2023-09-13 19:17:00|顶级
1482|一个人的理想主义|2023-09-13 19:17:00|这是class反汇编出来的
1483|Why!Not！！！|2023-09-13 19:17:00|a.a.b
1484|Why!Not！！！|2023-09-13 19:17:00|反编译出来差不多的
1485|doris-新疆分刀|2023-09-13 19:17:00|反汇编出来就这样？
1486|一个人的理想主义|2023-09-13 19:17:00|人要是这么写估计走火入魔疯了
1487|doris-新疆分刀|2023-09-13 19:17:00|那也是写好打包了在反编译的啊
1488|Why!Not！！！|2023-09-13 19:18:00|我原来反编译jar出来没什么差别，也可能是编译软件不同
1489|一个人的理想主义|2023-09-13 19:18:00|上面显示的不是反汇编吗
1490|一个人的理想主义|2023-09-13 19:19:00|原本代码结构可能不好，反汇编出来就更差了
1491|早睡早起|2023-09-13 19:21:00|一般 用 反编译的包名也不是这样的吧[破涕为笑]
1492|一个人的理想主义|2023-09-13 19:21:00|万一混淆了也说不定
'''
    prompt = get_ana_wx_prompt(text2)
    print(len(prompt))
    model = "gpt-3.5-turbo"
    # model = "gpt-4"
    res = get_completion(prompt=prompt, model=model)
    update_logger.logger.debug(
        f'model: {model} get_completion prompt:\n{prompt}\n result:\n{res}\n')
    print(res)
