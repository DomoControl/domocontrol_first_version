PRAGMA foreign_keys=ON;
CREATE TABLE "pi_program" ("id" INTEGER PRIMARY KEY  NOT NULL ,"in_id" INTEGER,"in_delay" INTEGER NOT NULL  DEFAULT (0) ,"in_inverted" BOOL DEFAULT (0) ,
"out_id" INTEGER,"out_inverted" BOOL DEFAULT (0) ,"type_id" INTEGER NOT NULL  DEFAULT (1) ,"timestamp" DATETIME DEFAULT (CURRENT_TIMESTAMP) ,
"name" VARCHAR,"description" VARCHAR, "timer" VARCHAR DEFAULT '0-0-0-0', "chrono" VARCHAR DEFAULT '0-0-0-0-0-0',
FOREIGN KEY("in_id", "out_id") REFERENCES "pi_board_io"("id","id"),
FOREIGN KEY("type_id") REFERENCES "pi_type"("id")
);





PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
CREATE TABLE "pi_prog" ("id" INTEGER PRIMARY KEY  NOT NULL ,"gpio_id" INTEGER NOT NULL ,"in_out" BOOL NOT NULL  DEFAULT (0) ,"type_id" INTEGER,"default_state" BOOL DEFAULT (0) ,"active" BOOL NOT NULL  DEFAULT (0) ,"timestamp" DATETIME NOT NULL  DEFAULT (CURRENT_TIMESTAMP) ,"name" VARCHAR,"timer" VARCHAR, "crono" VARCHAR);
CREATE TABLE "pi_type" ("id" INTEGER PRIMARY KEY  NOT NULL ,"name" VARCHAR NOT NULL  DEFAULT (null) );
INSERT INTO "pi_type" VALUES(1,'ON / OFF');
INSERT INTO "pi_type" VALUES(2,'Timer');
INSERT INTO "pi_type" VALUES(3,'Crono');
INSERT INTO "pi_type" VALUES(4,'Remote');
CREATE TABLE "pi_gpio" ("id" INTEGER PRIMARY KEY  NOT NULL ,"pin" INTEGER NOT NULL ,"name" VARCHAR DEFAULT (null) ,"gpio" VARCHAR DEFAULT (null) ,"timestamp" DATETIME NOT NULL  DEFAULT (CURRENT_TIMESTAMP) ,"type" VARCHAR,"active" BOOL DEFAULT (0) );
INSERT INTO "pi_gpio" VALUES(1,1,'VCC 3.3','','2014-05-19 19:44:13',NULL,0);
INSERT INTO "pi_gpio" VALUES(2,2,'VCC 5','','2014-05-19 19:46:10',NULL,0);
INSERT INTO "pi_gpio" VALUES(3,3,'GPIO2','2','2014-05-19 19:46:24','IN/OUT/I2C_SDA',0);
INSERT INTO "pi_gpio" VALUES(4,4,'VCC 5','','2014-05-19 19:50:58',NULL,0);
INSERT INTO "pi_gpio" VALUES(5,5,'GPIO3','3','2014-05-19 19:51:10','IN/OUT/I2C_SCL',0);
INSERT INTO "pi_gpio" VALUES(6,6,'GND','','2014-05-19 19:51:26',NULL,0);
INSERT INTO "pi_gpio" VALUES(7,7,'Rele 1','4','2014-05-19 19:51:52PRAGMA foreign_keys=','IN/OUT GPIO4',0);
INSERT INTO "pi_gpio" VALUES(8,8,'GPIO14','14','2014-05-19 19:52:17','IN/OUT/UART_TXD',0);
INSERT INTO "pi_gpio" VALUES(9,9,'GND','','2014-05-19 19:52:37',NULL,0);
INSERT INTO "pi_gpio" VALUES(10,10,'GPIO15','15','2014-05-19 19:53:09','IN/OUT/UART_RXD',0);
INSERT INTO "pi_gpio" VALUES(11,11,'GPIO17','17','2014-05-19 19:53:33','IN/OUT',0);
INSERT INTO "pi_gpio" VALUES(12,12,'Rele 2','18','2014-05-19 19:53:44','IN/OUT/PWM GPIO18',0);
INSERT INTO "pi_gpio" VALUES(13,13,'Rele 3','27','2014-05-19 19:53:54','IN/OUT GPIO27',0);
INSERT INTO "pi_gpio" VALUES(14,14,'GND','','2014-05-19 19:54:06',NULL,0);
INSERT INTO "pi_gpio" VALUES(15,15,'Rele 4','22','2014-05-19 19:54:57','IN/OUT GPIO22',0);
INSERT INTO "pi_gpio" VALUES(16,16,'Rele 5','23','2014-05-19 19:55:08','IN/OUT GPIO23',0);
INSERT INTO "pi_gpio" VALUES(17,17,'VCC 3.3','','2014-05-19 19:55:21',NULL,0);
INSERT INTO "pi_gpio" VALUES(18,18,'Rele 6','24','2014-05-19 19:55:24','IN/OUT GPIO24',0);
INSERT INTO "pi_gpio" VALUES(19,19,'GPIO10','10','2014-05-19 19:56:50','IN/OUT/SPI_MOSI',0);
INSERT INTO "pi_gpio" VALUES(20,20,'GND','','2014-05-19 19:57:04',NULL,0);
INSERT INTO "pi_gpio" VALUES(21,21,'GPIO9','9','2014-05-19 19:57:18','IN/OUT/SPI_MISO',0);
INSERT INTO "pi_gpio" VALUES(22,22,'Rele 7','25','2014-05-19 19:57:32','IN/OUT GPIO25',0);
INSERT INTO "pi_gpio" VALUES(23,23,'GPIO11','11','2014-05-19 19:57:45','IN/OUT/SPI_CLK',0);
INSERT INTO "pi_gpio" VALUES(24,24,'GPIO8','8','2014-05-19 19:57:57','IN/OUT/SPI_CE0',0);
INSERT INTO "pi_gpio" VALUES(25,25,'GND','','2014-05-19 19:58:08',NULL,0);
INSERT INTO "pi_gpio" VALUES(26,26,'GPIO7','7','2014-05-19 19:58:21','IN/OUT/SPI_CE1',0);
CREATE TABLE "pi_user" ("id" INTEGER PRIMARY KEY  NOT NULL ,"username" VARCHAR NOT NULL  DEFAULT (null) ,"name" VARCHAR NOT NULL ,"surname" VARCHAR NOT NULL ,"timestamp" DATETIME NOT NULL  DEFAULT (CURRENT_TIMESTAMP) ,"password" VARCHAR,"privileges" VARCHAR DEFAULT (null) );
INSERT INTO "pi_user" VALUES(1,'luca','Luca1','Subiaco','2014-05-19 19:29:04','123','1;2;3;4;5;15');
INSERT INTO "pi_user" VALUES(2,'user','prova','prova','2014-06-16 19:09:22','user',NULL);

