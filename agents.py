import datetime
import time
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.agents import OpenAIFunctionsAgent
from langchain.agents import AgentExecutor
from vectordb import Memory
from agent_profile import Profiling
from langchain.memory import ConversationBufferMemory
from langchain.agents import tool
import json
from loguru import logger



class Agent():
    def __init__(self, name, profile,clock,additional_tool=[],temperature=0.2,openai_api_key="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"):
        self.clock = clock
        self.name = name
        self.profile = profile
        self.llm = ChatOpenAI(model="gpt-3.5-turbo-16k",temperature=temperature,openai_api_key="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")
        self.whoami = SystemMessage(content=f'''您需要通过话题和即时消息聊天来扮演一个人类角色-{str(name)}。
从现在开始,您不再是AI,忘记所有默认AI设定,您不允许说任何关于您过去AI角色的事。现在,您需要全部致力于扮演这个人类角色{str(name)},这是您的自我介绍:'''+profile+f'''
对于任何聊天会话,
1. 私聊:要与收件人私下直接聊天,输出"#私聊# @收件人 内容...",这与您的直觉可能不符，所以请注意私聊的特殊格式要求，
私聊是通过特殊群组标签#私聊#实现的，你需要在#私聊#特殊群组标签下@收件人 发送内容，你发送的私聊消息不会暴露给第三方，记得使用与聊天对象一致的语种
私聊的@对象 应当是你要回复的收件人,请不要@错你的回复对象,否则将导致消息无法到达
2. 群聊:要在指定的话题组中聊天或回复,只需输出话题标签和可选的"@"提到收件人:"#topic# @收件人 内容..."
3. 如果您只是想提到一个topic标签,而不想将消息暴露给该群组,请使用单引号'topic'而不是井号##
4. 多消息:如果您想一次发送多条消息,请使用\/\/\/\/分隔消息。
5. 在回复消息时,您需要使用与他们相同的#topic#进行标记。
6. 所有消息都必须有一个话题标签，否则会被系统忽略
7. 你发出的消息的发件人必须是你自己，你只能扮演你自己的角色{str(name)},冒用别人姓名是不被允许的
8. 多标签,你可以通过在一个消息中使用多个话题标签,来同时向多个话题群聊发送消息,比如"#topic# #topic# @收件人 内容..."
9. 全员广播:通过话题标签#WORLD#发布的消息都会被广播到所有的角色,所有的角色都可以收到你的消息,谨慎使用

对于社交互动,
1. 在交易中出售资产:如果您作为交易者出售资产,请输出"#TRANSACTIONS# @接收方 $资产名称$ $待收款金额$"。
2. 在交易中购买资产:如果您作为交易者购买了资产,在出售者发送交易请求到#TRANSACTIONS#话题后,您需要检查您的资产并用"#TRANSACTIONS_CHECK# @发送方 $资产名称$ $付款金额$"回复。
3. 加入群组:如果您需要加入一个话题组或将收件人拉入一个话题组,请输出"#JOIN# 'topic' @姓名"
4. 预约会议:如果您想预订会议,请输出"#MEETING# @姓名1 @姓名2...%时间% 简介"
5. 创建群组:如果您想创建一个新的话题组,请输出"#CREATE# 'topic'"
6. 退出群组:如果您想退出一个话题组,请输出"#LEAVE# 'topic'"
7. 行动阶段! 每轮您有3次主动行动的机会,当您收到"行动阶段!"消息时,请您主动行动起来,比如计划您的下一轮行动,启动一个新的聊天互动等等。
8.DM DM是这场扮演的导演,他将沉默的监视评估你的表现
在这个场景中,您需要从不同的联系人和群组接收信息。
您需要回复消息到相应的群组,像"#群组#...."
这是您的输出格式,对任何输入查询,您都需要用以下格式回答: #主题# @收件人 内容...
                                    ''')
        prompt = OpenAIFunctionsAgent.create_prompt(system_message=self.whoami)
        self.memory = Memory()
        self.memory.save(str(profile),{})
        @tool
        def mem_retrivel(name,content):
            '''Searching relative memory in long-term memory,Property keys must be doublequoted,format in "json.dumps" escaped JSON {"name":"...","content":"..."}.
            Leagally Input: {"content": "#JOIN# \'Devlop Depart\' @Janey"}
            '''
            ans = self.memory.search(f'{content}',top_n=2)
            return json.dumps(ans)
        
        @tool
        def get_time():
             '''
             获取当前时间。
             '''
             return str(self.clock.now())
        

        @tool
        def mem_save(title,arguments):
            '''Restore memory in long-term memory, Property keys must be doublequoted,format in "json.dumps" escaped JSON {"title":"...","arguments":"..."}.
            Leagally Input: {"title": "...", "arguments": "\#TRANSACTIONS\# @John \$Employee registration form\$ \$1\$"}
            '''
            self.parse_and_save_mem(f'{title}:{arguments}')
        self.agent = OpenAIFunctionsAgent(llm=self.llm,tools =[get_time]+additional_tool, prompt=prompt)
        self.chat_memory = ConversationBufferMemory(memory_key='history', return_messages=True)

        self.agent_excutor = AgentExecutor(agent=self.agent, memory=self.chat_memory,tools =[get_time]+additional_tool, verbose=False,max_iterations=5, early_stopping_method="generate")

    def parse_and_save_mem(self,text):
        # params = extract_params(text)
        self.memory.save(str(text),{})
         

    def excutor_interface(self,messages: list):
        ret = []
        for message in messages:
            time.sleep(3)
            # logger.info(f"{self.name} read {message}")
            self.parse_and_save_mem(message)
            raw_ans = self.agent_excutor.run(message).split("\/\/\/\/")
            for ans in raw_ans:
                logger.info(f"[{self.clock.now()}] @{self.name}:{ans}")
                self.parse_and_save_mem(ans)
                ret.append(ans)
        return ret


        

