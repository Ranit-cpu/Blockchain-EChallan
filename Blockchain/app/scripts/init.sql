-- MySQL initialization script
CREATE DATABASE IF NOT EXISTS echallan_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'echallan_user'@'%' IDENTIFIED BY 'echallan_pass';
GRANT ALL PRIVILEGES ON echallan_db.* TO 'echallan_user'@'%';
FLUSH PRIVILEGES;