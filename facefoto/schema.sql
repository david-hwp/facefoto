-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS `group`;
DROP TABLE IF EXISTS `photo`;
DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS `cache`;
CREATE TABLE `group` (id BIGINT PRIMARY KEY AUTO_INCREMENT,oss_dir TEXT NOT NULL comment 'oss 中的文件路径',created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP comment '创建时间');

CREATE TABLE `photo` (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name CHARACTER(200) NOT NULL comment '图片名称',
  oss_path TEXT NOT NULL COMMENT 'oss文件系统的路径',
  group_id CHARACTER(100) NOT NULL comment '组id',
  feature MEDIUMTEXT NOT NULL comment '特征值',
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP comment '创建时间'
);

CREATE TABLE `face` (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  user_id CHARACTER(200) NOT NULL comment '用户id',
  group_id CHARACTER(100) NOT NULL comment '关注的组id',
  photo_id INTEGER NOT NULL comment '头像图片id',
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP comment '创建时间'
);

CREATE TABLE `cache` (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  user_id CHARACTER(200) NOT NULL comment '用户id',
  group_id CHARACTER(100) NOT NULL comment '关注的组id',
  similar_photo_id INTEGER NOT NULL comment '相似图片的id',
  notified BOOLEAN NOT NULL comment '是否已推送通知',
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP comment '创建时间'
);