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

# sql优化

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

[explain 详解](https://www.cnblogs.com/xuanzhi201111/p/4175635.html)

```sql
--基本操作
explain select * from table_name;

```

## profiling分析sql
分析sql语句  在各个阶段的耗时情况
```sql
--1 是否支持profiling
select @@have_profiling;
--2 查看是否开启profiling操作
select @@profiling;
-- 如果未开启
set profiling=1 开启

--查看所有操作耗时时间的列表
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
7. 使用or连接符 如果两边的条件其中之一不包含索引，那索引将会失效。用and则不会。
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
load data local infile(从哪加载) '/root/sql.log'(路径) into table 'table_name' fields terminated by ','(每个字段根据什么分割) lines terminated by '\n'(每一行根据什么分割)；
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
如果不想排序 可以使用 order by null来禁止排序
覆盖索引来优化
```

## 子查询优化
    使用多表联合查询来代替子查询