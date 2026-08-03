-- ============================================================
-- AI-Powered Student Exam Performance Tracker
-- MySQL Database Schema
-- ============================================================
-- Run with:  mysql -u root -p < database.sql
-- Requires MySQL 8.0+
-- ============================================================

CREATE DATABASE IF NOT EXISTS student_tracker
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE student_tracker;

-- ------------------------------------------------------------
-- Table: admins  (application users / authentication)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS admins (
    admin_id        INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    email           VARCHAR(120) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(120) NOT NULL,
    role            ENUM('admin', 'staff') DEFAULT 'admin',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login      TIMESTAMP NULL,
    INDEX idx_admins_username (username)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Table: departments
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS departments (
    department_id   INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Table: students
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS students (
    student_id      VARCHAR(20)  PRIMARY KEY,
    name            VARCHAR(120) NOT NULL,
    gender          ENUM('Male', 'Female', 'Other') NOT NULL,
    department_id   INT NOT NULL,
    semester        TINYINT NOT NULL CHECK (semester BETWEEN 1 AND 8),
    email           VARCHAR(120),
    phone           VARCHAR(20),
    date_of_birth   DATE,
    admission_year  YEAR,
    photo_url       VARCHAR(255),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_students_name (name),
    INDEX idx_students_department (department_id),
    INDEX idx_students_semester (semester)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Table: subjects
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS subjects (
    subject_id      INT AUTO_INCREMENT PRIMARY KEY,
    subject_name    VARCHAR(120) NOT NULL,
    subject_code    VARCHAR(20) NOT NULL UNIQUE,
    department_id   INT NOT NULL,
    semester        TINYINT NOT NULL CHECK (semester BETWEEN 1 AND 8),
    credits         TINYINT DEFAULT 3,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_subjects_department (department_id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Table: marks
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS marks (
    mark_id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id               VARCHAR(20) NOT NULL,
    subject_id               INT NOT NULL,
    attendance_percentage    DECIMAL(5,2) DEFAULT 0,
    study_hours              DECIMAL(5,2) DEFAULT 0,
    assignment_marks         DECIMAL(5,2) DEFAULT 0,
    quiz_marks               DECIMAL(5,2) DEFAULT 0,
    lab_marks                DECIMAL(5,2) DEFAULT 0,
    internal_marks           DECIMAL(5,2) DEFAULT 0,
    previous_semester_marks  DECIMAL(5,2) DEFAULT 0,
    project_marks            DECIMAL(5,2) DEFAULT 0,
    final_exam_marks         DECIMAL(5,2) DEFAULT 0,
    total_marks              DECIMAL(6,2) GENERATED ALWAYS AS (
        assignment_marks + quiz_marks + lab_marks + internal_marks + project_marks + final_exam_marks
    ) STORED,
    percentage               DECIMAL(5,2) GENERATED ALWAYS AS (
        total_marks / 130 * 100
    ) STORED,
    grade                    VARCHAR(2),
    pass_fail                ENUM('Pass', 'Fail'),
    created_at               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at               TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE KEY uq_student_subject (student_id, subject_id),
    INDEX idx_marks_student (student_id),
    INDEX idx_marks_subject (subject_id),
    INDEX idx_marks_pass_fail (pass_fail)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Table: attendance  (monthly attendance log, separate from marks snapshot)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id        VARCHAR(20) NOT NULL,
    subject_id        INT NOT NULL,
    month             VARCHAR(20) NOT NULL,
    year              YEAR NOT NULL,
    classes_held      INT NOT NULL DEFAULT 0,
    classes_attended  INT NOT NULL DEFAULT 0,
    percentage        DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN classes_held = 0 THEN 0 ELSE classes_attended / classes_held * 100 END
    ) STORED,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE KEY uq_attendance (student_id, subject_id, month, year),
    INDEX idx_attendance_student (student_id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Table: predictions  (stores AI prediction history for auditability)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id        VARCHAR(20) NOT NULL,
    subject_id        INT NULL,
    predicted_score   DECIMAL(5,2),
    predicted_result  ENUM('Pass', 'Fail'),
    confidence        DECIMAL(5,2),
    risk_level        ENUM('Low', 'Medium', 'High', 'Unknown'),
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_predictions_student (student_id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Sample seed data
-- ------------------------------------------------------------
INSERT INTO departments (name) VALUES
    ('Computer Science'), ('Information Technology'), ('Electronics'),
    ('Mechanical'), ('Civil')
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO admins (username, email, password_hash, full_name, role)
VALUES ('admin', 'admin@school.edu', '$2b$12$replace_with_generated_hash', 'System Administrator', 'admin')
ON DUPLICATE KEY UPDATE username = VALUES(username);
-- NOTE: The Flask app creates this admin account automatically on first run
-- using werkzeug.security.generate_password_hash — see app.py `seed_default_admin()`.

INSERT INTO subjects (subject_name, subject_code, department_id, semester, credits) VALUES
    ('Data Structures', 'CS301', 1, 3, 4),
    ('Operating Systems', 'CS302', 1, 3, 4),
    ('DBMS', 'CS303', 1, 4, 4),
    ('Computer Networks', 'CS304', 1, 4, 3),
    ('Machine Learning', 'CS305', 1, 5, 4)
ON DUPLICATE KEY UPDATE subject_name = VALUES(subject_name);

INSERT INTO students (student_id, name, gender, department_id, semester, email, admission_year) VALUES
    ('STU1001', 'Manav Joshi', 'Male', 1, 3, 'manav.joshi@school.edu', 2023),
    ('STU1002', 'Rohan Pillai', 'Male', 1, 3, 'rohan.pillai@school.edu', 2023)
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- ------------------------------------------------------------
-- Entity Relationship Diagram (Mermaid) — also included in README.md
-- ------------------------------------------------------------
-- erDiagram
--     DEPARTMENTS ||--o{ STUDENTS : has
--     DEPARTMENTS ||--o{ SUBJECTS : offers
--     STUDENTS ||--o{ MARKS : receives
--     SUBJECTS ||--o{ MARKS : "graded in"
--     STUDENTS ||--o{ ATTENDANCE : logs
--     SUBJECTS ||--o{ ATTENDANCE : "tracked for"
--     STUDENTS ||--o{ PREDICTIONS : "predicted for"
--     SUBJECTS ||--o{ PREDICTIONS : "predicted in"
