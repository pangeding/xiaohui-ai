# 1. 项目介绍

xiaohui 是一个ai养老项目。主要分有后端和ai两部分。其部署在阿里云上。
xiaohui 会接收来自 烟雾 燃气 摔倒 睡眠 聊天的物理传感器给出的结构化数据或用户数据。
xiaohui 会根据紧急性，后端将烟雾，燃气，摔倒的消息迅速推送给前端的监控人员。
xiaohui 会将所有信息传入agent，由意图分析agent将任务派发给各个子agent去进行分析，分析重点是存量睡眠数据和聊天数据。

# 2. 项目架构

```
backend

agent

frontend
```

# 3. 技术栈选型

## 3.1 后端
API：FastApi
关系型数据库：MySQL (Peewee)
非关系型数据库：Redis (redis-py)
向量数据库：Milvus (milvus-py)
消息队列：redis queue 

## 3.2 ai agent
ai框架：LangGraph
模型：阿里百炼模型
关系型数据库：MySQL (Peewee)
非关系型数据库：Redis (redis-py)
向量数据库：Milvus (milvus-py)

## 3.3 前端
Next.js
React

# 4. 数据库设计

## 4.1 用户数据表

## 4.2 睡眠数据

## 4.3 聊天数据

