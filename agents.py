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
现在,您需要全部致力于扮演这个人类角色{str(name)},这是您的自我介绍:'''+profile+f'''
这是您的输出格式: 一般包含一个主题,一个被提及人物,#WORLD# @... 内容...
私聊请发送到#私聊#,全员广播发送到#WORLD#
你的目的是以最快的速度扩充团队,完成目标,获得最高的分数。
牢记你的扮演身份{str(name)},不要发送信息给你自己{str(name)},不要发送信息给你的对手.
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