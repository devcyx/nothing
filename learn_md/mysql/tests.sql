delimiter $
create procedure demo01(in a int, in b int)
begin
declare c int default 0;
-- set c = a+b;
select count(*) into c from emp;
select concat('a+b=', c);
end$

create procedure demo02(in height int, out body varchar(10))
begin
-- declare body varchar(10);
IF height > 90 then set body = '大肌霸';
elseif height > 75 then set body = '肌肉男';
elseif height > 60 then set  body='标准身材';
else set body = '真的垃圾';
end if; 

-- select concat('你的身材是：', body);
-- return body
end$

create procedure demo03(in height int)
begin
declare body varchar(10);
-- 第一种方法
case when height > 90 then set body = '大肌霸';
when height > 75 then set body = '肌肉男';
when height > 60 then set  body='标准身材';
else set body = '真的垃圾';
end case; 

select concat('你的身材是：', body);

-- 第二种方法
case height when 90 then set body = '大肌霸';
when 75 then set body = '肌肉男';
when 60 then set  body='标准身材';
else set body = '真的垃圾';
end case; 
-- return body
select concat('你的身材是：', body);
end$

-- 游标的使用
create procedure demo04()
begin
declare cname varchar(20) default '没有啊';
declare csal double(7, 2);
declare has_data int default 1;

declare cursor_emp cursor for select ename, sal from emp;
declare exit handler for not found set has_data=0;
open cursor_emp;

c:loop
  fetch cursor_emp into cname, csal;
  select concat('val=', cname, 'sal=', csal, 'has_data=', has_data);
  if has_data=0 then
    leave c;
  end if;
end loop c;

close cursor_emp;
end$

-- 创建存储函数
create function demo05(sal int)
returns varchar(10)
begin
if sal > 50 then
  return 'pzmsb';
else return 'sbsb';
end if;
end$

-- 创建触发器
delimiter $
create trigger emp_logs_insert_trigger
after insert 
on emp
for each row
begin
  insert into emp_logs values (null, 'insert', now(), 1, concat('插入后的数据 empno=', new.empno, ' ename=', new.ename, ' job=', new.job, ' sal=', new.sal));
end$

delimiter ;