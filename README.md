
# GroupChat

GroupChat是一个通过话题-即时消息驱动的多AI智能体模拟人类企业式团队协作和社交的研究项目。

## 项目结构

- agents/: 实现EmployeeAgent和CustomerAgent等各种智能体类
- assets/: 实现資产和交易系统
- memory/: 实现个体智能体的私有记忆
- messages/: 消息类型定义
- topics/: 实现各种讨论主题类
- hub/: 消息路由器
- app.py: 主应用逻辑
- base.py: 序列化基类
- main.py: 程序入口
- utils.py: 工具函数

## 运行流程

1. 主程序初始化系统
2. 创建根用户和根讨论组
3. 根用户添加员工角色的智能体
4. 员工之间以及与客户进行讨论和互动
5. 智能体具有私有记忆,可以持续学习和回忆

## 核心功能

- 多智能体之间的自然语言交互
- 在不同讨论组(Topic)中的交流
- 基于记忆的智能体个性化
- 资产交易和任务协作
- 用户角色、讨论组的权限管理

## 依赖环境

- Python 3.6+
- Gradio
- LangChain

欢迎提出宝贵意见,我们会持续改进这个虚拟智能体社区,进行多智能体协作和社交的研究!
