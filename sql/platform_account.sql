/*
 Navicat Premium Dump SQL

 Source Server         : 测试-172.21.0.7
 Source Server Type    : MySQL
 Source Server Version : 80041 (8.0.41)
 Source Host           : 172.21.0.7:3306
 Source Schema         : lysz-media

 Target Server Type    : MySQL
 Target Server Version : 80041 (8.0.41)
 File Encoding         : 65001

 Date: 14/04/2026 09:10:17
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for platform_account
-- ----------------------------
DROP TABLE IF EXISTS `platform_account`;
CREATE TABLE `platform_account` (
  `username` varchar(64) COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户名',
  `cookie` text COLLATE utf8mb4_general_ci COMMENT '用户登录信息',
  `platform_type` varchar(10) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '平台名称',
  `id` bigint NOT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `create_user_id` varchar(32) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `update_user_id` varchar(32) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='视频平台账户';

SET FOREIGN_KEY_CHECKS = 1;
