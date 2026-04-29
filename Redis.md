# Redis(Remote dictionary server)
# 一、简介
Redis 是一款开源、高性能、基于内存的键值（Key-Value）数据库，最主流的**分布式**缓存中间件。
- 数据存储在内存
- 也支持持久化存储在硬盘

# 二、相关基础概念
## 1、集群和分布式
- 集群就是一群具备**相同技能**的人共同完成任务。
- 分布式就是将任务分为不同的模块，每一个模块由对应的人完成。
- 二者可以结合，分布式的每个人都可以是一个集群。

## 支持的数据类型
### 1、基本数据类型
- String
- Hash
- List
- set
- 有序集合

### 2、高级数据类型
- Stream消息队列  
- Geospatial地理空间 
- Hyperloglog
- Bitmap位图
- Bitfield位域

# 三、安装
## 1、安装
```
# Linux/mac
brew install redis

# Windows

```

