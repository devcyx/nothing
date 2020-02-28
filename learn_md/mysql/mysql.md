# 用户

## 创建用户

``` sql
create user 'username'@'localhost(可以在那里登录)' identified by 'password'
```

说明：
* username：你将创建的用户名
* host：指定该用户在哪个主机上可以登陆，如果是本地用户可用 localhost，如果想让该用户可以从任意远程主机登陆，可以使用通配符 %
*password：该用户的登陆密码，密码可以为空，如果为空则该用户可以不需要密码登陆服务器

## 授权

```sql
  GRANT privileges ON databasename.tablename TO 'username'@'host'
```

说明：
* privileges：用户的操作权限，如 SELECT，INSERT，UPDATE 等，如果要授予所的权限则使用 ALL
* databasename：数据库名
* tablename：表名，如果要授予该用户对所有数据库和表的相应操作权限则可用*表示，如*.*

### 授权完成  刷新

```sql
flush privileges;
```

### 权限查看

```sql
-- 方式一
show grants for username;
-- 方式二
select * from mysql.user where user='username'\G;
```

## 设置与更改用户密码

```sql
SET PASSWORD FOR 'username'@'host' = PASSWORD('newpassword');
--如果是当前用户
SET PASSWORD = PASSWORD("newpassword");
```

## 撤销用户权限

```sql
REVOKE privilege ON databasename.tablename FROM 'username'@'host';
```

## 删除用户

  ```sql
  DROP USER 'username'@'host';
  ```

# 索引

  * 优点：
  1. 提高数据的查询效率，降低数据库的 IO 成本（不用遍历）
  2. 建立索引列 对数据进行排序，降低的排序的成本。
  * 劣势：
  1. 实际上索引也是一张表，该表保存了所以列和主键字段并指向了实体类的记录，沿用一定空间（ 放在内存里）
  2. 虽然提高查询的效率但是大大降低了更新表的速度，因为 insert，update,delete 都需要去更改索

## 4 种主流的索引：

  1. BTree 索引： InnoDB,MyISAM,Memory 引擎都支持
  2. HASH 索引：Memory 引擎支持
  3. R-tree 索引：MyISAM 支持
  4. Full-text: InnoDB（5.6 版本之后），MyISAM 支持

## 索引的数据库 B+ 树

## 索引的分类

  1. 单值索引： 只针对一列进行建立索引，一个表可以有多个
  2. 唯一索引：索引列的值必须不能重复，可以为空
  3. 复合索引： 一个索引包含多个列

## 索引的基本操作

  1. 创建 create index index_name on table_name

## 索引的设计原则

  1. 数量量比较大，查询频率比较高
  2. 根据查询条件中的字段建索引
  3. 建立唯一索引最好，提高效率
  4. 索引不是越多越好
  5. 使用短索引（不占磁盘空间）
  6. 利用最左索引

# 存储过程和函数

* 是一推 sql 语句
* 减少应用程序和数据的交互 提高效率
* 存储过程没有返回值，存储函数有

## 存储的过程的基本使用

### 存储的过程的创建

  CREATE PROCEDURE name(params,)
  begin
    -- sql 语句
  end;

  delimiter 分隔符（终止符） 将默认的；修改为你想要的（主要是在存储过程中 写 sql 的时候 会把；识别为终止符）

### 存储的过程的调用

  call procedure_name;

### 查询存储过程

  -- 查询 db_name 数据库中的所有存储过程
  select name from mysql.proc where db='db_name';

  -- 查询存储过程的状态信息
  show procedure status;

  -- 查询某个存储过程的定义
  select create procedure test.pro_tests\G1;

### 基本语法

#### 变量

```sql
  -- 声明一个变量
  DECLARE name type default;
  -- 赋值
  1. set name = val
  2. select count(*) into name from tb_name;
```

#### if

  if xxx then xxx
  elseif xxx then xxx
  else xxx
  end if;

#### 输入输出

  IN 输入参数
  OUT 输出参数
  INOUT 既可以输入又可以输出

  ``` 伪代码
  创建：create procedure handle(in height int, out descr vachar(60))
  调用： call handle(188, @decsr)
  select @decsr  一个@代表当前用户会话变量（会话结束时会被释放）  @@ 代表系统变量
  ```

#### case 语法

  1. 写法一

  ``` sql
  case 变量
  when 值1 then xxx
  when 值2 then xxx
  else xxx
  end case;
  ```

  2. 写法二

  ```sql
  case
  when 条件表达式 then xxx
  when 条件表达式 then xxx
  else xxx
  end case;
  ```

#### while 循环

  条件不满足时，终止循环

  ```sql
  when 条件表达式 do
    xxx
  end when;
  ```

#### repeat 循环

  条件满足时，终止循环

  ```sql
  repeat
    xxx(循环体)
    until 条件表达式(不需要加分号)
  end repeat;
  ```

#### loop+leave 循环

  条件满足时，终止循环

  ```sql
  [循环名]:loop
    xxx(循环体)
    if 条件表达式 then -- 终止条件
      leave [循环名];
     end if;
  end loop [循环名];
  ```

#### 游标

  ```sql
  -- 声明接收字段的变量和终止条件的变量
  declare 字段名 类型;
  declare has_data int default 1;
  -- 声明一个游标
  declare cursor_name cursor for select 字段名 from table_name;
  declare exit handler for not fand set has_data=0; -- 终止条件的声明 如果要用循环fetch来做的话

  open cursor_name; -- 打开游标

  while has_data=1 do
    fetch cursor_name into 字段名; -- 获取一条数据
    select conact('val=', 字段名);
  end while;

  close cursor_name -- 关闭游标
  ```

### 存储函数

```sql
create function func_name(params type,)
returns type --声明返回值的类型
begin
  declare data_name int;
  set data_name = 0;
  return data_name;
end
```

