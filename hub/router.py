class MessageRouter:

    def __init__(self):
        self.agents = {}
        self.topics = {}

    def register(self, agent):
        self.agents[agent.name] = agent

    def route(self, message):
        # 按照主题,接收者等进行消息路由
        pass

    def broadcast(self, message, topic):
        # 将消息广播给主题内所有成员
        pass