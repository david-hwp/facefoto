-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS `group`;
DROP TABLE IF EXISTS `photo`;
CREATE TABLE `group` (id BIGINT PRIMARY KEY AUTO_INCREMENT,oss_dir TEXT NOT NULL comment 'oss 中的文件路径',created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP comment '创建时间');
CREATE TABLE `photo` (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name CHARACTER(200) NOT NULL comment '图片名称',
  oss_path TEXT NOT NULL COMMENT 'oss文件系统的路径',
  group_id CHARACTER(100) NOT NULL comment '组id',
  feature MEDIUMTEXT NOT NULL comment '特征值',
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP comment '创建时间'
);
