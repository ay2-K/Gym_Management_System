from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate, QRegularExpression
from PyQt6.QtGui import QFont, QRegularExpressionValidator

class AddMemberDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Add New Member")
        self.setFixedSize(400, 500)
        self.layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.inp_name = QLineEdit()
        self.inp_surname = QLineEdit()
        self.inp_email = QLineEdit()
        
        self.inp_phone = QLineEdit()
        self.inp_phone.setPlaceholderText("5XX...")
        self.inp_phone.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]*")))

        self.combo_gender = QComboBox()
        self.combo_gender.addItems(["Male", "Female", "Other"])

        self.combo_plan = QComboBox()
        self.inp_price = QLineEdit()
        self.inp_price.setReadOnly(True)
        self.inp_price.setStyleSheet("background-color: #f0f0f0; color: #333; font-weight: bold;")

        self.plans = self.db.get_all_plans()
        if not self.plans:
            self.combo_plan.addItem("Please Add Plan", 0.0)
            self.inp_price.setText("0")
        else:
            for p in self.plans:
                self.combo_plan.addItem(f"{p[1]} ({p[2]} Months)", p[3])
            
            if self.plans:
                self.inp_price.setText(str(self.plans[0][3]))

        self.combo_plan.currentIndexChanged.connect(self.update_price_field)
        self.combo_payment = QComboBox()
        self.combo_payment.addItems(["Credit Card", "Cash"])

        form.addRow("Name:", self.inp_name)
        form.addRow("Surname:", self.inp_surname)
        form.addRow("Email:", self.inp_email)
        form.addRow("Phone:", self.inp_phone)
        form.addRow("Gender:", self.combo_gender)
        
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine); line.setStyleSheet("color: #ccc")
        form.addRow(line)
        
        form.addRow("Plan:", self.combo_plan)
        form.addRow("Amount:", self.inp_price)
        form.addRow("Payment Type:", self.combo_payment)
        
        self.layout.addLayout(form)
        self.btn_save = QPushButton("Save")
        self.btn_save.setStyleSheet("background-color: #1565C0; color: white; padding: 10px; font-weight: bold;")
        self.btn_save.clicked.connect(self.accept)
        self.layout.addWidget(self.btn_save)

    def update_price_field(self):
        idx = self.combo_plan.currentIndex()
        if self.plans and idx < len(self.plans):
             price = self.plans[idx][3]
             self.inp_price.setText(str(price))

    def get_data(self):
        return (
            self.inp_name.text(), 
            self.inp_surname.text(), 
            self.inp_email.text(), 
            self.inp_phone.text(), 
            self.combo_gender.currentText(), 
            self.combo_plan.currentText(), 
            self.inp_price.text(), 
            self.combo_payment.currentText()
        )

class MemberPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        top = QHBoxLayout()
        header_lbl = QLabel("Member List")
        header_lbl.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        
        self.inp_search_member = QLineEdit()
        self.inp_search_member.setPlaceholderText("Search by name...")
        self.inp_search_member.setFixedWidth(250)
        self.inp_search_member.setStyleSheet("border: 1px solid #ccc; border-radius: 15px; padding: 5px 10px; background: white;")
        self.inp_search_member.textChanged.connect(self.load_members)

        btn_add = QPushButton("+ New Member")
        btn_add.setFixedSize(120, 40)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border-radius: 20px; font-weight: bold; } QPushButton:hover { background-color: #388E3C; }")
        btn_add.clicked.connect(self.open_add_member)
        
        top.addWidget(header_lbl)
        top.addStretch()
        top.addWidget(self.inp_search_member)
        top.addWidget(btn_add)
        layout.addLayout(top)

        self.table_members = QTableWidget()
        self.table_members.setColumnCount(11) 
        self.table_members.setHorizontalHeaderLabels([
            "ID", "Name", "Surname", "Plan", "Price", 
            "Email", "Phone", "Payment", "Reg Date", "Status", "Action"
        ])
        
        header = self.table_members.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed); self.table_members.setColumnWidth(0, 40)  
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed); self.table_members.setColumnWidth(1, 110) 
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed); self.table_members.setColumnWidth(2, 110)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed); self.table_members.setColumnWidth(3, 120)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed); self.table_members.setColumnWidth(4, 70)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed); self.table_members.setColumnWidth(6, 100)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed); self.table_members.setColumnWidth(7, 80)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed); self.table_members.setColumnWidth(8, 90)
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed); self.table_members.setColumnWidth(9, 100)
        header.setSectionResizeMode(10, QHeaderView.ResizeMode.Fixed); self.table_members.setColumnWidth(10, 60)

        self.table_members.verticalHeader().setVisible(False)
        self.table_members.setShowGrid(False)
        self.table_members.setAlternatingRowColors(False)
        self.table_members.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table_members.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        
        self.table_members.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #ddd; font-size: 13px; }
            QHeaderView::section { background-color: #607D8B; color: white; padding: 12px; font-weight: bold; border: none; border-right: 1px solid #455A64; }
            QTableWidget::item { padding-left: 10px; border-bottom: 1px solid #eee; border-right: 1px solid #e0e0e0; }
        """)
        
        layout.addWidget(self.table_members)
        self.load_members()

    def load_members(self):
        search_text = getattr(self, 'inp_search_member', None).text().lower() if hasattr(self, 'inp_search_member') else ""
        
        all_members = self.db.get_all_members()
        filtered = [m for m in all_members if search_text in m[1].lower() or search_text in m[2].lower()]
        
        self.table_members.setRowCount(0)
        for r, row in enumerate(filtered):
            self.table_members.insertRow(r)
            self.table_members.setRowHeight(r, 50)
            
            self.table_members.setItem(r, 0, QTableWidgetItem(str(row[0])))
            
            self.table_members.setItem(r, 1, QTableWidgetItem(str(row[1])))
            
            self.table_members.setItem(r, 2, QTableWidgetItem(str(row[2])))
            
            plan_full = str(row[3])
            plan_display = plan_full.split('(')[0].strip() if '(' in plan_full else plan_full
            self.table_members.setItem(r, 3, QTableWidgetItem(plan_display))
            
            self.table_members.setItem(r, 4, QTableWidgetItem(f"{row[4]} $"))
            
            self.table_members.setItem(r, 5, QTableWidgetItem(str(row[5])))
            
            self.table_members.setItem(r, 6, QTableWidgetItem(str(row[6])))
            
            self.table_members.setItem(r, 7, QTableWidgetItem(str(row[7])))
            
            date_val = row[8]
            date_str = date_val.strftime("%d.%m.%Y") if hasattr(date_val, 'strftime') else str(date_val)
            self.table_members.setItem(r, 8, QTableWidgetItem(date_str))

            status_val = row[9] 
            if not status_val: status_val = "Active"

            btn_status = QPushButton(status_val)
            btn_status.setFixedSize(80, 28)
            btn_status.setCursor(Qt.CursorShape.PointingHandCursor)
            
            if status_val in ["Active"]:
                btn_status.setText("Active")
                btn_status.setStyleSheet("QPushButton { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; border-radius: 14px; font-weight: bold; } QPushButton:hover { background-color: #c8e6c9; }")
            else:
                btn_status.setText("Passive")
                btn_status.setStyleSheet("QPushButton { background-color: #ffebee; color: #c62828; border: 1px solid #ef9a9a; border-radius: 14px; font-weight: bold; } QPushButton:hover { background-color: #ffcdd2; }")

            btn_status.clicked.connect(lambda _, mid=row[0], st=status_val: self.toggle_status_action(mid, st))
            
            w_status = QWidget(); l_s = QHBoxLayout(w_status); l_s.setContentsMargins(0, 0, 0, 0); l_s.setAlignment(Qt.AlignmentFlag.AlignCenter); l_s.addWidget(btn_status)
            self.table_members.setCellWidget(r, 9, w_status)

            btn_del = QPushButton("X")
            btn_del.setFixedSize(30, 30)
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setStyleSheet("QPushButton { background-color: transparent; color: #999; font-weight: bold; border: 1px solid #ddd; border-radius: 15px; } QPushButton:hover { background-color: #ffebee; color: red; border: 1px solid red; }")
            btn_del.clicked.connect(lambda _, mid=row[0]: self.delete_member_action(mid))
            
            w_del = QWidget(); l_d = QHBoxLayout(w_del); l_d.setContentsMargins(0, 0, 0, 0); l_d.setAlignment(Qt.AlignmentFlag.AlignCenter); l_d.addWidget(btn_del)
            self.table_members.setCellWidget(r, 10, w_del)

    def toggle_status_action(self, member_id, current_status):
        new_status = "Passive" if current_status in ["Active"] else "Active"
        if self.db.update_member_status(member_id, new_status):
            self.load_members()
        else:
            QMessageBox.critical(self, "Error", "Could not update status!")        
            
    def open_add_member(self):
        d = AddMemberDialog(self.db, self) 
        if d.exec(): 
            result = self.db.add_member(*d.get_data())
            
            if result == "SUCCESS":
                self.load_members()
            elif result == "DUPLICATE":
                QMessageBox.warning(self)
            elif result == "PLAN_ERROR":
                 QMessageBox.warning(self)
            else:
                QMessageBox.critical(self)

    def delete_member_action(self, mid):
        if QMessageBox.question(self, "Delete", "Are you sure you want to delete this member?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.db.delete_member(mid)
            self.load_members()

class AddTrainerDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("New Trainer")
        self.setFixedSize(400, 400)
        self.layout = QVBoxLayout(self)
        form = QFormLayout()

        self.inp_name = QLineEdit(); self.inp_surname = QLineEdit()
        self.combo_spec = QComboBox()
        classes = self.db.get_all_gym_classes()
        if classes:
            for c in classes: self.combo_spec.addItem(c[1]) 

        self.inp_email = QLineEdit()
        self.inp_phone = QLineEdit()
        self.inp_phone.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]*")))
        
        self.inp_date = QDateEdit()
        self.inp_date.setCalendarPopup(True)
        self.inp_date.setDate(QDate.currentDate())
        self.inp_date.setDisplayFormat("dd.MM.yyyy")

        form.addRow("Name:", self.inp_name)
        form.addRow("Surname:", self.inp_surname)
        form.addRow("Specialty:", self.combo_spec)
        form.addRow("Phone:", self.inp_phone)
        form.addRow("Email:", self.inp_email)
        form.addRow("Hire Date:", self.inp_date)

        self.layout.addLayout(form)
        self.btn_save = QPushButton("Save")
        self.btn_save.setStyleSheet("background-color: #1565C0; color: white; padding: 10px;")
        self.btn_save.clicked.connect(self.accept)
        self.layout.addWidget(self.btn_save)

    def get_data(self):
        return (self.inp_name.text(), self.inp_surname.text(), self.combo_spec.currentText(), 
                self.inp_phone.text(), self.inp_email.text(), self.inp_date.date().toString("yyyy-MM-dd"))

class TrainerPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        top = QHBoxLayout()
        header = QLabel("Trainers")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        btn_add = QPushButton("+ Add Trainer")
        btn_add.setFixedSize(140, 40)
        btn_add.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border-radius: 20px; font-weight: bold; } QPushButton:hover { background-color: #388E3C; }")
        btn_add.clicked.connect(self.open_add_trainer)
        top.addWidget(header); top.addStretch(); top.addWidget(btn_add)
        layout.addLayout(top)

        self.scroll_trainers = QScrollArea()
        self.scroll_trainers.setWidgetResizable(True)
        self.scroll_trainers.setStyleSheet("border: none; background: transparent;")
        
        self.content_trainers = QWidget()
        self.layout_trainers = QHBoxLayout(self.content_trainers)
        self.layout_trainers.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.layout_trainers.setSpacing(20)
        
        self.scroll_trainers.setWidget(self.content_trainers)
        layout.addWidget(self.scroll_trainers)
        self.load_trainers()

    def load_trainers(self):
        while self.layout_trainers.count():
            item = self.layout_trainers.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        trainers = self.db.get_all_trainers()
        if not trainers: self.layout_trainers.addWidget(QLabel("No trainers added.")); return

        for t in trainers:
            card = self.create_trainer_card(t)
            self.layout_trainers.addWidget(card)
        self.layout_trainers.addStretch()

    def create_trainer_card(self, data):
        t_id, name, surname, spec, phone, email, hire_date = data
        
        card = QFrame()
        card.setFixedSize(280, 360) 
        card.setStyleSheet("""
            QFrame { background-color: white; border-radius: 15px; border: 1px solid #ddd; }
            QFrame:hover { border: 2px solid #03A9F4; }
        """)
        
        l = QVBoxLayout(card)
        l.setSpacing(10)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_avatar = QLabel(name[0].upper() + surname[0].upper())
        lbl_avatar.setFixedSize(90, 90)
        lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_avatar.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        lbl_avatar.setStyleSheet("background-color: #E1F5FE; color: #03A9F4; border-radius: 45px; border: 2px solid #03A9F4;")
        
        lbl_name = QLabel(f"{name} {surname}")
        lbl_name.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_name.setStyleSheet("background-color: transparent; border: none; color: #333;")
        
        lbl_spec = QLabel(spec.upper())
        lbl_spec.setStyleSheet("background-color: transparent; border: none; color: #FF9800; font-weight: bold; font-size: 14px; letter-spacing: 1px;")
        
        lbl_contact = QLabel(f"📞 {phone}\n📧 {email}")
        lbl_contact.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_contact.setStyleSheet("background-color: transparent; border: none; color: #555; font-size: 14px;")
        
        hd_str = hire_date.strftime("%d.%m.%Y") if hasattr(hire_date, 'strftime') else str(hire_date)
        lbl_date = QLabel(f"Since: {hd_str}")
        lbl_date.setStyleSheet("background-color: transparent; border: none; color: #888; font-size: 12px;")

        btn_del = QPushButton("Delete Profile")
        btn_del.setFixedSize(140, 35)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet("background-color: #ff5252; color: white; border-radius: 17px; font-weight: bold; font-size: 13px;")
        btn_del.clicked.connect(lambda _, tid=t_id: self.delete_trainer_action(tid))
        
        l.addWidget(lbl_avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        l.addWidget(lbl_name, alignment=Qt.AlignmentFlag.AlignCenter)
        l.addWidget(lbl_spec, alignment=Qt.AlignmentFlag.AlignCenter)
        l.addWidget(lbl_contact, alignment=Qt.AlignmentFlag.AlignCenter)
        l.addWidget(lbl_date, alignment=Qt.AlignmentFlag.AlignCenter)
        l.addStretch()
        l.addWidget(btn_del, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return card

    def open_add_trainer(self):
        d = AddTrainerDialog(self.db, self) 
        if d.exec(): 
            result = self.db.add_trainer(*d.get_data())
            
            if result == "SUCCESS":
                self.load_trainers()
            elif result == "DUPLICATE":
                QMessageBox.warning(self)
            else:
                QMessageBox.critical(self)

    def delete_trainer_action(self, tid):
        if QMessageBox.question(self, "Delete", "Delete Trainer?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.db.delete_trainer(tid)
            self.load_trainers()