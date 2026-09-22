-- =========================================================
-- GYM MEMBERSHIP MANAGEMENT SYSTEM - DATABASE SQL SCRIPT
-- Database: gym_db
-- Table: members
-- =========================================================

-- Create Database
CREATE DATABASE IF NOT EXISTS gym_db;
USE gym_db;

-- Drop Table if exists
DROP TABLE IF EXISTS members;

-- Create Members Table
CREATE TABLE members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15) NOT NULL,
    password VARCHAR(255) NOT NULL,
    membership VARCHAR(50) NOT NULL,
    join_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Active'
);

-- Insert Sample Test Data
INSERT INTO members (name, email, phone, password, membership, join_date, status) 
VALUES 
('Alex Johnson', 'alex@fitnesshub.com', '9876543210', 'password123', 'Yearly', CURDATE(), 'Active'),
('Sarah Connor', 'sarah@fitnesshub.com', '9123456789', 'sarah2026', 'Quarterly', CURDATE(), 'Active'),
('Mike Tyson', 'mike@fitnesshub.com', '9988776655', 'ironmike', 'Monthly', CURDATE(), 'Active');

-- Verify Sample Data
SELECT * FROM members;
