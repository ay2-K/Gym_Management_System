import mysql.connector
from mysql.connector import errorcode

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password_here',  
}
DB_NAME = 'gym_db'

TABLES = {}

TABLES['plans'] = """
CREATE TABLE IF NOT EXISTS plans (
    plan_id INT AUTO_INCREMENT PRIMARY KEY,
    plan_name VARCHAR(20) NOT NULL,
    duration_months INT NOT NULL,
    price DECIMAL(5,2) NOT NULL
) ENGINE=InnoDB;
"""

TABLES['members'] = """
CREATE TABLE IF NOT EXISTS members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE,
    phone VARCHAR(15) UNIQUE,
    gender VARCHAR(10),
    join_date DATE,
    status VARCHAR(10) DEFAULT 'Active'
) ENGINE=InnoDB;
"""

TABLES['member_plans'] = """
CREATE TABLE IF NOT EXISTS member_plans (
    member_plan_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    plan_id INT NOT NULL,
    start_date DATE,
    end_date DATE,
    price_sold DECIMAL(5,2),
    is_active BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE
) ENGINE=InnoDB;
"""

TABLES['payments'] = """
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    amount DECIMAL(5,2) NOT NULL,
    payment_type VARCHAR(20),
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE
) ENGINE=InnoDB;
"""

TABLES['check_ins'] = """
CREATE TABLE IF NOT EXISTS check_ins (
    check_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE
) ENGINE=InnoDB;
"""

TABLES['trainers'] = """
CREATE TABLE IF NOT EXISTS trainers (
    trainer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    specialty VARCHAR(20),
    phone VARCHAR(15) UNIQUE,
    email VARCHAR(50) UNIQUE,
    hire_date DATE
) ENGINE=InnoDB;
"""

TABLES['gym_classes'] = """
CREATE TABLE IF NOT EXISTS gym_classes (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(20) NOT NULL UNIQUE,
    description TEXT
) ENGINE=InnoDB;
"""

TABLES['schedules'] = """
CREATE TABLE IF NOT EXISTS schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    trainer_id INT NOT NULL,
    day_of_week VARCHAR(15),
    start_time TIME,
    end_time TIME,
    
    FOREIGN KEY (class_id) REFERENCES gym_classes(class_id) ON DELETE CASCADE,
    FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id) ON DELETE CASCADE,
    UNIQUE KEY unique_trainer_slot (trainer_id, day_of_week, start_time)
) ENGINE=InnoDB;
"""

TABLES['enrollments'] = """
CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    schedule_id INT NOT NULL,
    
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id) ON DELETE CASCADE,
    UNIQUE KEY unique_member_booking (member_id, schedule_id)
) ENGINE=InnoDB;
"""


TABLES['equipments'] = """
CREATE TABLE IF NOT EXISTS equipments (
    equipment_id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_name VARCHAR(70) NOT NULL,
    quantity INT DEFAULT 0,
    purchase_date DATE
) ENGINE=InnoDB;
"""

PROCEDURES = {}

PROCEDURES['GetDashboardStats'] = """
CREATE PROCEDURE GetDashboardStats()
BEGIN
    SELECT 
        (SELECT COUNT(*) FROM members) as total_members,
        (SELECT COUNT(*) FROM members WHERE status = 'Active') as active_members,
        (SELECT COUNT(*) FROM members WHERE status = 'Passive') as passive_members,
        (SELECT COALESCE(SUM(amount), 0) FROM payments) as revenue,
        (SELECT COUNT(*) FROM plans) as total_plans,
        (SELECT COUNT(*) FROM gym_classes) as total_classes,
        (SELECT COUNT(*) FROM trainers) as trainers,
        (SELECT COALESCE(SUM(quantity), 0) FROM equipments) as equipments;
END
"""

PROCEDURES['GetMemberWithRemaining'] = """
CREATE PROCEDURE GetMemberWithRemaining(IN mem_id INT)
BEGIN
    SELECT 
        m.first_name, m.last_name, m.email, m.phone, 
        p.plan_name, mp.end_date, m.join_date, m.status,
        DATEDIFF(mp.end_date, CURDATE()) as remaining_days
    FROM members m
    LEFT JOIN member_plans mp ON m.member_id = mp.member_id 
        AND mp.is_active = TRUE
    LEFT JOIN plans p ON mp.plan_id = p.plan_id
    WHERE m.member_id = mem_id
    ORDER BY mp.end_date DESC LIMIT 1;
END
"""

PROCEDURES['CheckMemberAccess'] = """
CREATE PROCEDURE CheckMemberAccess(IN mem_id INT)
BEGIN
    DECLARE member_stat VARCHAR(10);
    DECLARE remaining INT;
    
    SELECT status INTO member_stat FROM members WHERE member_id = mem_id;
    
    SELECT DATEDIFF(MAX(end_date), CURDATE()) INTO remaining 
    FROM member_plans 
    WHERE member_id = mem_id AND is_active = TRUE;

    IF member_stat = 'Passive' THEN
        SELECT 'PASSIVE_MEMBER';
    ELSEIF remaining IS NULL OR remaining < 0 THEN
        SELECT 'EXPIRED';
    ELSE
        SELECT 'ACCESS_GRANTED';
    END IF;
END
"""

def create_database():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
        conn.close()
        
        DB_CONFIG['database'] = DB_NAME
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error:
        exit(1)

def create_tables_and_procedures(conn):
    cursor = conn.cursor()
    
    for _, ddl in TABLES.items():
        try:
            cursor.execute(ddl)
        except mysql.connector.Error:
            exit(1)
            
    for name, sql in PROCEDURES.items():
        try:
            cursor.execute(f"DROP PROCEDURE IF EXISTS {name}")
            cursor.execute(sql)
        except mysql.connector.Error:
            exit(1)

if __name__ == "__main__":
    cnx = create_database()
    if cnx and cnx.is_connected():
        create_tables_and_procedures(cnx)
        cnx.close()