删除存储函数 drop function func_name;

# 触发器

## 创建触发器

```sql
create trigger trigger_name
before/after insert/update/delete
on table_name
for each row -- mysql只支持行级触发器
begin
  --new.xxx  表示新增或者修改后的最新数据
  --old.xxx  表示更新之前或者删除的数据
  --触发操作
end
```

### 触发器的查看和删除

```sql
--查看触发器
show trigger\g;
-- 删除触发器
drop trigger trigger_name;
```

``` day02  ```
# mysql 体系
* 连接层：连接池
* 服务层：缓存啥
* 引擎层： InnoDB
* 文件层：数据存储的地方

# 存储引擎
  * show engines;显示数据的所有引擎
  * 针对表，不同的表可以有不同的引擎

## InnoDB引擎
  * mysql5.5版本之后的默认引擎， 支持事物， 行级锁和外键
  * 表结构存储在.frm文件中 数据和索引存储在.ibd文件中

## MyISAM引擎
  * mysql5.5之前版本的默认引擎
  * 不支持事物，也不支持外键
  * 优点是访问速度快
  * .frm存储表定义
  * .MYD 存储的是数据
  * .MYI 存储的是索引

## MEMORY
  * 数据存放在内存中
  * .frm 存放表结构

## MEGER
  * 是一组MyISAM表的合集，本身不存储数据  跟视图有点像
  * 一组MyISAM的表结构必须一致 跟分表一样

# sql分析

## 查看sql的执行频率
```sql

--1
show [global（全局）] status like 'Com_______';

-- InnoDB
show [global] status like 'Innodb_rows_%'

```
## 定位抵效率执行sql
1. 慢查询日志
2. show processlist; 查看实时查询效率;

## explain分析执行计划
    type: system > const > eq_red >ref>fulltext>ref_or_null>unique_subquery>index_subquery>range>index>all

