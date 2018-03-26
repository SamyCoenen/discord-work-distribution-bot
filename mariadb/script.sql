-- Author: Samy Coenen
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

CREATE DATABASE IF NOT EXISTS `inventory` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `inventory`;

CREATE OR REPLACE TABLE `inventory`.`workers` (
    `worker_id` INT unsigned NOT NULL AUTO_INCREMENT ,
    `discord_id` VARCHAR(50) NOT NULL ,
    `password` VARCHAR(20) NOT NULL ,
    `rank` VARCHAR(20) ,
    `needs_payment` BOOLEAN NOT NULL,
    PRIMARY KEY (`worker_id`)
) ENGINE = InnoDB DEFAULT CHARSET=latin1;
    
CREATE UNIQUE INDEX discord_id ON workers(discord_id);  -- no multiple id's per worker
CREATE OR REPLACE TABLE `inventory`.`servers` (
    `server_id` INT unsigned NOT NULL AUTO_INCREMENT,
    `ip` VARCHAR(39) NOT NULL ,
    `port` INT NOT NULL,
    `needs_preparing` BOOLEAN NOT NULL,
    `rank` VARCHAR(20) ,
    `items` INT unsigned,
    PRIMARY KEY (`server_id`)
) ENGINE = InnoDB DEFAULT CHARSET=latin1;

CREATE OR REPLACE TABLE `inventory`.`worker_with_server` (
    `worker_id` INT unsigned NOT NULL ,
    `server_id` INT unsigned NOT NULL ,
    PRIMARY KEY (`server_id`),
    FOREIGN KEY (`worker_id`) REFERENCES workers(`worker_id`)
) ENGINE = InnoDB DEFAULT CHARSET=latin1;

CREATE OR REPLACE TABLE `inventory`.`sessions` ( 
    `session_id` INT unsigned NOT NULL AUTO_INCREMENT ,
    `worker_id` INT unsigned NOT NULL , 
    `start_date` DATETIME NOT NULL , 
    `end_date` DATETIME , 
    `items_start` INT unsigned,
    `items_end` INT unsigned,
    PRIMARY KEY (`session_id`),
    FOREIGN KEY (`worker_id`) REFERENCES workers(`worker_id`)
) ENGINE = InnoDB DEFAULT CHARSET=latin1;