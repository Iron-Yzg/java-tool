/*
 * 阳光大姐业务系统 - 数据库重新设计 V2
 *
 * 设计原则：
 *   1. 单一职责：每张表只负责自己的业务域
 *   2. 逻辑外键：数据库层不强制外键约束，字段注释标明关联关系，由代码保证一致性
 *   3. 雪花算法主键：所有表 id 为 BIGINT，对应 Java @TableId(type = IdType.ASSIGN_ID)
 *   4. 逻辑删除：统一使用 is_deleted TINYINT(1) DEFAULT 0（0=未删除，1=已删除）
 *   5. 标准基础字段：id / create_time / update_time / create_user_id / update_user_id
 *   6. 审计追踪：敏感状态变更均有独立日志表记录
 *   7. MySQL 8.0+ 特性支持
 *
 * 业务域模块划分：
 *   模块一  ：组织架构域  (sys_*)
 *   模块二  ：服务项目域  (item_*)
 *   模块三  ：客户域      (cus_*)
 *   模块四  ：需求域      (req_*)
 *   模块五  ：服务员域    (staff_*)
 *   模块六  ：合同域      (contract_*)
 *   模块七  ：财务域      (fin_*)
 *   模块八  ：呼叫中心域  (call_*)
 *   模块九  ：回访域      (revisit_*)
 *   模块十  ：运营/报表域 (rpt_*)
 *   模块十一：培训域      (train_*)
 *   模块十二：消息通知域  (msg_*)
 *   模块十三：系统配置域  (cfg_*)
 *
 * Target Server Type    : MySQL
 * Target Server Version : 80000 (8.0+)
 * File Encoding         : UTF-8
 * Date: 2026-04-21
 */

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 模块一：组织架构域 (sys_*)
-- 表清单：
--   sys_store          门店/分部信息
--   sys_store_admin    门店管理员（坐席/运营人员）
--   sys_role           角色定义
--   sys_role_menu      角色菜单权限关联
--   sys_menu           菜单/权限资源
--   sys_user_role      用户角色关联
--   sys_dept           部门
--   sys_dept_user      部门用户关联
-- ############################################################

-- ----------------------------
-- 门店/分部信息表
-- ----------------------------
DROP TABLE IF EXISTS `sys_store`;
CREATE TABLE `sys_store` (
  `id`              BIGINT        NOT NULL                       COMMENT '主键ID（雪花算法）',
  `store_name`      VARCHAR(100)  NOT NULL                       COMMENT '门店名称',
  `store_code`      VARCHAR(50)   NOT NULL                       COMMENT '门店编码（唯一）',
  `store_type`      TINYINT       NOT NULL DEFAULT 0             COMMENT '门店类型：0=总部，1=直营店，2=加盟店',
  `parent_id`       BIGINT                                       COMMENT '上级门店ID（逻辑外键→sys_store.id），null表示顶级',
  `province`        VARCHAR(50)                                  COMMENT '省',
  `city`            VARCHAR(50)                                  COMMENT '市',
  `district`        VARCHAR(50)                                  COMMENT '区/县',
  `address`         VARCHAR(255)                                 COMMENT '详细地址',
  `phone`           VARCHAR(30)                                  COMMENT '门店联系电话',
  `manager_user_id` VARCHAR(32)                                  COMMENT '门店负责人用户ID（逻辑外键→sys_store_admin.id）',
  `sort_order`      INT           NOT NULL DEFAULT 0             COMMENT '显示排序',
  `status`          TINYINT       NOT NULL DEFAULT 1             COMMENT '状态：0=停用，1=启用',
  `remark`          VARCHAR(500)                                 COMMENT '备注',
  `is_deleted`      TINYINT(1)    NOT NULL DEFAULT 0             COMMENT '逻辑删除：0=未删除，1=已删除',
  `create_time`     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time`     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `create_user_id`  VARCHAR(32)                                  COMMENT '创建人用户ID',
  `update_user_id`  VARCHAR(32)                                  COMMENT '最后更新人用户ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_store_code` (`store_code`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_status` (`status`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='门店/分部信息表';

-- ############################################################
