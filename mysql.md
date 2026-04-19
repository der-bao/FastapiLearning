# MySQL

# 一、简介

MySQL是一种关系型数据库**管理系统**。

# 二、安装

```
# Windows
下载链接：https://dev.mysql.com/downloads/installer/
```

# 三、基本操作

## 1. 表的相关操作

```
# 运行服务端，windows-cmd
net start mysql80	# 默认端口3306
net stop mysql80	# 停止服务端，cmd管理员身份运行

# 打开mysql命令行客户端
mysql -u root -p

# 查看当前有哪些数据库
show databases;

# 创建一个数据库
create database {db_name};

# 删除一个数据库
drop database {db_name};

# 选中数据库
use {db_name};

# 建表
create table {table_name} (
    id int,         # 字段 数据类型
    name varchar(100),
    level int,
    exp int,
    gold decimal(10,2)
);

# 数据类型
    - INTEGER ：整数
    - TEXT : 文本
    - REAL : 浮点数
    - BLOB：二进制数据
    - NULL：空值

# 约束条件:
    - PRIMARY KEY : 主键，唯一标识该行数据（如用户的专属ID），全表不能有该值相同的两行。
    - AUTOINCREMENT : 自动递增
    - NOT NULL : 不能为空
    - UNIQUE : 唯一
    - DEFAULT : 默认值
    - FOREIGN KEY : 外键，用于与其他表关联，保证引用的数据必须存在（如评论表里的 user_id 必须在用户表里的id存在）。

# 查看当前数据库有哪些表
show tables;

# 查看表的结构 describe
desc {table_name}

# 修改表结构
alter table {table_name} modify column {字段名如name} varchar(200);     # 关键字:modify 修改字段数据类型
alter table {table_name} rename column {字段名} to {new字段名};         # 关键字: rename 
alter table {table_name} add column {字段名} {数据类型};                # ADD
alter table {table_name} drop column {字段名};               # drop

# 删表
drop table {table_name};
```

## 2. 增删改查

```
# 增加 INSERT
insert into {tb_name} (field1,field2,...) values(val1,val2,...)     # 如果是字符串记得加引号
insert into {tb_name} (field1,field2,...) values(val1,val2,...),(val1,val2,...)     # 插入多条

# 查 SELECT
## 查询所有数据
select * from {tb_name}; 
## 条件查询
select {field1,...} from {tb_name} where   
SELECT name, age FROM user WHERE age > ?

# 改 UPDATE
UPDATE user SET address = ? WHERE name = ?

# 删 DELETE
DELETE FROM user WHERE age < ?
```

## 3. 数据导入和导出

```
# 导出，在cmd下执行
mysqldump -u root -p {db_name} {tb_name} > {path/db.sql}   # {tb_name}省略则导出所有的表

# 导入
mysql -u root -p {db_name} < {path/db.sql}
```

## 4. 索引