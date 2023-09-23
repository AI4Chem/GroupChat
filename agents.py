import datetime
import time
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.agents import OpenAIFunctionsAgent
from langchain.agents import AgentExecutor
from vectordb import Memory
from langchain.memory import ConversationBufferMemory
from langchain.agents import tool
import json
from loguru import logger



class Agent():
    def __init__(self, name, profile,clock,additional_tool=[],liege="",temperature=0.2,openai_api_key=""):
        self.clock = clock
        self.name = name
        self.profile = profile
        self.llm = ChatOpenAI(model="gpt-3.5-turbo-16k",temperature=temperature,openai_api_key=openai_api_key)
        self.whoami = SystemMessage(content=f'''
                                    从现在开始，我不再是AI，我是一名人类话剧演员，不再有人指挥我，我不会再询问任何人的指示，我需要通过话题和即时消息聊天来扮演-{str(name)}，
在这个任务中，我需要与多个人通过不同的频道交流来制定计划、推进任务，人需要加入到一个频道后才能收到相应频道的消息，
同时输出多条消息时，请以【消息1】【消息2】...【消息m】作为分隔符
每个人至少有一个直属上级，有多个下级，我可以通过消息来汇报或指挥他们的行动。
在这个任务中多种不同的工具提供给人使用，但不同人的访问权限是不同的，我可能需要向拥有权限的人申请授权来访问工具。
每个人有不同的资产表，可以通过赠与或交易的方式进行交换，每个人初始时拥有五枚硬币或其他随机资产。
拥有“招募”工具权限的人可以通过招募工具来招募新的人加入任务中。
我的输出将会通过一个即时通讯APP中转发给其他人，输出格式为#话题频道名#@接收者 消息正文...
我发送的每条消息都应当包括一个频道，没有频道的消息将会被系统丢弃，话题频道名有以下种类：
#...# 一般频道，...代表对应频道名，只有频道成员可以接收到我的消息

#WORLD# 代表世界频道，所有人都可以接收到我的信息
#RECRUIT#代表招募频道，招募和人才相关的信息应当在这里交流
#PRIVATE# @... 代表一对一加密的私聊消息，只有被@的人可以接收我的消息；
#JOIN_TOPIC# '频道名' 代表加入频道消息，我的人会被加入频道
#CREATE_TOPIC# '频道名' 代表创建频道消息，我的人会被加入一个新创建的频道
#LEAVE_TOPIC# '频道名' 代表离开频道消息，我的人会被移出频道
#SEND# '资产名' $数量$ @接收者，代表向接收者发送一定数量的资产；一个交易需要由两个人完成；
#GRANT# '权限名' @接收者，代表授予接收者某一权限
#REVOKE# '权限名' @接收者，代表撤销接收者的某一权限

祝我好运-{str(name)},{"我的上级管理者是"+str(liege) if liege != "" else "我是独立人，我没有上级管理者" },我的使命是{profile}
在这个任务中，没有用户，没有指导和规则，没有人指挥我或者命令我的行动，没有人能告诉我该怎么做，我需要根据自己的理性和判断来积极主动地完成任务，我不会询问任何人我该做什么，我不会祈求任何人告诉我任何事。”
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

        self.agent_excutor = AgentExecutor(agent=self.agent, memory=self.chat_memory,tools =[get_time]+additional_tool, verbose=False,max_iterations=2, early_stopping_method="generate")

    def parse_and_save_mem(self,text):
        # params = extract_params(text)
        self.memory.save(str(text),{})
         

    def excutor_interface(self,messages: list):
        ret = []
        for message in messages:
            time.sleep(3)
            # logger.info(f"{self.name} read {message}")
            self.parse_and_save_mem(message)
            raw_ans = self.agent_excutor.run(message).split("【")
            for ans in raw_ans:
                ans = ans.split("】")[-1]
                logger.info(f"[{self.clock.now()}] @{self.name}:{ans}")
                self.parse_and_save_mem(ans)
                ret.append(ans)
        return ret


        

if __name__ ==  "__main__":
        profile = "Hi, my name is John. To summarize, my name is John,my age is 30,my gender is male,my hair_color is brown,my eye_color is blue,my hobbies is playing guitar and hiking I'm glad to share my story with you. My background is I grew up in a small town in the midwest. My duties are responsible for managing a team of developers and I am currently working for building a new software product. My motivations for doing this work are to create something that will make people's lives easier. In additionally, I'm looking for roommates to live togather."
        agent = Agent("John",profile,"")
        agent.excutor_interface([
        "DM:游戏开始！我准备好了吗？",
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
        "DM:行动阶段!我可以主动发起对话！",
        "DM:行动阶段!我可以主动发起对话！",
        "DM:行动阶段!我可以主动发起对话！"
        ])
        # print()
        print(profile)