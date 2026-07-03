CREATE DATABASE IF NOT EXISTS gzdouban
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;

USE gzdouban;

CREATE TABLE IF NOT EXISTS movies (
  id INT AUTO_INCREMENT PRIMARY KEY,
  directors VARCHAR(255),
  rate VARCHAR(255),
  title VARCHAR(255),
  casts VARCHAR(255),
  cover VARCHAR(255),
  `year` VARCHAR(255),
  types VARCHAR(255),
  country VARCHAR(255),
  lang VARCHAR(255),
  `time` VARCHAR(255),
  movieTime VARCHAR(255),
  commentLen VARCHAR(255),
  star VARCHAR(255),
  summary VARCHAR(2555),
  imgList VARCHAR(2555),
  detailLink VARCHAR(2555)
) DEFAULT CHARSET = utf8mb4;
