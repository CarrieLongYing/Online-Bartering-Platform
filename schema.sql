CREATE USER IF NOT EXISTS gatechUser@localhost IDENTIFIED BY 'mydb234';
DROP DATABASE IF EXISTS `cs6400_summer22_team040`; 
SET default_storage_engine=InnoDB;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS cs6400_summer22_team040 
    DEFAULT CHARACTER SET utf8mb4 
    DEFAULT COLLATE utf8mb4_unicode_ci;
USE cs6400_summer22_team040;

GRANT SELECT, INSERT, UPDATE, DELETE, FILE ON *.* TO 'gatechUser'@'localhost';
GRANT ALL PRIVILEGES ON `gatechuser`.* TO 'gatechUser'@'localhost';
GRANT ALL PRIVILEGES ON `cs6400_summer22_team040`.* TO 'gatechUser'@'localhost';
FLUSH PRIVILEGES;

CREATE TABLE `User` (
  email varchar(250) NOT NULL,
  nickname varchar(100) NOT NULL,
  password varchar(30) NOT NULL,
  first_name varchar(100) NOT NULL,
  last_name varchar(100) NOT NULL,
  postal_code varchar(250) NOT NULL,
  PRIMARY KEY (email),
  UNIQUE KEY (nickname)
);

CREATE TABLE `PostalCode` (
  postal_code varchar(250) NOT NULL,
  longitude double NOT NULL,
  latitude double NOT NULL,
  city varchar(100) NOT NULL,
  state varchar(100) NOT NULL,
  PRIMARY KEY (postal_code)
);

CREATE TABLE `Trade` (
  proposer_email varchar(250) NOT NULL,
  counterparty_email varchar(250) NOT NULL,
  proposed_itemID int(10) NOT NULL,
  desired_itemID int(10) NOT NULL,
  proposed_date datetime NOT NULL,
  accepted_rejected_date datetime DEFAULT NULL,
  response_time int(10) DEFAULT NULL,
  trade_status ENUM('0', '1', '2') NOT NULL,
  tradeID int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`tradeID`),
  UNIQUE KEY (proposer_email,counterparty_email,proposed_itemID, desired_itemID)
);



CREATE TABLE `Item` (
  itemID int(10) NOT NULL AUTO_INCREMENT,
  user_email varchar(250) NOT NULL,
  title varchar(250) NOT NULL,
  game_type varchar(250) NOT NULL,
  item_condition varchar(250) NOT NULL,
  description varchar(8000) DEFAULT NULL,
  PRIMARY KEY (itemID)
);

CREATE TABLE `VideoGame` (
  itemID int(10) NOT NULL,
  platform_type varchar(250) NOT NULL,
  media varchar(250) NOT NULL,
  PRIMARY KEY (itemID)
);

CREATE TABLE `CollectiableCardGame` (
  itemID int(10) NOT NULL,
  number_of_offered_card int(10) NOT NULL,
  PRIMARY KEY (itemID)
);

CREATE TABLE `ComputerGame` (
  itemID int(10) NOT NULL,
  platform_type varchar(250) NOT NULL,
  PRIMARY KEY(itemID)
);

CREATE TABLE `Platform`(
  platform_type varchar(250) NOT NULL,
  PRIMARY KEY(platform_type)
);

CREATE TABLE `Distance` (
  postal_code_from varchar(250) NOT NULL,
  postal_code_to varchar(250) NOT NULL,
  distance double NOT NULL,
  PRIMARY KEY (postal_code_from, postal_code_to)
);


CREATE TABLE `UserStatistics` (
  email varchar(250) NOT NULL,
  number_of_completed_trade_proposer int(10),
  number_of_completed_trade_counterparty int(10),
  response_time decimal(10,1) DEFAULT NULL,
  number_of_unaccepted_trade_counterparty int(10),
  user_rank varchar(250) NOT NULL,
  PRIMARY KEY (email)
);
-- Constraints Foreign Keys: FK_ChildTable_childColumn_ParentTable_parentColumn

ALTER TABLE User
  ADD CONSTRAINT fk_User_postalcode_PostalCode_postalcode FOREIGN KEY (postal_code) REFERENCES PostalCode (postal_code) ON DELETE CASCADE ON UPDATE CASCADE;


ALTER TABLE Distance
  ADD CONSTRAINT fk_Distance_PostalCodeFrom_PostalCode_postalcode FOREIGN KEY (postal_code_from) REFERENCES PostalCode (postal_code) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT fk_Distance_PostalCodeTo_PostalCode_postalcode FOREIGN KEY (postal_code_to) REFERENCES PostalCode (postal_code) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE Trade
  ADD CONSTRAINT fk_Trade_proposeremail_User_email FOREIGN KEY (proposer_email)  REFERENCES User (email) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT fk_Trade_counterpartyemail_User_email FOREIGN KEY (counterparty_email) REFERENCES User (email) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT fk_Trade_proposeditemid_Item_itemid FOREIGN KEY (proposed_itemID) REFERENCES Item (itemID) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT fk_Trade_desireditemid_Item_itemid FOREIGN KEY (desired_itemID) REFERENCES Item (itemID) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE Item
   ADD CONSTRAINT fk_Item_useremail_User_email FOREIGN KEY (user_email) REFERENCES User (email) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE UserStatistics
  ADD CONSTRAINT fk_UserStatistics_email_User_email FOREIGN KEY (email) REFERENCES User (email) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE ComputerGame
    ADD CONSTRAINT fk_ComputerGame_platformtype_Platform_platformtype FOREIGN KEY (platform_type) REFERENCES Platform (platform_type) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE VideoGame 
   ADD CONSTRAINT fk_VideoGame_platformtype_Platform_platformtype FOREIGN KEY (platform_type) REFERENCES Platform (platform_type) ON DELETE CASCADE ON UPDATE CASCADE;




