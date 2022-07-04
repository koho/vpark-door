# VPark Door

云硅谷门禁网页版，可代替 APP 端，开启公司门禁。

## 创建 MySQL 数据库
```sql
CREATE TABLE `door_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time` datetime DEFAULT NULL,
  `username` varchar(64) DEFAULT NULL,
  `door_id` varchar(50) DEFAULT NULL,
  `door_name` varchar(100) DEFAULT NULL,
  `code` int(11) DEFAULT NULL,
  `msg` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
);
```

在 `app.py` 配置数据库信息。

## 安装 Python 依赖
```shell
pip install -r requirements.txt
```

## 运行服务
```shell
python vpark.py
```
