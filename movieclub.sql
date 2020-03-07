/*
 Navicat Premium Data Transfer

 Source Server         : mysql
 Source Server Type    : MySQL
 Source Server Version : 80016
 Source Host           : localhost:3306
 Source Schema         : movieclub

 Target Server Type    : MySQL
 Target Server Version : 80016
 File Encoding         : 65001

 Date: 23/02/2020 19:54:26
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for m_eplnk
-- ----------------------------
DROP TABLE IF EXISTS `m_eplnk`;
CREATE TABLE `m_eplnk` (
  `uid` varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `tpid` varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `slnkid` varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `epno` int(11) DEFAULT NULL,
  `title` varbinary(100) DEFAULT NULL,
  `playurl` varchar(500) DEFAULT NULL,
  `playgate` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `args` varchar(100) DEFAULT NULL,
  `pubdate` bigint(14) DEFAULT NULL,
  `latime` bigint(14) DEFAULT NULL,
  `isoff` int(11) DEFAULT '0',
  `hot` int(11) DEFAULT '0',
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for m_sourlnk
-- ----------------------------
DROP TABLE IF EXISTS `m_sourlnk`;
CREATE TABLE `m_sourlnk` (
  `uid` varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `tpid` varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `name` varchar(30) DEFAULT NULL,
  `lnk_code` varchar(100) DEFAULT NULL,
  `lnk_url` varchar(500) DEFAULT NULL,
  `pubdate` bigint(20) DEFAULT NULL,
  `latime` bigint(20) DEFAULT NULL,
  `isoff` int(4) DEFAULT '0',
  PRIMARY KEY (`uid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for m_titlepage
-- ----------------------------
DROP TABLE IF EXISTS `m_titlepage`;
CREATE TABLE `m_titlepage` (
  `uid` varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `title` varchar(250) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `alias` varchar(500) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `imgs` varchar(500) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `genres` int(11) DEFAULT NULL,
  `directors` varchar(400) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `actors` varchar(1000) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `area` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `subtype` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `year` int(11) DEFAULT NULL,
  `summary` varchar(8010) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `mocode` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `pubdate` bigint(20) DEFAULT NULL,
  `latime` bigint(20) DEFAULT NULL,
  `isoff` int(11) DEFAULT '0',
  `hot` int(11) DEFAULT '0',
  `dbid` varchar(50) DEFAULT '',
  `imdb` varchar(50) DEFAULT '',
  PRIMARY KEY (`uid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

SET FOREIGN_KEY_CHECKS = 1;
