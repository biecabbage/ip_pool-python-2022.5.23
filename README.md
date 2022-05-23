# ip代理的爬虫文档
## 爬取代理ip,并存储到数据库中

## 数据库设计
+-----------+--------------+------+-----+---------+----------------+
| Field     | Type         | Null | Key | Default | Extra          |
+-----------+--------------+------+-----+---------+----------------+
| id        | int          | NO   | PRI | NULL    | auto_increment |
| ip        | varchar(80)  | YES  |     | NULL    |                |
| port      | varchar(10)  | YES  |     | NULL    |                |
| anonymity | varchar(30)  | YES  |     | NULL    |                |
| type      | varchar(10)  | YES  |     | NULL    |                |
| location  | varchar(120) | YES  |     | NULL    |                |
| socket    | varchar(120) | YES  |     | NULL    |                |
| data      | datetime     | YES  |     | NULL    |                |
+-----------+--------------+------+-----+---------+----------------+
## 爬虫逻辑
爬取到代理ip后,发送请求得到响应码,可以的话进行数据库的筛选，把数据库的数据依次发送请求，不能用就直接删除(确保数据库内的ip拿出来随时可用)后,存入数据库
## 项目架构
解决了什么问题，满足了什么需求?

可以使用代理ip,防止被封ip

目标用户是谁?

白嫖党
