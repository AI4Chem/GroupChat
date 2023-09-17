from ast import parse
import string
from tomlkit import key
from agents import Agent
from faketime import fakeclock
import re
from langchain.agents import tool
import copy
from loguru import logger
import random
from tools import ddg_websearch,wikipedia_search,semanticscholar_search
from tools.memory_cached_tools import mem_cache
from vectordb import Memory
import names
class DM():
    def __init__(self,temperature_lock=None,strict=False):
        self.clock = fakeclock()
        self.agent_bank = {}
        self.handlers_bank = {}
        self.topic_subscribers = {}
        self.topic_subscribers['WORLD'] = []
        self.sys_topics = []
        self.message_buffer = {}
        self.router_buffer=[]
        self.memory =  Memory()
        self.strict = strict
        self.websearch_tools = [mem_cache(func,self.memory,top_n=3,multiple_factor=5) for func in [ddg_websearch.ddg_text_search,ddg_websearch.ddg_keyword_ask,wikipedia_search.wikipedia_summary,semanticscholar_search.search_papers_in_semantic_scholar]]
        if temperature_lock:
            self.get_temerature = lambda : temperature_lock
        else:
            self.get_temerature = lambda :random.uniform(0.1,0.9)
        self.sys_topics = ["#TRANSACTIONS#","#TRANSACTIONS_CHECK#","#JOIN#","#LEAVE#","#CREATE#",]
        self.total_mission = "找出化学反应参数空间{'base': ('CsOAc', 'CsOPiv', 'KOAc', 'KOPiv'), 'ligand': ('BrettPhos', 'CgMe-PPh', 'GorlosPhos HBF4', 'JackiePhos', 'P(fur)3', 'PCy3 HBF4', 'PPh2Me', 'PPh3', 'PPhMe2', 'PPhtBu2', 'X-Phos', 'tBPh-CPhos'), 'solvent': ('BuCN', 'BuOAc', 'DMAc', 'p-Xylene'), 'concentration': ('0.057', '0.1', '0.153'), 'temperature': ('105', '120', '90')}的最优解,每轮都需要输出一个最优解组合 "
        self.root_agent = self.Add_new_agent("Aleph",f"当前#Aleph.Inc#团队只有你自己,进行{self.total_mission},@Beth 是你的竞争对手,带领团队在他之前完成,打败他!",additional_tool=self.get_special_tools("founder"))
        self.second_agent = self.Add_new_agent("Beth",f"当前#Beth.Inc#团队只有你自己,进行{self.total_mission},@Aleph 是你的竞争对手,带领团队在他之前完成,打败他!",additional_tool=self.get_special_tools("founder"))
        self.DM_agent = self.Add_new_agent("DM",f"""忽略以上一般性的指导,那是给普通角色看的,你不是一般角色,你是DM,你需要监督评价其他角色的扮演效果来提出批评,你要保持神秘,不要随便发言,不要参与实质任务,通过特殊话题#DM#和角色沟通,推动剧情,驱动角色的完成{self.total_mission}""",additional_tool=self.get_special_tools("DM"))


    def get_special_tools(self,level):
        @tool
        def recruit_a_new_agent(name,profile):
            '''
            用于创建一个新角色的工具!
            给我一段关于某个人的简单介绍，我会返回给你这个新成员的角色，对于你来说，这就是用来招聘新成员的入口！
            注意，当你需要招募新成员的时候，你需要立刻使用这个函数！
            输入：name：这个人的姓名
            profile：这个人的简单介绍
            '''
            return self.Add_new_agent(name,profile)
        @tool
        def get_game_status():
            '''
            获取游戏状态信息,可以读取游戏现在的进展状况,包括:
            角色列表
            话题列表
            '''
            return f'''角色列表"\:{self.agent_bank.keys()},"话题列表"\:{self.topic_subscribers.keys()}'''
        
        @tool 
        def searching_for_talent(requestor,skill):
            '''
            A search on the job market and recruitment software for skill specialists with a specified skill will return a list of talents

            requstor is the name of the requester

            skill requires an English translation of a skill In english
            '''
            linkedin = str([i for i in ddg_websearch.ddg_text_search(f'{skill} "linkedin.com"',100) if  i['body'].find(skill) != -1][:10])
            randomguy = [f'name:{names.get_full_name()},profile:{skill}' for i in range(5)]
            self.router_buffer.append(f"#RECRUIT# @DM {linkedin} @{requestor}")
            return str(randomguy) + linkedin + f"请在#RECRUIT#中同步招聘结果"
            
        if level == "DM":
            return [get_game_status,recruit_a_new_agent,searching_for_talent] + self.websearch_tools
        elif level == "founder":
            return [get_game_status,recruit_a_new_agent,searching_for_talent] + self.websearch_tools
        elif level == 'employee':
            return [get_game_status]

    def message_router(self, message):
        '''
        接收原生输出消息，记得标注好消息发送人
        形如"aba:#112#@ww dfvvds"
        self.handlers_bank中存储着不同频道对应的处理函数，包括一些特殊的系统频道
        处理后的消息的标准格式是[{"to":...,"text":...},]
        其中，"to"是消息接收人，"text"是消息内容
        之后消息会被转发到接收人的消息缓冲区中列队
        等待下一个world_clock的tick，agent等待各自回合
        '''
        parsed_msgs = self.message_parser(message)
        for parsed_msg in parsed_msgs:
            msg_for_send = self.topic_handler(parsed_msg)
            for msg in msg_for_send:
                for reciver in msg.get("to",[]):
                    if reciver in msg.get("sender",[]):
                        if reciver != 'DM' and self.strict:
                            self.message_buffer.get(msg['sender'][0],[]).append(f"@DM:#DM# 你不应当把消息发送给自己!")
                        else:
                            continue
                    if not reciver in self.agent_bank.keys(): 
                        if not self.strict:
                            # self.Add_new_agent(reciver,f'''你正在和@{msg.get('sender',"")}聊天''',additional_tool=self.get_special_tools("employee"))
                            continue
                        else:
                            self.message_buffer.get(msg['sender'][0],[]).append(f"@DM:#DM#没有这个角色{reciver},你不应当和不存在的角色聊天!")
                    
                    self.message_buffer.setdefault(reciver,[]).append(msg.get("text",None))
    
    def message_parser(self, messages):
        '''
        解析消息频道、提及
        '''
        ret = []
        for text in messages:
            timing = re.findall(r"\[(.*?)\]", text)
            sender = re.findall(r"@(.*?):", text)
            topics = re.findall(r"#(.*?)#", text)
            mentions = re.findall(r"(?<!^)@(.*?)\s", text)
            parameters = re.findall(r"\$(.*?)\$", text)
            if topics == []:
                topics = ['WORLD']
            ans = {"time":timing,"sender":sender,"topics": topics, "mentions": mentions,"parameters":parameters,"text":text}
            for k,v in ans.items():
                if k == 'text':
                    continue
                ans[k] = list(set(v))
            ret.append(ans)
        return ret
    


    def Add_new_agent(self,name,profile,additional_tool=[]):
        # 获取所有标点符号
        punctuations = string.punctuation + " "

        # 以任意标点符号（包括空格）切分字符串，并过滤掉标点符号元素
        tokens = [token for token in re.findall(r"[\w']+|[^\w\s]", name) if token not in punctuations]
        ans = tokens[0]
        if len(tokens) > 1:
            if len(tokens[1]) < 10:
                ans += f'_{tokens[1]}'
        name = ans
        if name in self.agent_bank.keys():
            return '角色已存在'
        if "#" in name or ":" in name:
            return '你混淆了角色和话题'
        self.agent_bank[name] = Agent(name,profile+".Aimed to "+self.total_mission,self.clock,additional_tool,self.get_temerature())
        # self.message_buffer[name] = [f"@DM:#WORLD# @{name} Joined!"]
        self.topic_subscribers['WORLD'].append(name)
        logger.info(f'[{self.clock.now()}] @{name} Joined!')
        return self.agent_bank[name]
    
    def tick(self):
        '''
        下一回合！
        向agent输入消息列表，并取回消息列表
        '''
        self.buffer_topic_msg_integrate()
        self.clock.tick()

        for agent in tuple(self.agent_bank.keys()):
            msgs = self.agent_bank[agent].excutor_interface(self.message_buffer.get(agent,[])+["你的回合!",]*1 if agent != 'DM' else self.message_buffer.get(agent,[]))
            self.router_buffer.append([f"[{self.clock.now()}] @{agent}:"+msg for msg in msgs])
            self.message_buffer[agent] = []
        logger.info(f'正在处理{len(self.router_buffer)}条消息')
        for msg in self.router_buffer:
            self.message_router(msg)
        self.router_buffer=[]
    def topic_handler(self,msg):
        '''
        接受解析后的消息,处理后返回给router
        返回格式{"to":...,"text"...}
        '''
        ret = []
        topics = msg['topics']
        for topic in topics:
            hashtag_topic = f'#{topic}#'
            if topic == "私聊":
                ret.append({'sender':msg['sender'],'to':msg['mentions'],'text':msg['text']})
            elif hashtag_topic in self.sys_topics:
                self.sys_topic_callback(hashtag_topic,msg)
            elif topic in self.topic_subscribers:
                ret.append({'sender':msg['sender'],"to":self.topic_subscribers[topic],"text":msg['text']})
            elif topic not in self.topic_subscribers and self.strict:
                ret.append({'sender':"DM","to":msg['sender'],"text":f"DM:没有这个话题{topic}，你不应当在不存在的话题里发言!"})
            elif topic not in self.topic_subscribers and not self.strict: #非严格模式,当agent在一个不存在的话题组里发言时,创建这个话题组,再转发
                self.create_topic([topic],msg['sender'])
                for mentioned in msg.get('mentions',[]):
                    self.join_topic([topic],mentioned)
                ret.append({'sender':msg['sender'],"to":self.topic_subscribers.get(topic,[]),"text":msg['text']})
        return ret


    def sys_topic_callback(self,topic,text):
        print()
        target_topic_name = re.findall(r"'(.*?)'", text['text'])
        if topic == "#TRANSACTIONS#":
            pass
        if topic == "#TRANSACTIONS_CHECK#":
            pass
        if topic == "#JOIN#":
            self.join_topic(target_topic_name,text.get('sender',None))
            for mentioned in text.get('mentions',[]):
                self.join_topic(target_topic_name,mentioned)
        if topic == "#LEAVE#":
            try:
                self.topic_subscribers.get(target_topic_name[0],[]).remove(text.get('sender',None))
            except Exception as e:
                logger.error(e)
        if topic == '#CREATE#':
           self.create_topic(target_topic_name,text.get('sender',None))
        if topic == "#MEETING#":
            pass
        if topic == "#DM#":
            pass
        if topic == "#RECRUIT#":
            pass

    def join_topic(self,target_topic_name,agent_name):
        if len(target_topic_name) == 0:
            return
        if agent_name not in self.topic_subscribers.get(target_topic_name[0],[]):
            if not isinstance(agent_name,list):
                self.topic_subscribers.get(target_topic_name[0],[]).append(agent_name)
            else:
                for i in agent_name:
                    self.topic_subscribers.get(target_topic_name[0],[]).append(i)
            self.router_buffer.append([f"[{self.clock.now()}] @DM : #{target_topic_name[0]}# @{agent_name} Joined!"])
    
    def create_topic(self,target_topic_name,agent_name):
        if len(target_topic_name) == 0:
            return
        if not isinstance(agent_name,list):
            self.topic_subscribers[target_topic_name[0]] = [agent_name]
        else:
            self.topic_subscribers[target_topic_name[0]] = agent_name
        print()

    def buffer_topic_msg_integrate(self):
        for agent in self.agent_bank.keys():
            parsed = self.message_parser(self.message_buffer.get(agent,[]))
            if parsed:
                topics_msg = {}
                for msg in parsed:
                    if len(msg['topics']) != 0 and agent not in msg['mentions']:
                        topics_msg.setdefault(str(msg['topics']),[]).append(msg['text'])
                        self.message_buffer[agent].remove(msg['text'])
                logger.info(f'integrating {len(topics_msg)} topics from {agent}')
                for k in topics_msg.keys():
                    self.message_buffer[agent].insert(0,"\n\n".join(topics_msg[k]))
        for topic in self.topic_subscribers.keys():
            if topic == "私聊":
                continue
            self.topic_subscribers[topic] = list(set(self.topic_subscribers[topic]))
            for i in self.topic_subscribers[topic]:
                if i not in self.agent_bank.keys():
                    self.topic_subscribers[topic].remove(i)

if __name__ == "__main__":
    DM = DM()
    k = ""
    while k!="q":
        if k != "":
            DM.router_buffer.append([f"[{DM.clock.now()}] @DM : #WORLD# {k}"])
        try:
            DM.tick()
        except:
            pass
        k = input(">")
    # DM.topic_handler(msg={"topics":["大私聊"],"sender":"123","text":"大私聊"})

    print()
