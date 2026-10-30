-- PROBLEMA:
-- Kalat-kalat ang multa sa school (ID replacement, nasirang gamit, huling
-- bayad, atbp.). Nasa notebook lang ang record kaya nawawala ang resibo,
-- hindi natrack ang partial payment, at walang aging kung sino ang matagal
-- nang may utang. Hindi rin malaman ng office kung magkano ang nakolekta.
--
-- SOLUSYON:
-- Isang ledger ng fines at payments. Ang balanse ay
-- (amount - SUM(amount_paid)), kaya laging tama kahit partial ang bayad.
-- May aging report (DATEDIFF), collection report per buwan/uri, top debtors,
-- at waive na may dahilan.

CREATE DATABASE IF NOT EXISTS school_fines_db;
USE school_fines_db;

CREATE TABLE IF NOT EXISTS students (
  student_id VARCHAR(20) PRIMARY KEY,
  full_name VARCHAR(150) NOT NULL,
  grade_level VARCHAR(20) NOT NULL,
  section VARCHAR(50) NOT NULL,
  date_added DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fine_types (
  type_id INT AUTO_INCREMENT PRIMARY KEY,
  type_name VARCHAR(80) NOT NULL UNIQUE,
  default_amount DECIMAL(8,2) NOT NULL DEFAULT 0.00,
  description VARCHAR(200) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS fines (
  fine_id INT AUTO_INCREMENT PRIMARY KEY,
  student_id VARCHAR(20) NOT NULL,
  type_id INT NOT NULL,
  description VARCHAR(200) DEFAULT NULL,
  amount DECIMAL(8,2) NOT NULL,
  date_issued DATE NOT NULL,
  due_date DATE NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'UNPAID',
  issued_by VARCHAR(150) NOT NULL,
  remarks VARCHAR(200) DEFAULT NULL,
  date_recorded DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_fn_student FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_fn_type FOREIGN KEY (type_id) REFERENCES fine_types(type_id) ON DELETE RESTRICT ON UPDATE CASCADE,
  INDEX idx_fn_status (status),
  INDEX idx_fn_due (due_date),
  INDEX idx_fn_student (student_id)
);

CREATE TABLE IF NOT EXISTS payments (
  payment_id INT AUTO_INCREMENT PRIMARY KEY,
  fine_id INT NOT NULL,
  amount_paid DECIMAL(8,2) NOT NULL,
  payment_date DATE NOT NULL,
  receipt_no VARCHAR(30) NOT NULL UNIQUE,
  received_by VARCHAR(150) NOT NULL,
  remarks VARCHAR(200) DEFAULT NULL,
  date_recorded DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_fn_payment_fine FOREIGN KEY (fine_id) REFERENCES fines(fine_id) ON DELETE RESTRICT ON UPDATE CASCADE,
  INDEX idx_fn_payment_fine (fine_id),
  INDEX idx_fn_payment_date (payment_date)
);

INSERT IGNORE INTO fine_types (type_name, default_amount, description) VALUES
('ID Replacement', 50.00, 'Kapalit ng nawalang o nasirang school ID'),
('Lost/Damaged Property', 100.00, 'Kapalit ng nawala o nasirang gamit ng school'),
('Late Return of Property', 5.00, 'Bawat araw na huli sa pagbabalik ng gamit'),
('Late Payment', 20.00, 'Huling bayad sa takdang oras'),
('Uniform/Grooming Violation', 30.00, 'Paglabag sa patakaran sa suot at ayos'),
('Others', 0.00, 'Iba pang multa, ilagay ang aktwal na halaga');