CREATE TABLE "pi_area" ("id" INTEGER PRIMARY KEY  NOT NULL ,"name" VARCHAR NOT NULL  DEFAULT (null) ,"description" VARCHAR NOT NULL  DEFAULT (null) ,"timestamp" DATETIME NOT NULL  DEFAULT (CURRENT_TIMESTAMP) );
INSERT INTO "pi_area" VALUES(1,'bedroom','Bedroom','2014-09-05 20:17:00');
INSERT INTO "pi_area" VALUES(2,'kitchen','Kitchen','2014-09-05 21:45:51');
INSERT INTO "pi_area" VALUES(3,'name','description','2014-09-09 21:52:27');
INSERT INTO "pi_area" VALUES(4,'name','description','2014-09-09 21:52:29');
INSERT INTO "pi_area" VALUES(5,'name','description','2014-09-09 21:52:30');
INSERT INTO "pi_area" VALUES(6,'name','description','2014-09-09 21:52:32');
CREATE TABLE "pi_privileges" ("id" INTEGER PRIMARY KEY  NOT NULL ,"name" VARCHAR,"description" VARCHAR,"timestamp" DATETIME DEFAULT (CURRENT_TIMESTAMP) );
INSERT INTO "pi_privileges" VALUES(1,'enable','User_enable','2014-09-06 11:34:50');
INSERT INTO "pi_privileges" VALUES(2,'superuser','SuperUser','2014-09-06 11:34:50');
INSERT INTO "pi_privileges" VALUES(3,'status','Status','2014-09-06 11:34:50');
INSERT INTO "pi_privileges" VALUES(4,'setup','Setup','2014-09-06 11:34:50');
INSERT INTO "pi_privileges" VALUES(5,'user_setup','User_Setup','2014-09-06 11:34:50');
INSERT INTO "pi_privileges" VALUES(6,'area_setup','Area_setup','2014-09-06 11:34:50');
INSERT INTO "pi_privileges" VALUES(7,'group
group_privileges','group
Group_privileges','2014-09-06 11:43:48');
INSERT INTO "pi_privileges" VALUES(8,'device_setup','Device_setup','2014-09-06 11:46:11');
INSERT INTO "pi_privileges" VALUES(9,'input_setup','Input_setup','2014-09-06 11:46:34');
INSERT INTO "pi_privileges" VALUES(10,'email_sms_setup','Email_SMS_setup','2014-09-06 11:46:54');
INSERT INTO "pi_privileges" VALUES(16,'log','Trace_Log','2014-09-06 11:34:50');
CREATE TABLE "pi_io_type" ("id" INTEGER PRIMARY KEY  NOT NULL ,"name" VARCHAR,"description" VARCHAR,"timestamp" DATETIME NOT NULL  DEFAULT (CURRENT_TIMESTAMP) );
INSERT INTO "pi_io_type" VALUES(1,'in','IN','2014-09-08 13:13:24');
INSERT INTO "pi_io_type" VALUES(2,'out','OUT','2014-09-08 13:13:45');
CREATE TABLE "pi_program" ("id" INTEGER PRIMARY KEY  NOT NULL ,"in_id" INTEGER,"in_delay" INTEGER NOT NULL  DEFAULT (0) ,"in_inverted" BOOL DEFAULT (0) ,"out_id" INTEGER,"out_inverted" BOOL DEFAULT (0) ,"type_id" INTEGER NOT NULL  DEFAULT (1) ,"timestamp" DATETIME DEFAULT (CURRENT_TIMESTAMP) ,"name" VARCHAR,"description" VARCHAR, "timer" VARCHAR DEFAULT '0-0-0-0', "chrono" VARCHAR DEFAULT '0-0-0-0-0-0');
INSERT INTO "pi_program" VALUES(2,11,10,1,13,0,3,'2014-09-13 07:25:45','prog1','Programma%20prova','1;5;2;1','5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;0;0;0;0;0;0;5;2;1;5;2;1;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0');
INSERT INTO "pi_program" VALUES(3,12,5,0,14,0,2,'2014-09-13 08:59:45','prog2','programma%202','2;1;5;2;9','5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;9');
INSERT INTO "pi_program" VALUES(4,17,0,0,13,0,1,'2014-09-15 20:36:59','On-Off','Programma_ON_OFF','2;1;5;2;9','5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;1;5;2;9');
CREATE TABLE "pi_board" ("id" INTEGER PRIMARY KEY  NOT NULL ,"name" VARCHAR,"description" VARCHAR,"enable" BOOL NOT NULL  DEFAULT (0) ,"timestamp" DATETIME DEFAULT (CURRENT_TIMESTAMP) ,"address" VARCHAR DEFAULT (0) ,"board_type" INTEGER NOT NULL  DEFAULT (0) );
INSERT INTO "pi_board" VALUES(1,'I2C_out','I2C_local_board_out',1,'2014-09-08 15:01:30','32',1);
INSERT INTO "pi_board" VALUES(2,'I2C_in','I2C_local_board_in',1,'2014-09-12 22:46:54','33',1);
CREATE TABLE pi_board_io (
    "id" INTEGER NOT NULL,
    "io_type_id" INTEGER NOT NULL DEFAULT ('null'),
    "name" VARCHAR NOT NULL,
    "description" VARCHAR,
    "enable" BOOL,
    "timestamp" DATETIME NOT NULL DEFAULT ('CURRENT_TIMESTAMP'),
    "board_id" INTEGER,
    "address" VARCHAR DEFAULT (0)
);
INSERT INTO "pi_board_io" VALUES(12,1,'IN2','Input_2',1,'2014-09-12 22:47:08',2,'2');
INSERT INTO "pi_board_io" VALUES(13,2,'OUT1','Output_1',1,'2014-09-13 12:23:40',1,'1');
INSERT INTO "pi_board_io" VALUES(14,2,'OUT2','Output_2',1,'2014-09-13 12:25:59',1,'2');
INSERT INTO "pi_board_io" VALUES(15,1,'IN3','Input_3',1,'2014-09-18 19:42:06',2,'3');
INSERT INTO "pi_board_io" VALUES(16,2,'OUT3','Output_3',1,'2014-09-18 19:42:38',1,'3');
INSERT INTO "pi_board_io" VALUES(17,1,'IN1','Input_1',1,'2014-09-18 19:47:32',2,'1');
COMMIT;