[explain 详解](https://www.cnblogs.com/xuanzhi201111/p/4175635.html)

```sql

-- 基本操作
explain select * from table_name;

```

## profiling分析sql
分析sql语句  在各个阶段的耗时情况
```sql

--1 是否支持 profiling
select @@have_profiling;
--2 查看是否开启 profiling 操作
select @@profiling;
-- 如果未开启
set profiling=1 开启

-- 查看所有操作耗时时间的列表
show profiling;
-- 查看某次操作  具体的耗时时间
show profile for query number;

```

## trace分析优化执行计划
  对sql语句进行优化 [详解](https://blog.csdn.net/hydhyd212/article/details/103231469)


# 索引的使用
  索引是查询更快的手段之一

1. 全值匹配:对索引中的所有列都指定具体值
2. 最左前缀法则： 如果索引了多列，要从最左列开始，并且不跳过中间索引列(跟where中顺序无关，主要看有没有包含最左列)
3. 范围查询右边的列、不能使用索引。：若最左索引列使用范围查询,则右边的列都不会在走索引
4. 不能再索引列进行运算操作，索引将失效。（例如substring截取）
5. 字符串不加单引号，会造成索引失效。
6. 避免使用select *,使用select 索引字段，可以不用回调查询去找对应的数据，直接返回索引列的值。
7. 使用or连接符 如果两边的条件其中之一不包含索引，那索引将会失效。用and则不会。<font color='red'>注：只能是单列索引  不能是复核索引</font>
8. 以%开头的Like模糊查询，索引失效。解决方法可以使用覆盖索引来代替* 。见第6条
9. 如果全表搜索比索引快  则mysql会全表扫描。（某一列相同的数据特别多）
10. is null，is not null 有时走索引，有时不走索引。mysql会根据null所占比例多少来决定是否走索引
11. in会使用索引， not in不使用索引
12. 单例索引和复合索引的选择，尽量选择符合索引。
### 索引使用情况的查看
```sql

show [global] status like 'Handler_read%';

```

# SQL优化
## 大批量插入数据的优化
```sql

load data local infile（从哪加载） '/root/sql.log'（路径） into table 'table_name' fields terminated by ','（每个字段根据什么分割） lines terminated by '\n'（每一行根据什么分割）；

```
1. 使用主键顺序插入：有序的效率比较高
2. 关闭唯一性校验；set unique_checks=0;导入之后再开启校验 设置为1.
3. 手动提交事务：导入之前执行 set autocommit=0;关闭。导入之后设置为1.

## insert语句优化
1. 插入多条sql语句，变成一条insert语句
2. 索引有序
3. start transaction;开启手动事务，插入完成后commit; 手动提交。

## order by 优化
###两种排序方式
1. filesort 根据文件系统排序 效率比较低
2. using index.select * 换成覆盖索引 直接返回索引表的数据 不用回调查询

### fielsort的优化
  mysql通过比较系统变量max_length_for_sort_data的大小和Query语句的大小,来判定使用哪个算法。
  max_length_for_sort_data大走一次扫描算法。
  可以适当提高sort_buffer_size和max_length_for_sort_data大小来提高效率
1. 两次扫描算法:第一次根据排序字段跟行指针进行排序，第二次根据行指针去原表查询数据。IO操作较多，影响效率
2. 一次扫描算法：一次性取出所有满足条件的所有字段.然后在sort buffer（排序区）中排序然后输出。效率比较高，但是内存占用大。

## group by优化
```

如果不想排序 可以使用 order by null 来禁止排序
覆盖索引来优化

```

## 子查询优化
    使用多表联合查询来代替子查询

## OR优化
    用union代替 or

## 分页查询优化（主要是排序耗时长）
1. 在索引上完成排序操作，在进行关联查询原表查询进行分页
2. 1：必须是主键自增 2.没有断层。则可以where id > 某个值  limit 10;

## 使用sql提示
1. use index(手动建议数据库根据用户指定的索引进行搜索)
2. ignore index  忽略
3. force index 强制执行这个索引
```sql

select * from table_name use index(index_name)

```

# 应用优化
1. 使用数据库连接池
2. 减少对mysql的访问
    2.1 避免对数据进行重复检索
    2.2 增加cache层
3. 负载均衡 分布式数据库、主从复制 读写分离

# 查询缓存

## 查询缓存配置
·
```sql

-- 1 查看当前数据库是否支持缓存
show variables like 'have_query_cache';

-- 2 查看当前 mysql 是否开启了查询缓存
show variables like 'query_cache_type';

-- 3 查看查询缓存的占用大小
show variables like 'query_cache_size';
-- 4 查看查看缓存的状态变量：
show status like 'Qcache%';

```
##  开启查询缓存
    MySQL的查询缓存默认是关闭的，需要手动配置参数
    query_cache_type.off或者0关闭 on或者1开启 demand或者2 按需进行(需要指定sql_cache选项 才能缓存)

    在/usr/my.cnf配置中，新增配置：
    query_cache_type=1

    配置完成重启服务器

## 查询缓存 select 选项

1. SQL_CACHE: 如果查询结果是可缓存的，并且query_cache_type为ON或者DEMAND，则缓存结果
```sql

select sql_cache id, name from table_name;

```
2. SQL_NO_CACHE: 不能缓存查询结果

```sql

select sql_no_cache id, name from table_name;

```

## 查询缓存失效的情况

1. sql语句必须一致
2. 当查询语句中有不确定的值，不会缓存。例如：now() current_date() ...等等
3. 不使用任何表查询语句。例如 select 'a';
4. 查询系统库中表时 不会有缓存。
5. 在存储过程，触发器或者实践的主体内执行的查询。
6. 如果表更改 针对这张表的所有缓存都会删除。例如insert update delete alert drop等等


# Mysql内存管理及优化
都是去mysql的配置文件的配置 /usr/mysql.conf
##内存优化原则
1. 除操作系统与应用程序之外，给mysql尽量多的内存座缓存。
2. 如果有MyISAM引擎的表 需要更多内存做IO缓存
3. 排序区、连接区的默认值根据最大连接数合理分配，如果设置太大，不但浪费资源，而且并发连接较高是会导致物理内存耗尽。

### MyISAM内存优化
1. key_buffer_size 分配多一点（索引用的）
2. read_buffer_size session独占 看最大连接数（全表扫描）
3. read_rnd_buffer_size session独占 (做排序用的)

### InnoDB内存优化
innodb用一块内存区做IO缓存池，该缓存池不仅用来缓存innodb的索引块，而且也用来缓存Innodb的数据块

1. innodb_log_buffer_size: 该变量决定了上诉最大缓存区的大小。性能的高低（越大越好）

2. innodb_log_buffer_size 决定了innodb重做日志缓存的大小

# Mysql并发参数的调整
1. max_connections:mysql的最大连接数 默认为151
2. back_log: 等待mysql连接的资源的最大值
3. table_open_cache:每一条sql 至少操作一张表 既有一个表缓存 改值为表缓存的最大值
4. thread_cache_size mysql线程池大小
5. innodb_lock_wait_timeout 等待行锁的超时时间 默认50ms

# Mysql锁问题

## 背景知识

**事务及其ACID属性**

事务是由一组SQL语句组成的逻辑处理单元。

事务具有以下4个特性，简称为事务ACID属性。

| ACID属性             | 含义                                                         |
| -------------------- | ------------------------------------------------------------ |
| 原子性（Atomicity）  | 事务是一个原子操作单元，其对数据的修改，要么全部成功，要么全部失败。 |
| 一致性（Consistent） | 在事务开始和完成时，数据都必须保持一致状态。                 |
| 隔离性（Isolation）  | 数据库系统提供一定的隔离机制，保证事务在不受外部并发操作影响的 “独立” 环境下运行。 |
| 持久性（Durable）    | 事务完成之后，对于数据的修改是永久的。                       |



**并发事务处理带来的问题**

| 问题                               | 含义                                                         |
| ---------------------------------- | ------------------------------------------------------------ |
| 丢失更新（Lost Update）            | 当两个或多个事务选择同一行，最初的事务修改的值，会被后面的事务修改的值覆盖。 |
| 脏读（Dirty Reads）                | 当一个事务正在访问数据，并且对数据进行了修改，而这种修改还没有提交到数据库中，这时，另外一个事务也访问这个数据，然后使用了这个数据。 |
| 不可重复读（Non-Repeatable Reads） | 一个事务在读取某些数据后的某个时间，再次读取以前读过的数据，却发现和以前读出的数据不一致。 |
| 幻读（Phantom Reads）              | 一个事务按照相同的查询条件重新读取以前查询过的数据，却发现其他事务插入了满足其查询条件的新数据。 |



**事务隔离级别**

为了解决上述提到的事务并发问题，数据库提供一定的事务隔离机制来解决这个问题。数据库的事务隔离越严格，并发副作用越小，但付出的代价也就越大，因为事务隔离实质上就是使用事务在一定程度上“串行化” 进行，这显然与“并发” 是矛盾的。

数据库的隔离级别有4个，由低到高依次为Read uncommitted、Read committed、Repeatable read、Serializable，这四个级别可以逐个解决脏写、脏读、不可重复读、幻读这几类问题。

| 隔离级别                | 丢失更新 | 脏读 | 不可重复读 | 幻读 |
| ----------------------- | -------- | ---- | ---------- | ---- |
| Read uncommitted        | ×        | √    | √          | √    |
| Read committed          | ×        | ×    | √          | √    |
| Repeatable read（默认） | ×        | ×    | ×          | √    |
| Serializable            | ×        | ×    | ×          | ×    |

备注 ： √  代表可能出现 ， × 代表不会出现 。

Mysql 的数据库的默认隔离级别为 Repeatable read ， 查看方式：

```

show variables like 'tx_isolation';

```

## 锁分类

```

从对数据操作的粒度分 ：

1） 表锁：操作时，会锁定整个表。

2） 行锁：操作时，会锁定当前操作行。

从对数据操作的类型分：

1） 读锁（共享锁）：针对同一份数据，多个读操作可以同时进行而不会互相影响。

2） 写锁（排它锁）：当前操作没有完成之前，它会阻断其他写锁和读锁。

```

## mysql锁

相对其他数据库而言，MySQL的锁机制比较简单，其最显著的特点是不同的存储引擎支持不同的锁机制。下表中罗列出了各存储引擎对锁的支持情况：
| 存储引擎 | 表级锁 | 行级锁 | 页面锁 |
| -------- | ------ | ------ | ------ |
| MyISAM   | 支持   | 不支持 | 不支持 |
| InnoDB   | 支持   | 支持   | 不支持 |
| MEMORY   | 支持   | 不支持 | 不支持 |
| BDB      | 支持   | 不支持 | 支持   |

MySQL这3种锁的特性可大致归纳如下 ：

| 锁类型 | 特点                                                         |
| ------ | ------------------------------------------------------------ |
| 表级锁 | 偏向MyISAM 存储引擎，开销小，加锁快；不会出现死锁；锁定粒度大，发生锁冲突的概率最高,并发度最低。 |
| 行级锁 | 偏向InnoDB 存储引擎，开销大，加锁慢；会出现死锁；锁定粒度最小，发生锁冲突的概率最低,并发度也最高。 |
| 页面锁 | 开销和加锁时间界于表锁和行锁之间；会出现死锁；锁定粒度界于表锁和行锁之间，并发度一般。 |

从上述特点可见，很难笼统地说哪种锁更好，只能就具体应用的特点来说哪种锁更合适！仅从锁的角度来说：表级锁更适合于以查询为主，只有少量按索引条件更新数据的应用，如Web 应用；而行级锁则更适合于有大量按索引条件并发更新少量不同数据，同时又有并查询的应用，如一些在线事务处理（OLTP）系统。

## MyISAM 表锁

​	1） 对MyISAM 表的读操作，不会阻塞其他用户对同一表的读请求，但会阻塞对同一表的写请求；

​	2） 对MyISAM 表的写操作，则会阻塞其他用户对同一表的读和写操作；

​	简而言之，就是读锁会阻塞写，但是不会阻塞读。而写锁，则既会阻塞读，又会阻塞写。


此外，MyISAM 的读写锁调度是写优先，这也是MyISAM不适合做写为主的表的存储引擎的原因。因为写锁后，其他线程不能做任何操作，大量的更新会使查询很难得到锁，从而造成永远阻塞。

### 加锁

MyISAM 在执行查询语句（SELECT）前，会自动给涉及的所有表加读锁，在执行更新操作（UPDATE、DELETE、INSERT 等）前，会自动给涉及的表加写锁，这个过程并不需要用户干预，因此，用户一般不需要直接用 LOCK TABLE 命令给 MyISAM 表显式加锁。

显示加表锁语法：

```SQL

加读锁 ： lock table table_name read;

加写锁 ： lock table table_name write；

```

### 解锁
UNLOCK TABLES;

### 查看锁竞争

```

show open tables；

```

In_user : 表当前被查询使用的次数。如果该数为零，则表是打开的，但是当前没有被使用。

Name_locked：表名称是否被锁定。名称锁定用于取消表或对表进行重命名等操作。


```

show status like 'Table_locks%';

```

Table_locks_immediate ： 指的是能够立即获得表级锁的次数，每立即获取锁，值加1。

Table_locks_waited ： 指的是不能立即获取表级锁而需要等待的次数，每等待一次，该值加1，此值高说明存在着较为严重的表级锁争用情况。

## InnoDB 行锁

InnoDB  实现了以下两种类型的行锁。

- 共享锁（S）：又称为读锁，简称S锁，共享锁就是多个事务对于同一数据可以共享一把锁，都能访问到数据，但是只能读不能修改。
- 排他锁（X）：又称为写锁，简称X锁，排他锁就是不能与其他锁并存，如一个事务获取了一个数据行的排他锁，其他事务就不能再获取该行的其他锁，包括共享锁和排他锁，但是获取排他锁的事务是可以对数据就行读取和修改。

对于UPDATE、DELETE和INSERT语句，InnoDB会自动给涉及数据集加排他锁（X)；

对于普通SELECT语句，InnoDB不会加任何锁；



可以通过以下语句显示给记录集加共享锁或排他锁 。

```

共享锁（S）：SELECT * FROM table_name WHERE ... LOCK IN SHARE MODE

排他锁（X) ：SELECT * FROM table_name WHERE ... FOR UPDATE

```
### 无索引行锁升级为表锁

如果不通过索引条件检索数据，那么InnoDB将对表中的所有记录加锁，实际效果跟表锁一样。

查看当前表的索引 ： show  index  from test_innodb_lock ;

### 间隙锁危害

当我们用范围条件，而不是使用相等条件检索数据，并请求共享或排他锁时，InnoDB会给符合条件的已有数据进行加锁； 对于键值在条件范围内但并不存在的记录，叫做 "间隙（GAP）" ， InnoDB也会对这个 "间隙" 加锁，这种锁机制就是所谓的 间隙锁（Next-Key锁） 。

### InnoDB 行锁争用情况

```sql

show  status like 'innodb_row_lock%';

```

```

Innodb_row_lock_current_waits: 当前正在等待锁定的数量

Innodb_row_lock_time: 从系统启动到现在锁定总时间长度

Innodb_row_lock_time_avg: 每次等待所花平均时长

Innodb_row_lock_time_max: 从系统启动到现在等待最长的一次所花的时间

Innodb_row_lock_waits: 系统启动后到现在总共等待的次数

当等待的次数很高，而且每次等待的时长也不小的时候，我们就需要分析系统中为什么会有如此多的等待，然后根据分析结果着手制定优化计划。

```
### 总结

InnoDB存储引擎由于实现了行级锁定，虽然在锁定机制的实现方面带来了性能损耗可能比表锁会更高一些，但是在整体并发处理能力方面要远远由于MyISAM的表锁的。当系统并发量较高的时候，InnoDB的整体性能和MyISAM相比就会有比较明显的优势。

但是，InnoDB的行级锁同样也有其脆弱的一面，当我们使用不当的时候，可能会让InnoDB的整体性能表现不仅不能比MyISAM高，甚至可能会更差。



优化建议：

- 尽可能让所有数据检索都能通过索引来完成，避免无索引行锁升级为表锁。
- 合理设计索引，尽量缩小锁的范围
- 尽可能减少索引条件，及索引范围，避免间隙锁
- 尽量控制事务大小，减少锁定资源量和时间长度
- 尽可使用低级别事务隔离（但是需要业务层面满足需求）

# 常用SQL技巧

## SQL执行顺序

编写顺序

```SQL

SELECT DISTINCT
	<select list>
FROM
	<left_table> <join_type>
JOIN
	<right_table> ON <join_condition>
WHERE
	<where_condition>
GROUP BY
	<group_by_list>
HAVING
	<having_condition>
ORDER BY
	<order_by_condition>
LIMIT
	<limit_params>

```

执行顺序

``` sql

FROM	<left_table>

ON 		<join_condition>

<join_type>		JOIN	<right_table>

WHERE		<where_condition>

GROUP BY 	<group_by_list>

HAVING		<having_condition>

SELECT DISTINCT		<select list>

ORDER BY	<order_by_condition>

LIMIT		<limit_params>

```

## 正则表达式使用

正则表达式（Regular Expression）是指一个用来描述或者匹配一系列符合某个句法规则的字符串的单个字符串。

| 符号   | 含义                          |
| ------ | ----------------------------- |
| ^      | 在字符串开始处进行匹配        |
| $      | 在字符串末尾处进行匹配        |
| .      | 匹配任意单个字符, 包括换行符  |
| [...]  | 匹配出括号内的任意字符        |
| [^...] | 匹配不出括号内的任意字符      |
| a*     | 匹配零个或者多个a(包括空串)   |
| a+     | 匹配一个或者多个a(不包括空串) |
| a?     | 匹配零个或者一个a             |
| a1\|a2 | 匹配a1或a2                    |
| a(m)   | 匹配m个a                      |
| a(m,)  | 至少匹配m个a                  |
| a(m,n) | 匹配m个a 到 n个a              |
| a(,n)  | 匹配0到n个a                   |
| (...)  | 将模式元素组成单一元素        |

```

select * from emp where name regexp '^T';

select * from emp where name regexp '2$';

select * from emp where name regexp '[uvw]';

```

## MySQL 常用函数

数字函数

| 函数名称                                                     | 作 用                                                      |
| ------------------------------------------------------------ | ---------------------------------------------------------- |
| ABS                                                          | 求绝对值                                                   |
| SQRT               | 求二次方根                                                 |
| MOD                 | 求余数                                                     |
| CEIL 和 CEILING | 两个函数功能相同，都是返回不小于参数的最小整数，即向上取整 |
| FLOOR            | 向下取整，返回值转化为一个BIGINT                           |
| RAND               | 生成一个0~1之间的随机数，传入整数参数是，用来产生重复序列  |
| ROUND            | 对所传参数进行四舍五入                                     |
| SIGN              | 返回参数的符号                                             |
| POW 和 POWER  | 两个函数的功能相同，都是所传参数的次方的结果值             |
| SIN                 | 求正弦值                                                   |
| ASIN               | 求反正弦值，与函数 SIN 互为反函数                          |
| COS                 | 求余弦值                                                   |
| ACOS               | 求反余弦值，与函数 COS 互为反函数                          |
| TAN                 | 求正切值                                                   |
| ATAN               | 求反正切值，与函数 TAN 互为反函数                          |
| COT                 | 求余切值                                                   |

字符串函数

| 函数名称  | 作 用                                                        |
| --------- | ------------------------------------------------------------ |
| LENGTH    | 计算字符串长度函数，返回字符串的字节长度                     |
| CONCAT    | 合并字符串函数，返回结果为连接参数产生的字符串，参数可以使一个或多个 |
| INSERT    | 替换字符串函数                                               |
| LOWER     | 将字符串中的字母转换为小写                                   |
| UPPER     | 将字符串中的字母转换为大写                                   |
| LEFT      | 从左侧字截取符串，返回字符串左边的若干个字符                 |
| RIGHT     | 从右侧字截取符串，返回字符串右边的若干个字符                 |
| TRIM      | 删除字符串左右两侧的空格                                     |
| REPLACE   | 字符串替换函数，返回替换后的新字符串                         |
| SUBSTRING | 截取字符串，返回从指定位置开始的指定长度的字符换             |
| REVERSE   | 字符串反转（逆序）函数，返回与原始字符串顺序相反的字符串     |

日期函数

| 函数名称                | 作 用                                                        |
| ----------------------- | ------------------------------------------------------------ |
| CURDATE 和 CURRENT_DATE | 两个函数作用相同，返回当前系统的日期值                       |
| CURTIME 和 CURRENT_TIME | 两个函数作用相同，返回当前系统的时间值                       |
| NOW 和  SYSDATE         | 两个函数作用相同，返回当前系统的日期和时间值                 |
| MONTH                   | 获取指定日期中的月份                                         |
| MONTHNAME               | 获取指定日期中的月份英文名称                                 |
| DAYNAME                 | 获取指定曰期对应的星期几的英文名称                           |
| DAYOFWEEK               | 获取指定日期对应的一周的索引位置值                           |
| WEEK                    | 获取指定日期是一年中的第几周，返回值的范围是否为 0〜52 或 1〜53 |
| DAYOFYEAR               | 获取指定曰期是一年中的第几天，返回值范围是1~366              |
| DAYOFMONTH              | 获取指定日期是一个月中是第几天，返回值范围是1~31             |
| YEAR                    | 获取年份，返回值范围是 1970〜2069                            |
| TIME_TO_SEC             | 将时间参数转换为秒数                                         |
| SEC_TO_TIME             | 将秒数转换为时间，与TIME_TO_SEC 互为反函数                   |
| DATE_ADD 和 ADDDATE     | 两个函数功能相同，都是向日期添加指定的时间间隔               |
| DATE_SUB 和 SUBDATE     | 两个函数功能相同，都是向日期减去指定的时间间隔               |
| ADDTIME                 | 时间加法运算，在原始时间上添加指定的时间                     |
| SUBTIME                 | 时间减法运算，在原始时间上减去指定的时间                     |
| DATEDIFF                | 获取两个日期之间间隔，返回参数 1 减去参数 2 的值             |
| DATE_FORMAT             | 格式化指定的日期，根据参数返回指定格式的值                   |
| WEEKDAY                 | 获取指定日期在一周内的对应的工作日索引                       |

聚合函数

| 函数名称                                         | 作用                             |
| ------------------------------------------------ | -------------------------------- |
| MAX     | 查询指定列的最大值               |
| MIN    | 查询指定列的最小值               |
| COUNT | 统计查询结果的行数               |
| SUM     | 求和，返回指定列的总和           |
| AVG     | 求平均值，返回指定列数据的平均值 |


**mysql day4**
# MySql中常用工具

## mysql

该mysql不是指mysql服务，而是指mysql的客户端工具。

语法 ：

```
mysql [options] [database]
```

### 连接选项

```
参数 ： 
	-u, --user=name			指定用户名
	-p, --password[=name]	指定密码
	-h, --host=name			指定服务器IP或域名
	-P, --port=#			指定连接端口

示例 ：
	mysql -h 127.0.0.1 -P 3306 -u root -p
	
	mysql -h127.0.0.1 -P3306 -uroot -p2143
	
```

### 执行选项

```
-e, --execute=name		执行SQL语句并退出
```

此选项可以在Mysql客户端执行SQL语句，而不用连接到MySQL数据库再执行，对于一些批处理脚本，这种方式尤其方便。

```
示例：
	mysql -uroot -p2143 db01 -e "select * from tb_book";
```
## mysqladmin

  
mysqladmin 是一个执行管理操作的客户端程序。可以用它来检查服务器的配置和当前状态、创建并删除数据库等。

可以通过 ： mysqladmin --help  指令查看帮助文档

```
示例 ：
	mysqladmin -uroot -p2143 create 'test01';  
	mysqladmin -uroot -p2143 drop 'test01';
	mysqladmin -uroot -p2143 version;
	
```

## mysqlbinlog

由于服务器生成的二进制日志文件以二进制格式保存，所以如果想要检查这些文本的文本格式，就会使用到mysqlbinlog 日志管理工具。

语法 ：

```
mysqlbinlog [options]  log-files1 log-files2 ...

选项：
	
	-d, --database=name : 指定数据库名称，只列出指定的数据库相关操作。
	
	-o, --offset=# : 忽略掉日志中的前n行命令。
	
	-r,--result-file=name : 将输出的文本格式日志输出到指定文件。
	
	-s, --short-form : 显示简单格式， 省略掉一些信息。
	
	--start-datatime=date1  --stop-datetime=date2 : 指定日期间隔内的所有日志。
	
	--start-position=pos1 --stop-position=pos2 : 指定位置间隔内的所有日志。
```

##  mysqldump

mysqldump 客户端工具用来备份数据库或在不同数据库之间进行数据迁移。备份内容包含创建表，及插入表的SQL语句。

语法 ：

```
mysqldump [options] db_name [tables]

mysqldump [options] --database/-B db1 [db2 db3...]

mysqldump [options] --all-databases/-A
```

### 连接选项

```
参数 ： 
	-u, --user=name			指定用户名
	-p, --password[=name]	指定密码
	-h, --host=name			指定服务器IP或域名
	-P, --port=#			指定连接端口
```

###  输出内容选项

```
参数：
	--add-drop-database		在每个数据库创建语句前加上 Drop database 语句
	--add-drop-table		在每个表创建语句前加上 Drop table 语句 , 默认开启 ; 不开启 (--skip-add-drop-table)
	
	-n, --no-create-db		不包含数据库的创建语句
	-t, --no-create-info	不包含数据表的创建语句
	-d --no-data			不包含数据
	
	 -T, --tab=name			自动生成两个文件：一个.sql文件，创建表结构的语句；
	 						一个.txt文件，数据文件，相当于select into outfile  
```

```
示例 ： 
	mysqldump -uroot -p2143 db01 tb_book --add-drop-database --add-drop-table > a
	
	mysqldump -uroot -p2143 -T /tmp test city
```

## mysqlimport/source

mysqlimport 是客户端数据导入工具，用来导入mysqldump 加 -T 参数后导出的文本文件。

语法：

```
mysqlimport [options]  db_name  textfile1  [textfile2...]
```

示例：

```
mysqlimport -uroot -p2143 test /tmp/city.txt
```



如果需要导入sql文件,可以使用mysql中的source 指令 : 

```
source /root/tb_book.sql
```

## mysqlshow

mysqlshow 客户端对象查找工具，用来很快地查找存在哪些数据库、数据库中的表、表中的列或者索引。

语法：

```
mysqlshow [options] [db_name [table_name [col_name]]]
```

参数：

```
--count		显示数据库及表的统计信息（数据库，表 均可以不指定）

-i			显示指定数据库或者指定表的状态信息
```



示例：

```
#查询每个数据库的表的数量及表中记录的数量
mysqlshow -uroot -p2143 --count

#查询test库中每个表中的字段书，及行数
mysqlshow -uroot -p2143 test --count

#查询test库中book表的详细情况
mysqlshow -uroot -p2143 test book --count

```

#  Mysql 日志

在任何一种数据库中，都会有各种各样的日志，记录着数据库工作的方方面面，以帮助数据库管理员追踪数据库曾经发生过的各种事件。MySQL 也不例外，在 MySQL 中，有 4 种不同的日志，分别是错误日志、二进制日志（BINLOG 日志）、查询日志和慢查询日志，这些日志记录着数据库在不同方面的踪迹。

## 错误日志

错误日志是 MySQL 中最重要的日志之一，它记录了当 mysqld 启动和停止时，以及服务器在运行过程中发生任何严重错误时的相关信息。当数据库出现任何故障导致无法正常使用时，可以首先查看此日志。

该日志是默认开启的 ， 默认存放目录为 mysql 的数据目录（var/lib/mysql）, 默认的日志文件名为  hostname.err（hostname是主机名）。

查看日志位置指令 ： 

```sql
show variables like 'log_error%';
```


查看日志内容 ： 

```shell
tail -f /var/lib/mysql/xaxh-server.err
```

### 二进制日志

二进制日志（BINLOG）记录了所有的 DDL（数据定义语言）语句和 DML（数据操纵语言）语句，但是不包括数据查询语句。此日志对于灾难时的数据恢复起着极其重要的作用，MySQL的主从复制， 就是通过该binlog实现的。

二进制日志，默认情况下是没有开启的，需要到MySQL的配置文件中开启，并配置MySQL日志的格式。 

配置文件位置 : /usr/my.cnf

日志存放位置 : 配置时，给定了文件名但是没有指定路径，日志默认写入Mysql的数据目录。

```
#配置开启binlog日志， 日志的文件前缀为 mysqlbin -----> 生成的文件名如 : mysqlbin.000001,mysqlbin.000002
log_bin=mysqlbin

#配置二进制日志的格式
binlog_format=STATEMENT

```

### 日志格式

**STATEMENT**

该日志格式在日志文件中记录的都是SQL语句（statement），每一条对数据进行修改的SQL都会记录在日志文件中，通过Mysql提供的mysqlbinlog工具，可以清晰的查看到每条语句的文本。主从复制的时候，从库（slave）会将日志解析为原文本，并在从库重新执行一次。



**ROW**

该日志格式在日志文件中记录的是每一行的数据变更，而不是记录SQL语句。比如，执行SQL语句 ： update tb_book set status='1' , 如果是STATEMENT 日志格式，在日志中会记录一行SQL文件； 如果是ROW，由于是对全表进行更新，也就是每一行记录都会发生变更，ROW 格式的日志中会记录每一行的数据变更。



**MIXED**

这是目前MySQL默认的日志格式，即混合了STATEMENT 和 ROW两种格式。默认情况下采用STATEMENT，但是在一些特殊情况下采用ROW来进行记录。MIXED 格式能尽量利用两种模式的优点，而避开他们的缺点。



### 日志读取

由于日志以二进制方式存储，不能直接读取，需要用mysqlbinlog工具来查看，语法如下 ：

```
mysqlbinlog log-file；

```

**查看STATEMENT格式日志** 

执行插入语句 ：

```SQL
insert into tb_book values(null,'Lucene','2088-05-01','0');
```

 查看日志文件 ：


mysqlbin.index : 该文件是日志索引文件 ， 记录日志的文件名；

mysqlbing.000001 ：日志文件

查看日志内容 ：

```
mysqlbinlog mysqlbing.000001；

```


**查看ROW格式日志**

配置 :

```
#配置开启binlog日志， 日志的文件前缀为 mysqlbin -----> 生成的文件名如 : mysqlbin.000001,mysqlbin.000002
log_bin=mysqlbin

#配置二进制日志的格式
binlog_format=ROW

```

插入数据 :

```sql
insert into tb_book values(null,'SpringCloud实战','2088-05-05','0');
```

如果日志格式是 ROW , 直接查看数据 , 是查看不懂的 ; 可以在mysqlbinlog 后面加上参数 -vv  

```SQL
mysqlbinlog -vv mysqlbin.000002 
```



## 日志删除

对于比较繁忙的系统，由于每天生成日志量大 ，这些日志如果长时间不清楚，将会占用大量的磁盘空间。下面我们将会讲解几种删除日志的常见方法 ：

**方式一** 

通过 Reset Master 指令删除全部 binlog 日志，删除之后，日志编号，将从 xxxx.000001重新开始 。

查询之前 ，先查询下日志文件 ： 

执行删除日志指令： 

```
Reset Master
```

执行之后， 查看日志文件 ：



**方式二**

执行指令 ``` purge  master logs to 'mysqlbin.******'``` ，该命令将删除  ``` ******``` 编号之前的所有日志。 



**方式三**

执行指令 ``` purge master logs before 'yyyy-mm-dd hh24:mi:ss'``` ，该命令将删除日志为 "yyyy-mm-dd hh24:mi:ss" 之前产生的所有日志 。



**方式四**

设置参数 --expire_logs_days=# ，此参数的含义是设置日志的过期天数， 过了指定的天数后日志将会被自动删除，这样将有利于减少DBA 管理日志的工作量。

配置如下 ： 

![1554125506938](assets/1554125506938.png) 



## 查询日志

查询日志中记录了客户端的所有操作语句，而二进制日志不包含查询数据的SQL语句。

默认情况下， 查询日志是未开启的。如果需要开启查询日志，可以设置以下配置 ：

```
#该选项用来开启查询日志 ， 可选值 ： 0 或者 1 ； 0 代表关闭， 1 代表开启 
general_log=1

#设置日志的文件名 ， 如果没有指定， 默认的文件名为 host_name.log 
general_log_file=file_name

```

在 mysql 的配置文件 /usr/my.cnf 中配置如下内容 ： 

![1554128184632](assets/1554128184632.png) 



配置完毕之后，在数据库执行以下操作 ：

```
select * from tb_book;
select * from tb_book where id = 1;
update tb_book set name = 'lucene入门指南' where id = 5;
select * from tb_book where id < 8;

```



执行完毕之后， 再次来查询日志文件 ： 

![1554128089851](assets/1554128089851.png) 



##  慢查询日志

慢查询日志记录了所有执行时间超过参数 long_query_time 设置值并且扫描记录数不小于 min_examined_row_limit 的所有的SQL语句的日志。long_query_time 默认为 10 秒，最小为 0， 精度可以到微秒。



### 文件位置和格式

慢查询日志默认是关闭的 。可以通过两个参数来控制慢查询日志 ：

```
# 该参数用来控制慢查询日志是否开启， 可取值： 1 和 0 ， 1 代表开启， 0 代表关闭
slow_query_log=1 

# 该参数用来指定慢查询日志的文件名
slow_query_log_file=slow_query.log

# 该选项用来配置查询的时间限制， 超过这个时间将认为值慢查询， 将需要进行日志记录， 默认10s
long_query_time=10

```



###  日志的读取

和错误日志、查询日志一样，慢查询日志记录的格式也是纯文本，可以被直接读取。

1） 查询long_query_time 的值。


2） 执行查询操作

```sql
select id, title,price,num ,status from tb_item where id = 1;
```

由于该语句执行时间很短，为0s ， 所以不会记录在慢查询日志中。



```
select * from tb_item where title like '%阿尔卡特 (OT-927) 炭黑 联通3G手机 双卡双待165454%' ;

```

该SQL语句 ， 执行时长为 26.77s ，超过10s ， 所以会记录在慢查询日志文件中。



3） 查看慢查询日志文件

直接通过cat 指令查询该日志文件 ： 


如果慢查询日志内容很多， 直接查看文件，比较麻烦， 这个时候可以借助于mysql自带的 mysqldumpslow 工具， 来对慢查询日志进行分类汇总。 



#  Mysql复制

复制是指将主数据库的DDL 和 DML 操作通过二进制日志传到从库服务器中，然后在从库上对这些日志重新执行（也叫重做），从而使得从库和主库的数据保持同步。

MySQL支持一台主库同时向多台从库进行复制， 从库同时也可以作为其他从服务器的主库，实现链状复制。



## 复制原理

MySQL 的主从复制原理如下。

![1554423698190](assets/1.jpg) 

从上层来看，复制分成三步：

- Master 主库在事务提交时，会把数据变更作为时间 Events 记录在二进制日志文件 Binlog 中。
- 主库推送二进制日志文件 Binlog 中的日志事件到从库的中继日志 Relay Log 。

- slave重做中继日志中的事件，将改变反映它自己的数据。



##  复制优势

MySQL 复制的有点主要包含以下三个方面：

- 主库出现问题，可以快速切换到从库提供服务。

- 可以在从库上执行查询操作，从主库中更新，实现读写分离，降低主库的访问压力。

- 可以在从库中执行备份，以避免备份期间影响主库的服务。



##  搭建步骤

### master

1） 在master 的配置文件（/usr/my.cnf）中，配置如下内容：

```properties
#mysql 服务ID,保证整个集群环境中唯一
server-id=1

#mysql binlog 日志的存储路径和文件名
log-bin=/var/lib/mysql/mysqlbin

#错误日志,默认已经开启
#log-err

#mysql的安装目录
#basedir

#mysql的临时目录
#tmpdir

#mysql的数据存放目录
#datadir

#是否只读,1 代表只读, 0 代表读写
read-only=0

#忽略的数据, 指不需要同步的数据库
binlog-ignore-db=mysql

#指定同步的数据库
#binlog-do-db=db01
```

2） 执行完毕之后，需要重启Mysql：

```sql
service mysql restart ；
```

3） 创建同步数据的账户，并且进行授权操作：

```sql
grant replication slave on *.* to 'itcast'@'192.168.192.131' identified by 'itcast';	

flush privileges;
```

4） 查看master状态：

```sql
show master status;
```

字段含义：

```
File : 从哪个日志文件开始推送日志文件 
Position ： 从哪个位置开始推送日志
Binlog_Ignore_DB : 指定不需要同步的数据库
```



###  slave

1） 在 slave 端配置文件中，配置如下内容：

```properties
#mysql服务端ID,唯一
server-id=2

#指定binlog日志
log-bin=/var/lib/mysql/mysqlbin
```

2）  执行完毕之后，需要重启Mysql：

```
service mysql restart；
```

3） 执行如下指令 ：

```sql
change master to master_host= '192.168.192.130', master_user='itcast', master_password='itcast', master_log_file='mysqlbin.000001', master_log_pos=413;
```

指定当前从库对应的主库的IP地址，用户名，密码，从哪个日志文件开始的那个位置开始同步推送日志。

4） 开启同步操作

```
start slave;

show slave status;
```

5） 停止同步操作

```
stop slave;
```



###  验证同步操作

1） 在主库中创建数据库，创建表，并插入数据 ：

```sql
create database db01;

user db01;

create table user(
	id int(11) not null auto_increment,
	name varchar(50) not null,
	sex varchar(1),
	primary key (id)
)engine=innodb default charset=utf8;

insert into user(id,name,sex) values(null,'Tom','1');
insert into user(id,name,sex) values(null,'Trigger','0');
insert into user(id,name,sex) values(null,'Dawn','1');
```

2） 在从库中查询数据，进行验证
