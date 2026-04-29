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

-- 模块三：客户域 (cus_*)
-- ############################################################

DROP TABLE IF EXISTS `cus_customer`;
CREATE TABLE `cus_customer` (
  `id`                  BIGINT        NOT NULL                       COMMENT '主键ID（雪花算法）',
  `customer_no`         VARCHAR(50)                                  COMMENT '客户编号（系统生成，唯一）',
  `customer_name`       VARCHAR(100)  NOT NULL                       COMMENT '客户姓名',
  `mobile`              VARCHAR(20)   NOT NULL                       COMMENT '客户手机号（主联系方式）',
  `mobile_alt`          VARCHAR(20)                                  COMMENT '备用手机号',
  `gender`              TINYINT       NOT NULL DEFAULT 0             COMMENT '性别：0=未知，1=男，2=女',
  `id_card`             VARCHAR(64)                                  COMMENT '身份证号（脱敏存储）',
  `birthday`            DATE                                         COMMENT '出生日期',
  `wechat_openid`       VARCHAR(128)                                 COMMENT '微信OpenID',
  `wechat_nickname`     VARCHAR(100)                                 COMMENT '微信昵称',
  `province`            VARCHAR(50)                                  COMMENT '省',
  `city`                VARCHAR(50)                                  COMMENT '市',
  `district`            VARCHAR(50)                                  COMMENT '区/县',
  `address`             VARCHAR(500)                                 COMMENT '详细地址',
  `source_type`         VARCHAR(20)                                  COMMENT '客户来源：CALL=电话，WX=微信，WALK=到访，REFERRAL=转介绍，OTHER=其他',
  `source_detail`       VARCHAR(200)                                 COMMENT '来源详情（如推荐人、广告渠道等）',
  `belong_store_id`     BIGINT                                       COMMENT '所属门店ID（逻辑外键→sys_store.id）',
  `belong_seat_id`      BIGINT                                       COMMENT '归属坐席ID（逻辑外键→sys_store_admin.id）',
  `customer_level`      TINYINT       NOT NULL DEFAULT 0             COMMENT '客户等级：0=普通，1=VIP，2=SVIP',
  `is_blacklist`        TINYINT(1)    NOT NULL DEFAULT 0             COMMENT '是否黑名单：0=否，1=是',
  `blacklist_reason`    VARCHAR(200)                                 COMMENT '拉黑原因',
  `remark`              TEXT                                         COMMENT '备注',
  `is_deleted`          TINYINT(1)    NOT NULL DEFAULT 0             COMMENT '逻辑删除：0=未删除，1=已删除',
  `create_time`         DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time`         DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `create_user_id`      VARCHAR(32)                                  COMMENT '创建人用户ID',
  `update_user_id`      VARCHAR(32)                                  COMMENT '最后更新人用户ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_customer_no` (`customer_no`),
  KEY `idx_mobile` (`mobile`),
  KEY `idx_belong_store_id` (`belong_store_id`),
  KEY `idx_belong_seat_id` (`belong_seat_id`),
  KEY `idx_source_type` (`source_type`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户主表';

DROP TABLE IF EXISTS `cus_family_member`;
CREATE TABLE `cus_family_member` (
  `id`                  BIGINT        NOT NULL                       COMMENT '主键ID（雪花算法）',
  `customer_id`         BIGINT        NOT NULL                       COMMENT '所属客户ID（逻辑外键→cus_customer.id）',
  `member_name`         VARCHAR(100)                                 COMMENT '成员姓名',
  `relation`            VARCHAR(30)                                  COMMENT '与客户关系（如：本人、丈夫、母亲、孩子）',
  `gender`              TINYINT       NOT NULL DEFAULT 0             COMMENT '性别：0=未知，1=男，2=女',
  `birthday`            DATE                                         COMMENT '出生日期',
  `id_card`             VARCHAR(64)                                  COMMENT '身份证号（脱敏存储）',
  `mobile`              VARCHAR(20)                                  COMMENT '联系手机号',
  `expected_due_date`   DATE                                         COMMENT '预产期（月嫂服务时填写）',
  `actual_birth_date`   DATE                                         COMMENT '实际分娩日期',
  `delivery_hospital`   VARCHAR(200)                                 COMMENT '分娩医院',
  `delivery_type`       VARCHAR(20)                                  COMMENT '分娩方式：NATURAL=顺产，CESAREAN=剖腹产',
  `baby_count`          TINYINT       NOT NULL DEFAULT 1             COMMENT '宝宝数量（多胞胎）',
  `health_condition`    TEXT                                         COMMENT '健康状况/特殊需求描述',
  `is_deleted`          TINYINT(1)    NOT NULL DEFAULT 0             COMMENT '逻辑删除：0=未删除，1=已删除',
  `create_time`         DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time`         DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `create_user_id`      VARCHAR(32)                                  COMMENT '创建人用户ID',
  `update_user_id`      VARCHAR(32)                                  COMMENT '最后更新人用户ID',
  PRIMARY KEY (`id`),
  KEY `idx_customer_id` (`customer_id`),
  KEY `idx_expected_due_date` (`expected_due_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户家庭成员信息表';

DROP TABLE IF EXISTS `cus_address`;
CREATE TABLE `cus_address` (
  `id`              BIGINT        NOT NULL                       COMMENT '主键ID（雪花算法）',
  `customer_id`     BIGINT        NOT NULL                       COMMENT '所属客户ID（逻辑外键→cus_customer.id）',
  `address_label`   VARCHAR(50)                                  COMMENT '地址标签（如：家、公司、月子中心）',
  `province`        VARCHAR(50)                                  COMMENT '省',
  `city`            VARCHAR(50)                                  COMMENT '市',
  `district`        VARCHAR(50)                                  COMMENT '区/县',
  `street`          VARCHAR(100)                                 COMMENT '街道/乡镇',
  `detail`          VARCHAR(500)  NOT NULL                       COMMENT '详细地址',
  `longitude`       DECIMAL(10,7)                                COMMENT '经度',
  `latitude`        DECIMAL(10,7)                                COMMENT '纬度',
  `contact_name`    VARCHAR(50)                                  COMMENT '联系人姓名',
  `contact_phone`   VARCHAR(20)                                  COMMENT '联系人电话',
  `is_default`      TINYINT(1)    NOT NULL DEFAULT 0             COMMENT '是否默认地址：0=否，1=是',
  `is_deleted`      TINYINT(1)    NOT NULL DEFAULT 0             COMMENT '逻辑删除：0=未删除，1=已删除',
  `create_time`     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time`     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `create_user_id`  VARCHAR(32)                                  COMMENT '创建人用户ID',
  `update_user_id`  VARCHAR(32)                                  COMMENT '最后更新人用户ID',
  PRIMARY KEY (`id`),
  KEY `idx_customer_id` (`customer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户地址薄';

DROP TABLE IF EXISTS `cus_tag`;
CREATE TABLE `cus_tag` (
  `id`              BIGINT        NOT NULL                       COMMENT '主键ID（雪花算法）',
  `tag_name`        VARCHAR(50)   NOT NULL                       COMMENT '标签名称',
  `tag_code`        VARCHAR(50)   NOT NULL                       COMMENT '标签编码（唯一）',
  `tag_group`       VARCHAR(50)                                  COMMENT '标签分组（如：来源、意向、行为）',
  `tag_color`       VARCHAR(20)                                  COMMENT '标签颜色（前端展示用）',
  `sort_order`      INT           NOT NULL DEFAULT 0             COMMENT '排序',
  `is_system`       TINYINT(1)    NOT NULL DEFAULT 0             COMMENT '是否系统内置标签：0=自定义，1=系统内置',
  `status`          TINYINT       NOT NULL DEFAULT 1             COMMENT '状态：0=停用，1=启用',
  `is_deleted`      TINYINT(1)    NOT NULL DEFAULT 0             COMMENT '逻辑删除：0=未删除，1=已删除',
  `create_time`     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time`     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `create_user_id`  VARCHAR(32)                                  COMMENT '创建人用户ID',
  `update_user_id`  VARCHAR(32)                                  COMMENT '最后更新人用户ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_tag_code` (`tag_code`),
  KEY `idx_tag_group` (`tag_group`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户标签定义表';

DROP TABLE IF EXISTS `cus_customer_tag`;
CREATE TABLE `cus_customer_tag` (
  `id`              BIGINT        NOT NULL                       COMMENT '主键ID（雪花算法）',
  `customer_id`     BIGINT        NOT NULL                       COMMENT '客户ID（逻辑外键→cus_customer.id）',
  `tag_id`          BIGINT        NOT NULL                       COMMENT '标签ID（逻辑外键→cus_tag.id）',
  `tag_value`       VARCHAR(200)                                 COMMENT '标签值（部分标签有具体取值）',
  `create_time`     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `create_user_id`  VARCHAR(32)                                  COMMENT '创建人用户ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_customer_tag` (`customer_id`, `tag_id`),
  KEY `idx_customer_id` (`customer_id`),
  KEY `idx_tag_id` (`tag_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户与标签关联表';


-- ############################################################