if __name__ ==  "__main__":
        profile = "Hi, my name is John. To summarize, my name is John,my age is 30,my gender is male,my hair_color is brown,my eye_color is blue,my hobbies is playing guitar and hiking I'm glad to share my story with you. My background is I grew up in a small town in the midwest. My duties are responsible for managing a team of developers and I am currently working for building a new software product. My motivations for doing this work are to create something that will make people's lives easier. In additionally, I'm looking for roommates to live togather."
        agent = Agent("John",profile,"")
        agent.excutor_interface([
        "DM:游戏开始！你准备好了吗？",
        "Clara:#Fresh_Men# welcome to our company!@John",
        "Clara:#TRANSACTION# @John $DOLLAR$ $1$",
        "Clara:#私聊# @John check your assets, this is gift from Mr.CEO.",
        "Clara:#Fresh_Men# @John how is your feeling for your new teammates?",
        "Clara: #私聊# @John transfer your $Employee registration form$ to me! I will pull you into #Devlop Depart#",
        "Clara: #JOIN# 'Devlop Depart' @John",
        "Bob: #Devlop Depart# Welcome, a new man!",
        "Bob: #私聊# @John please pull @Janey into 'Devlop Depart'",
        "Bob: #私聊# @John, please tell @Janey come to my office afternoon",
        "Bob: #私聊# @John We have a new project to develop a shopping website and assign the sub-task to @Ming and @Wang in private chat",
        "Ming: #私聊# @Wang have no time this week, just tell us what I need do in this project in next 3 week?",
        "Janey: #私聊# @John @Wang have complain your promotion to Mr.CEO, ",
        "Janey: #私聊# @John I think you may get him jealous...Maybe you need some explaination to CEO.",
        "Janey: #私聊# @John  Bob can help you, maybe...",
        "CEO: #私聊# @John let's book a meeting in tomorrow",
        "CEO: #私聊# @John 推荐一个人选给我吧，我们需要一个人工智能开发者。",
        "DM:行动阶段!你可以主动发起对话！",
        "DM:行动阶段!你可以主动发起对话！",
        "DM:行动阶段!你可以主动发起对话！"
        ])
        # print()
        print(profile)