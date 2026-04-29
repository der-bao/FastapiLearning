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
# mac
brew install redis

# Linux
sudo apt update		# 更新软件源
sudo apt install redis-server -y
redis-server --version	# 验证

# Windows
不建议
在wsl运行即可
```

# 四、相关指令
## 1、基本指令
```
# 登录
redis-cli --raw # 可以中文输出
```

## 2、字符串
```
# 1、设置数据
set key value   # 关键字(如set)不区分大小写

# 2、获取键对应的值 - get
get key         # 键区分大小写，一般默认使用string来存储数据，以二进制存储，中文以二进制显示，想要输出中文要在登录时加上 --raw参数

# 3、删除一个键 - delete
delete key

# 4、查看一个键是否存在 - exist
exist key 

# 5、检索符合条件的键 - keys
keys *      # 返回所有的键

# 6、清空所有的键
flushall

# 7、查看键的过期时间 - ttl (Time to live)
TTL key         # "-1": 没有设置过期时间;  "-2":已经过期(过期后无法被检索到)

# 8、设置一个键的过期时间 - expire
expire key 10       # 设置一个键的过期时间是10s

# 9、同时设置一个带有过期时间的键值对 - setex
setex key time value    # 如"setex name 10 lk"

# 10、判断一个键是否存在，不存在则创建赋值，存在则不进行任何操作 - setnx
setnx key value         # 应用场景：验证码
```

## 3、list
```
# 1、新增元素 - lpush/rpush
lpush key value     # list头部新增一个元素
rpush key value     # list尾部新增一个元素

# 2、查看指定列表的切片 - lrange
lrange key {起始位置} {终止位置}

# 3、删除元素 - rpop/lpop
rpop key n   # 弹出list的尾部n个元素
lpop key n   # 弹出list的头部n个元素

# 4、获取list长度 - llen
llen key

# 5、修建切片 - ltrim
ltrim key {起始位置} {终止位置}
```

## 4、set
```
# 1、新增元素 - sadd
sadd key value

# 2、查看成员 - smembers(会员)
smembers key

# 3、查看一个成员是不是属于集合 - sismembers(is_member)
sismember key member

# 4、删除一个元素 - srem(remove)
srem key value

# 5、交并补 - sinter | sunion | Sdiff

```

## 5、有序集合(Zset)
每个成员关联一个浮点数，依据浮点数进行排序(默认升序); 成员唯一，浮点数可重复。
```
# 1、新增元素 - zadd
zadd key {浮点数} value

# 2、切片查看 - zrange
zrange key {起始位置} {终止位置}
zrange key {起始位置} {终止位置} withscores    # 同时输出浮点数

# 3、查看指定成员的浮点数 - Zscore
zscore key value

# 4、查看指定成员的排名 - zrank(升序) | zrevrank(降序)
zrank key value
```

## 6、Hash
类似对象
```
# 1、新建一个哈希 - Hset
hset key field value

# 2、获取hash的键值 - hget
hget key field

# 3、详细输出所有键值对 - hgetall
hgetall key

# 4、删除指定键值对 - hdel
hdel key field

...
```

# 五、

## 1、发布订阅模式
