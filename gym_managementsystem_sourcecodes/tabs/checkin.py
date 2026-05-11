from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QFont, QRegularExpressionValidator

class CheckinPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(40, 40, 40, 40); layout.setSpacing(20)

        lbl_title = QLabel("Member Access (Check-In)")
        lbl_title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        search_layout = QHBoxLayout(); search_layout.addStretch()
        
        self.inp_checkin_id = QLineEdit()
        self.inp_checkin_id.setPlaceholderText("Member ID...")
        self.inp_checkin_id.setFixedSize(200, 50)
        self.inp_checkin_id.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.inp_checkin_id.setFont(QFont("Arial", 16))
        self.inp_checkin_id.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]*")))
        self.inp_checkin_id.returnPressed.connect(self.perform_checkin)

        btn_check = QPushButton("CHECK")
        btn_check.setFixedSize(120, 50)
        btn_check.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_check.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; font-size: 14px; border-radius: 5px;")
        btn_check.clicked.connect(self.perform_checkin)

        search_layout.addWidget(self.inp_checkin_id); search_layout.addWidget(btn_check); search_layout.addStretch()
        layout.addLayout(search_layout)

        self.card_result = QFrame(); self.card_result.setVisible(False); self.card_result.setFixedSize(500, 400)
        self.card_result.setStyleSheet("QFrame { background-color: white; border-radius: 20px; border: none; }")
        
        card_layout = QVBoxLayout(self.card_result); card_layout.setSpacing(15); card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_ci_avatar = QLabel("AA"); self.lbl_ci_avatar.setFixedSize(100, 100); self.lbl_ci_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter); self.lbl_ci_avatar.setFont(QFont("Arial", 36, QFont.Weight.Bold)); self.lbl_ci_avatar.setStyleSheet("background-color: #E8F5E9; color: #2E7D32; border-radius: 50px;")
        self.lbl_ci_name = QLabel("Name Surname"); self.lbl_ci_name.setFont(QFont("Arial", 22, QFont.Weight.Bold)); self.lbl_ci_name.setStyleSheet("border: none; color: #333;")
        
        self.lbl_ci_details = QLabel("Details..."); 
        self.lbl_ci_details.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_ci_details.setFont(QFont("Arial", 13))
        self.lbl_ci_details.setStyleSheet("border: none; color: #555;")
        
        self.lbl_ci_status = QLabel("ACCESS GRANTED"); self.lbl_ci_status.setFont(QFont("Arial", 18, QFont.Weight.Bold)); self.lbl_ci_status.setStyleSheet("border: none; color: #4CAF50; margin-top: 10px;")

        card_layout.addWidget(self.lbl_ci_avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.lbl_ci_name, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.lbl_ci_details, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.lbl_ci_status, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.card_result, alignment=Qt.AlignmentFlag.AlignCenter); layout.addStretch()

    def perform_checkin(self):
        mid = self.inp_checkin_id.text().strip()
        if not mid: return

        member_info = self.db.get_member_by_id(mid)
        
        access_result = self.db.check_member_access(mid)

        if member_info and access_result != 'NOT_FOUND':
            
            fname = member_info[0]
            lname = member_info[1]
            email = member_info[2]
            phone = member_info[3]
            raw_plan = member_info[4]
            join_date = member_info[6]
            remaining_days = member_info[8] 

            date_str = join_date.strftime("%d.%m.%Y") if hasattr(join_date, 'strftime') else str(join_date)

            plan_display = raw_plan.split('(')[0].strip() if raw_plan and '(' in raw_plan else raw_plan

            self.lbl_ci_avatar.setText(f"{fname[0].upper()}{lname[0].upper()}")
            self.lbl_ci_name.setText(f"{fname} {lname}")
            
            detail_text = (
                f"📞 {phone}\n"
                f"📧 {email}\n"
                f"📋 Plan: {plan_display}\n"
                f"📅 Reg: {date_str}\n"
                f"⏳ Remaining: {remaining_days} Days"
            )
            self.lbl_ci_details.setText(detail_text)
            
            if access_result == 'ACCESS_GRANTED':
                self.card_result.setStyleSheet("QFrame { background-color: white; border-radius: 20px; border: 4px solid #2E7D32; }")
                self.lbl_ci_status.setText("ACCESS GRANTED")
                self.lbl_ci_status.setStyleSheet("color: #2E7D32; font-weight: bold; font-size: 20px; border: none;")
                self.lbl_ci_avatar.setStyleSheet("background-color: #E8F5E9; color: #2E7D32; border-radius: 50px; border: none;")
            
            else:
                self.card_result.setStyleSheet("QFrame { background-color: white; border-radius: 20px; border: 4px solid #C62828; }")
                self.lbl_ci_status.setStyleSheet("color: #C62828; font-weight: bold; font-size: 20px; border: none;")
                self.lbl_ci_avatar.setStyleSheet("background-color: #FFEBEE; color: #C62828; border-radius: 50px; border: none;")

                if access_result == 'EXPIRED':
                    self.lbl_ci_status.setText("MEMBERSHIP EXPIRED")
                elif access_result == 'PASSIVE_MEMBER':
                    self.lbl_ci_status.setText(" MEMBERSHIP FROZEN")
                else:
                    self.lbl_ci_status.setText(" ACCESS DENIED")

            self.card_result.setVisible(True)
        else:
            self.card_result.setVisible(True)
            self.lbl_ci_avatar.setText("?")
            self.lbl_ci_avatar.setStyleSheet("background-color: #ECEFF1; color: #607D8B; border-radius: 50px; border: none;")
            self.lbl_ci_name.setText("Not Found")
            self.lbl_ci_details.setText(f"ID: {mid} not registered.")
            
            self.card_result.setStyleSheet("QFrame { background-color: white; border: 4px solid #607D8B; border-radius: 20px; }")
            self.lbl_ci_status.setText("INVALID ID")
            self.lbl_ci_status.setStyleSheet("color: #607D8B; font-weight: bold; font-size: 20px; border: none;")
            
        self.inp_checkin_id.clear()