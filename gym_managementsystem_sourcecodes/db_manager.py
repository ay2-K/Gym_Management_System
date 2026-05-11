import mysql.connector
from mysql.connector import errorcode
from datetime import datetime, date, timedelta

class GymDatabase:
    def __init__(self, host="localhost", user="root", password="your_password_here", database="gym_db"):
        self.db_config = {'host': host, 'user': user, 'password': password, 'database': database}
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            print(f"SQL Connection Error: {err}")
            self.conn = None

    def _reconnect(self):
        try:
            if not self.conn or not self.conn.is_connected():
                self.conn = mysql.connector.connect(**self.db_config)
                self.cursor = self.conn.cursor()
           
            if self.cursor:
                try:
                    self.cursor.fetchall() 
                except: pass
        except Exception as e:
            print(f"Reconnect Error: {e}")

    
    def get_dashboard_stats(self):
        self._reconnect()
        try:
            self.cursor.callproc('GetDashboardStats')
            for res in self.cursor.stored_results():
                r = res.fetchone()
                if r:
                    return {
                        "total_members": r[0], 
                        "active_members": r[1], 
                        "passive_members": r[2],
                        "revenue": float(r[3]) if r[3] else 0.0, # Decimal -> Float
                        "total_plans": r[4], 
                        "total_classes": r[5],
                        "trainers": r[6], 
                        "equipments": int(r[7])
                    }
            return {}
        except Exception as e:
            print(f"Dashboard Error: {e}")
            return {"total_members":0, "active_members":0, "passive_members":0, "revenue":0.0, "total_plans":0, "total_classes":0, "trainers":0, "equipments":0}

   
    def get_all_plans(self):
        self._reconnect()
        self.cursor.execute("SELECT plan_id, plan_name, duration_months, price FROM plans")
        return self.cursor.fetchall()

    def add_plan(self, name, months, price):
        self._reconnect()
        sql = "INSERT INTO plans (plan_name, duration_months, price) VALUES (%s, %s, %s)"
        self.cursor.execute(sql, (name, months, price))
        self.conn.commit()

    def delete_plan(self, pid):
        self._reconnect()
        try:
            self.cursor.execute("DELETE FROM plans WHERE plan_id=%s", (pid,))
            self.conn.commit()
            return True
        except: return False

 
    def get_all_members(self):
        self._reconnect()
        query = """
            SELECT 
                m.member_id, 
                m.first_name, 
                m.last_name, 
                
                COALESCE(
                    (SELECT p.plan_name 
                     FROM member_plans mp 
                     JOIN plans p ON mp.plan_id = p.plan_id 
                     WHERE mp.member_id = m.member_id AND mp.is_active = TRUE 
                     ORDER BY mp.end_date DESC LIMIT 1), 
                '-') AS plan_name,

                COALESCE(
                    (SELECT mp.price_sold 
                     FROM member_plans mp 
                     WHERE mp.member_id = m.member_id AND mp.is_active = TRUE 
                     ORDER BY mp.end_date DESC LIMIT 1), 
                0) AS price,

                m.email, 
                m.phone, 

                COALESCE(
                    (SELECT pay.payment_type 
                     FROM payments pay 
                     WHERE pay.member_id = m.member_id 
                     ORDER BY pay.payment_date DESC LIMIT 1), 
                '-') AS payment_type,

                m.join_date, 
                m.status
            FROM members m
            ORDER BY m.member_id DESC;
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def add_member(self, name, surname, email, phone, gender, plan_name, price_str, payment_method):
        self._reconnect()

        try:
            if not price_str or price_str == "0": price = 0.0
            else: price = float(str(price_str).replace("$", "").replace("TL", "").strip())
            
          
            clean_plan = plan_name.split(' (')[0].strip()
            self.cursor.execute("SELECT plan_id, duration_months FROM plans WHERE plan_name=%s", (clean_plan,))
            plan_res = self.cursor.fetchone()
            
            if not plan_res: return "PLAN_ERROR"
            plan_id, months = plan_res

            
            try:
                self.conn.start_transaction()
            except mysql.connector.errors.ProgrammingError:
                self.conn.rollback()
                self.conn.start_transaction()
            
            sql_mem = "INSERT INTO members (first_name, last_name, email, phone, gender, join_date, status) VALUES (%s, %s, %s, %s, %s, %s, 'Active')"
            self.cursor.execute(sql_mem, (name, surname, email, phone, gender, date.today()))

            member_id = self.cursor.lastrowid
            end_date = date.today() + timedelta(days=months*30)
            sql_mp = "INSERT INTO member_plans (member_id, plan_id, start_date, end_date, price_sold, is_active) VALUES (%s, %s, %s, %s, %s, TRUE)"
            self.cursor.execute(sql_mp, (member_id, plan_id, date.today(), end_date, price))

            sql_pay = "INSERT INTO payments (member_id, amount, payment_type) VALUES (%s, %s, %s)"
            self.cursor.execute(sql_pay, (member_id, price, payment_method))

            self.conn.commit()
            return "SUCCESS"

        except mysql.connector.Error as err:
            self.conn.rollback()
            print(f"SQL Error: {err}")
            return "DUPLICATE" if err.errno == 1062 else "ERROR"
        except Exception as e:
            self.conn.rollback()
            print(f"Genel Hata: {e}")
            return "ERROR"

    def delete_member(self, mid):
        self._reconnect()
        self.cursor.execute("DELETE FROM members WHERE member_id=%s", (mid,))
        self.conn.commit()
        return True

    def update_member_status(self, mid, status):
        self._reconnect()
        db_stat = 'Active' if status in ['Active', 'Aktif'] else 'Passive'
        self.cursor.execute("UPDATE members SET status=%s WHERE member_id=%s", (db_stat, mid))
        self.conn.commit()
        return True

    def get_member_by_id(self, mid):
        self._reconnect()
        try:
            self.cursor.callproc('GetMemberWithRemaining', [mid])
            for res in self.cursor.stored_results():
                return res.fetchone()
        except: return None

    def check_member_access(self, mid):
        self._reconnect()
        try:
            self.cursor.callproc('CheckMemberAccess', [mid])
            for res in self.cursor.stored_results():
                return res.fetchone()[0]
        except: return "ERROR"

    def get_all_trainers(self):
        self._reconnect()
        self.cursor.execute("SELECT trainer_id, first_name, last_name, specialty, phone, email, hire_date FROM trainers")
        return self.cursor.fetchall()

    def add_trainer(self, name, surname, spec, phone, email, hdate):
        self._reconnect()
        try:
            sql = "INSERT INTO trainers (first_name, last_name, specialty, phone, email, hire_date) VALUES (%s,%s,%s,%s,%s,%s)"
            self.cursor.execute(sql, (name, surname, spec, phone, email, hdate))
            self.conn.commit()
            return "SUCCESS"
        except mysql.connector.Error as e:
            return "DUPLICATE" if e.errno == 1062 else "ERROR"

    def delete_trainer(self, tid):
        self._reconnect()
        self.cursor.execute("DELETE FROM trainers WHERE trainer_id=%s", (tid,))
        self.conn.commit()

    def get_all_equipments(self):
        self._reconnect()
        self.cursor.execute("SELECT * FROM equipments")
        return self.cursor.fetchall()

    def add_equipment(self, name, qty, pdate):
        self._reconnect()
        sql = "INSERT INTO equipments (equipment_name, quantity, purchase_date) VALUES (%s,%s,%s)"
        self.cursor.execute(sql, (name, qty, pdate))
        self.conn.commit()

    def delete_equipment_by_name(self, name):
        self._reconnect()
        self.cursor.execute("DELETE FROM equipments WHERE equipment_name=%s", (name,))
        self.conn.commit()
    
    def delete_equipment_by_id(self, eid):
        self._reconnect()
        self.cursor.execute("DELETE FROM equipments WHERE equipment_id=%s", (eid,))
        self.conn.commit()

    def get_all_gym_classes(self):
        self._reconnect()
        self.cursor.execute("SELECT * FROM gym_classes")
        return self.cursor.fetchall()

    def add_gym_class(self, name, desc):
        self._reconnect()
        self.cursor.execute("INSERT INTO gym_classes (class_name, description) VALUES (%s,%s)", (name, desc))
        self.conn.commit()

    def delete_gym_class(self, cid):
        self._reconnect()
        self.cursor.execute("DELETE FROM gym_classes WHERE class_id=%s", (cid,))
        self.conn.commit()

    def get_all_schedules(self):
        self._reconnect()
        query = "SELECT s.schedule_id, c.class_name, CONCAT(t.first_name, ' ', t.last_name), s.day_of_week, s.start_time, s.end_time FROM schedules s JOIN gym_classes c ON s.class_id = c.class_id JOIN trainers t ON s.trainer_id = t.trainer_id"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def add_schedule(self, cid, tid, day, start, end):
        self._reconnect()
        try:
            sql = "INSERT INTO schedules (class_id, trainer_id, day_of_week, start_time, end_time) VALUES (%s,%s,%s,%s,%s)"
            self.cursor.execute(sql, (cid, tid, day, start, end))
            self.conn.commit()
            return 
        except mysql.connector.Error as err:
            if err.errno == 1062:
                return

    def delete_schedule(self, sid):
        self._reconnect()
        self.cursor.execute("DELETE FROM schedules WHERE schedule_id=%s", (sid,))
        self.conn.commit()

    def get_all_enrollments(self):
        self._reconnect()
        query = "SELECT e.enrollment_id, CONCAT(m.first_name, ' ', m.last_name), c.class_name, s.day_of_week, s.start_time FROM enrollments e JOIN members m ON e.member_id = m.member_id JOIN schedules s ON e.schedule_id = s.schedule_id JOIN gym_classes c ON s.class_id = c.class_id"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def add_enrollment(self, mid, sid):
        self._reconnect()
        self.cursor.execute("INSERT INTO enrollments (member_id, schedule_id) VALUES (%s,%s)", (mid, sid))
        self.conn.commit()

    def delete_enrollment(self, eid):
        self._reconnect()
        self.cursor.execute("DELETE FROM enrollments WHERE enrollment_id=%s", (eid,))
        self.conn.commit()