# NoSQL(NoSQL = Not Only SQL )，意即"不仅仅是 SQL"。

在现代的计算系统上每天网络上都会产生庞大的数据量。

这些数据有很大一部分是由关系数据库管理系统（RDBMS）来处理。 1970 年 E. F. Codd's 提出的关系模型的论文 "A relational model of data for large shared data banks"，这使得数据建模和应用程序编程更加简单。

通过应用实践证明，关系模型是非常适合于客户服务器编程，远远超出预期的利益，今天它是结构化数据存储在网络和商务应用的主导技术。

NoSQL 是一项全新的数据库革命性运动，早期就有人提出，发展至 2009 年趋势越发高涨。NoSQL 的拥护者们提倡运用非关系型的数据存储，相对于铺天盖地的关系型数据库运用，这一概念无疑是一种全新的思维的注入。

# 什么是 MongoDB ?

MongoDB 是由 C++ 语言编写的，是一个基于分布式文件存储的开源数据库系统。

在高负载的情况下，添加更多的节点，可以保证服务器性能。

MongoDB 旨在为 WEB 应用提供可扩展的高性能数据存储解决方案。

MongoDB 将数据存储为一个文档，数据结构由键值 (key=>value) 对组成。MongoDB 文档类似于 JSON 对象。字段值可以包含其他文档，数组及文档数组。

# MongoDB 体系

| SQL 术语 / 概念 | MongoDB 术语 / 概念 | 解释 / 说明                        |
|---------------|-------------------|-----------------------------------|
| database      | database          | 数据库                             |
| table         | collection        | 数据库表 / 集合                     |
| row           | document          | 数据记录行 / 文档                   |
| column        | field             | 数据字段 / 域                      |
| index         | index             | 索引                              |
| table joins   |                   | 表连接，MongoDB 不支持               |
| primary key   | primary key       | 主键，MongoDB 自动将_id 字段设置为主键 |

# 基本使用

#### 1. 数据库切换

use db_name  

1. 如有db_name数据库 则切换至db_name数据库
2. 如果没有db_name数据库 则创建数据库（在内存中创建 不会持久化到磁盘。当有一个集合时才会持久化到磁盘）
3. 数据库名 不能起内置的名字 例如 admin,local,config等

#### 2. 数据库查看

show dbs 或者 show databases  

#### 3. 数据库的删除

db.dropDatabase()

### 2. 集合操作

#### 2.1 集合创建
db.createCollection('name')

### 3. 文档操作

#### 3.1 插入
db.collection_name.insert({})

#### 3.2修改

db.collection_name.remove(条件)

#### 3.3 删除

1. db.collection_name.update({条件}, {更改的值})
2. db.collection_name.update({条件}, {$set:{要修改的字段名：值}})

#### 3.4 查询

``` sql
-- 查询所有
db.collection_name.find()

-- 查询一个
db.collection_name.findone()

-- 查询有多少条记录
db.collection_name.count(条件)

-- 条件查询
db.collection_name.find({key:val})

-- 正则查询
db.collection_name.find({key:/RegEx/})

-- 比较查询
-- $lt 小于
-- $gt 大于
-- $lte 小于等于
-- $gte 大于等于

db.collection_name.find({key:{$gt: val}})

-- 比较查询
-- $in 在什么里
-- $nin 不在什么里

db.collection_name.find({key:{$in: [v1, v2]]}})

--条件连接查询
--$and:[{}, {}]
--$or:[{}, {}]

-- 限制查询多少条
db.collection_name.find().limit(number)

-- 跳过多少条记录
db.collection_name.find().skip(number)

-- 排序
db.collection_name.find().sort({key:1 or 0}) -- 1是升序 0是降序

```

### 4. 索引

#### 4.1 查询索引
db.collection_name.getIndexs()

#### 4.2 创建索引

db.collection.createIndex(keys, options)
keys: {key1:1 or 1} 1是升序 -1是降序

options可选参数如下：

| Parameter          | Type          | Description                                                                                                        |
|--------------------|---------------|--------------------------------------------------------------------------------------------------------------------|
| background         | Boolean       | 建索引过程会阻塞其它数据库操作，background可指定以后台方式创建索引，即增加 "background" 可选参数。 "background" 默认值为false。    |
| unique             | Boolean       | 建立的索引是否唯一。指定为true创建唯一索引。默认值为false.                                                                  |
| name               | string        | 索引的名称。如果未指定，MongoDB的通过连接索引的字段名和排序顺序生成一个索引名称。                                                |
| dropDups           | Boolean       | 3.0+版本已废弃。在建立唯一索引时是否删除重复记录, 指定 true 创建唯一索引。默认值为 false.                                       |
| sparse             | Boolean       | 对文档中不存在的字段数据不启用索引；这个参数需要特别注意，如果设置为true的话，在索引字段中不会查询出不包含对应字段的文档.。默认值为 false. |
| expireAfterSeconds | integer       | 指定一个以秒为单位的数值，完成 TTL设定，设定集合的生存时间。                                                                  |
| v                  | index version | 索引的版本号。默认的索引版本取决于mongod创建索引时运行的版本。                                                               |
| weights            | document      | 索引权重值，数值在 1 到 99, 999 之间，表示该索引相对于其他索引字段的得分权重。                                                  |
| default_language   | string        | 对于文本索引，该参数决定了停用词及词干和词器的规则的列表。 默认为英语                                                          |
| language_override  | string        | 对于文本索引，该参数指定了包含在文档中的字段名，语言覆盖默认的language，默认值为 language.                                       |

#### 4.2 删除索引

* 删除单个

db.collection.dropIndex(index_name)

* 删除所有

db.collection.dropIndexs()

#### 4.3 执行计划（查询分析） explain

db.collection.find().explain(options)

#### 4.4 涵盖查询 （mysql叫覆盖索引 只查询显示索引列 就不会去集合里面重新获取其他数据）

gender和user_name是复合索引  
db.users.find({gender:"M"}, {user_name:1, _id:0})

### 5 MongoDB 复制（副本集）

MongoDB复制是将数据同步在多个服务器的过程。

复制提供了数据的冗余备份，并在多个服务器上存储数据副本，提高了数据的可用性， 并可以保证数据的安全性。

复制还允许您从硬件故障和服务中断中恢复数据。

### 6 MongoDB 分片

在Mongodb里面存在另一种集群，就是分片技术, 可以满足MongoDB数据量大量增长的需求。

当MongoDB存储海量的数据时，一台机器可能不足以存储数据，也可能不足以提供可接受的读写吞吐量。这时，我们就可以通过在多台机器上分割数据，使得数据库系统能存储和处理更多的数据。

