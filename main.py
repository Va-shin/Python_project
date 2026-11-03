from os import name
import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QLineEdit,QWidget,
                            QLineEdit,QPushButton,QVBoxLayout,QLabel,QFormLayout,QMessageBox,
                            QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QTabWidget,QComboBox,
                            QTimeEdit,QDateTimeEdit,QHBoxLayout,QDateEdit,QFileDialog,QDialog,)
from database import (create_tables, add_patient,search_patients,get_patients,update_patient,add_doctor,search_doctors,get_doctors,
                      save_update_schedule,search_schedule,get_doctor_schedule,book_appointment,get_appointments,update_appointment_status,)
from PyQt5.QtCore import QTime,QDateTime,QDate
from datetime import datetime,timedelta,time
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.ticker import MaxNLocator
from login import LoginDialog
from security import has_staff_accounts
from reports import get_appointment_report
from styles import APP_STYLE
from PyQt5.QtGui import QColor, QBrush
class HospitalWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("HospitalWindow")
        self.setWindowTitle("Hospital Management System")
        self.resize(1100, 750)
        self.selected_patient_id = None
        self.selected_doctor_id = None
        self.setWindowTitle("Hospital Patient Registration")
        #self.resize(600, 600)
        self.setGeometry(300,300,900,600)
        
        self.tabs = QTabWidget()
        
        self.patient_tab = QWidget()
        patient_layout = QVBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter patient name")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter patient phone number")
        
        
        patient_form = QFormLayout()
        patient_form.addRow("Name :", self.name_input)
        patient_form.addRow("Phone :", self.phone_input)
        
        self.savebutton = QPushButton("Save Patient")
        self.update_button = QPushButton("Update")       
        self.update_button.setEnabled(False)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search the patient")     
        self.search_button = QPushButton("Search")
 
        patient_layout.addLayout(patient_form)
        patient_layout.addWidget(self.savebutton)
        
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(3)
        self.patient_table.setHorizontalHeaderLabels(["ID","Name","Phone"])
        
        self.patient_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.patient_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.patient_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.patient_table.itemSelectionChanged.connect(self.load_selected_patient)
        
        patient_layout.addWidget(self.search_input)
        patient_layout.addWidget(self.search_button)
        patient_layout.addWidget(self.update_button)
        patient_layout.addWidget(self.patient_table)
        self.search_button.clicked.connect(self.search_patient)
        self.update_button.clicked.connect(self.update_selected_patient)
        
        self.patient_tab.setLayout(patient_layout)
        
        self.savebutton.clicked.connect(self.save_patient)
        
        self.doctor_tab = QWidget()  
        doctor_layout = QVBoxLayout()
        self.doctor_name_input = QLineEdit()
        self.doctor_name_input.setPlaceholderText("Enter Doctor name")
        self.doctor_specialty_input = QLineEdit()
        self.doctor_specialty_input.setPlaceholderText("Enter Doctor specialty")
        self.doctor_search_input = QLineEdit()
        self.doctor_search_input.setPlaceholderText("Enter the doctor for search")
        
        doctor_form = QFormLayout()
        doctor_form.addRow("Name :", self.doctor_name_input)
        doctor_form.addRow("Specialty :", self.doctor_specialty_input)
        self.save_doctor = QPushButton("Save doctor")
        self.search_doctor_button = QPushButton("Search")
        self.doctor_table = QTableWidget()
        self.doctor_table.setColumnCount(3)
        self.doctor_table.setHorizontalHeaderLabels(["ID","Doctor Name","Specialty"])
        
        self.doctor_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.doctor_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.doctor_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        doctor_layout.addLayout(doctor_form)
        doctor_layout.addWidget(self.doctor_name_input)
        doctor_layout.addWidget(self.doctor_specialty_input)
        doctor_layout.addWidget(self.save_doctor)
        doctor_layout.addWidget(self.doctor_search_input)
        doctor_layout.addWidget(self.search_doctor_button)
        doctor_layout.addWidget(self.doctor_table)
        
        self.doctor_tab.setLayout(doctor_layout)
        
        self.save_doctor.clicked.connect(self.save_doctors)
        self.search_doctor_button.clicked.connect(self.search_doctor)
        
        self.doctor_table.itemSelectionChanged.connect(self.load_selected_doctor)
        
        self.schedule_tab = QWidget()
        
        self.schedule_doctor_input = QComboBox()
        self.weekday_input = QComboBox()
        
        days = [
                    "Monday", "Tuesday", "Wednesday",
                    "Thursday", "Friday", "Saturday", "Sunday"
                ]
        
        for number,day in enumerate(days):
            self.weekday_input.addItem(day,number)
        
        self.schedule_doctor_input.clear()
        for doctor_id,name in get_doctors():
            self.schedule_doctor_input.addItem(name,doctor_id)
               
        
        self.starttime_input = QTimeEdit()
        self.starttime_input.setDisplayFormat("HH:mm")
        self.starttime_input.setTime(QTime(9,0))
        
        self.endtime_input = QTimeEdit()
        self.endtime_input.setDisplayFormat("HH:mm")
        self.endtime_input.setTime(QTime(17,0))

        self.save_update_button = QPushButton("Save")
        
        self.schedule_search_input = QLineEdit()
        self.schedule_search_input.setPlaceholderText("Enter the doctor ID ")
        
        self.schedule_search_button = QPushButton("Search")
        
        self.schedule_form = QFormLayout()
        self.schedule_form.addRow("Doctor :",self.schedule_doctor_input)
        self.schedule_form.addRow("Weekday :",self.weekday_input)
        self.schedule_form.addRow("Start Time :",self.starttime_input)
        self.schedule_form.addRow("End Time :",self.endtime_input) 
        
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(5)
        self.schedule_table.setHorizontalHeaderLabels(["ID","Doctor ID","Weekday","Start Time","End Time"])
        
        self.schedule_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.schedule_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.schedule_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.schedule_layout = QVBoxLayout()
        
        self.schedule_layout.addLayout(self.schedule_form)
        self.schedule_layout.addWidget(self.schedule_doctor_input)
        self.schedule_layout.addWidget(self.weekday_input)
        self.schedule_layout.addWidget(self.starttime_input)
        self.schedule_layout.addWidget(self.endtime_input)
        self.schedule_layout.addWidget(self.save_update_button)
        self.schedule_layout.addWidget(self.schedule_search_input)
        self.schedule_layout.addWidget(self.schedule_search_button)
        self.schedule_layout.addWidget(self.schedule_table)
        
        self.save_update_button.clicked.connect(self.save_schedule)
        self.schedule_search_button.clicked.connect(self.search_doctor_schedule)
        self.schedule_tab.setLayout(self.schedule_layout)
        
        
        self.appointment_tab = QWidget()
        self.patient = QComboBox()
        
        for id,name in get_patients():
            self.patient.addItem(name,id)
        
        self.doctor = QComboBox()
        
        for id,name in get_doctors():
            self.doctor.addItem(name,id)
            
        self.appointment_start_input  = QDateTimeEdit()
        self.appointment_start_input.setCalendarPopup(True)
        self.appointment_start_input.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.appointment_start_input.setDateTime(QDateTime.currentDateTime())
        
        self.duration_input = QComboBox()
        
        for minutes in [15,30,45,60]:
            self.duration_input.addItem(f"{minutes} minutes",minutes)
        
        
        self.reason_input = QLineEdit()
        self.book_button = QPushButton("Book Appointment")
        self.appointment_table = QTableWidget()
        self.appointment_table.setColumnCount(7)

        self.appointment_table.setHorizontalHeaderLabels(
            [
                "ID", "Patient", "Doctor", "Start",
                "End", "Status", "Reason"
            ]
        )
        self.appointment_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.appointment_table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.appointment_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.cancel_appointment_button = QPushButton(
                    "Cancel Appointment"
                )
        
        self.complete_appointment_button = QPushButton(
                    "Mark Completed"
                )
        appointment_action_layout = QHBoxLayout()
        
        appointment_action_layout.addWidget(
            self.cancel_appointment_button
        )

        appointment_action_layout.addWidget(
            self.complete_appointment_button
        )
        self.appointment_form = QFormLayout()
        self.appointment_form.addRow("Patient :",self.patient)
        self.appointment_form.addRow("Doctor :",self.doctor)
        self.appointment_form.addRow("Start :",self.appointment_start_input)
        self.appointment_form.addRow("Duration :",self.duration_input)
        self.appointment_form.addRow("Reason :",self.reason_input)
        
        self.appointment_layout = QVBoxLayout()
        self.appointment_layout.addLayout(self.appointment_form)        
        self.appointment_layout.addWidget(self.book_button)
        self.appointment_layout.addWidget(self.appointment_table)
        self.appointment_layout.addLayout(appointment_action_layout)
        self.appointment_tab.setLayout(self.appointment_layout)
        self.appointment_tab.setLayout(self.appointment_layout)  
        self.book_button.clicked.connect(self.save_appointment)
        self.cancel_appointment_button.clicked.connect(
            self.cancel_selected_appointment
        )
        self.complete_appointment_button.clicked.connect(
            self.complete_selected_appointment
        )    
        
        #Reports
        self.reports_df = None
        self.report_tab = QWidget()
        report_layout = QVBoxLayout()
        
        self.report_start_input = QDateEdit()
        self.report_start_input.setCalendarPopup(True)
        self.report_start_input.setDisplayFormat("dd/MM/yyyy")
        
        self.report_end_input = QDateEdit()
        self.report_end_input.setCalendarPopup(True)
        self.report_end_input.setDisplayFormat("dd/MM/yyyy")
        
        today = QDate.currentDate()
        
        self.report_start_input.setDate(QDate(today.year(),today.month(),1))
        self.report_end_input.setDate(today)
        
        date_form = QFormLayout()
        date_form.addRow("From Date :",self.report_start_input)
        date_form.addRow("To Date :",self.report_end_input)
        
        
        self.generate_report_button = QPushButton("Generate Report")
        self.export_report_button = QPushButton("Export CSV")
        self.export_report_button.setEnabled(False)
        
        report_buttons = QHBoxLayout()
        report_buttons.addWidget(self.generate_report_button)
        report_buttons.addWidget(self.export_report_button)
        
        self.report_summary = QLabel("Generate a report to see results")
        self.report_summary.setObjectName("SummaryCard")
        self.report_summary.setWordWrap(True)
        self.report_table = QTableWidget()
        self.report_table.setEditTriggers(
        QAbstractItemView.NoEditTriggers
        )
        
        self.report_figure = Figure(figsize=(5,3))
        self.report_canvas = FigureCanvasQTAgg(self.report_figure)
        
                
        # Arrange everything.
        report_layout.addLayout(date_form)
        report_layout.addLayout(report_buttons)
        report_layout.addWidget(self.report_summary)
        report_layout.addWidget(self.report_table)
        report_layout.addWidget(self.report_canvas)

        self.report_tab.setLayout(report_layout)

        self.tabs.addTab(self.report_tab, "Reports")

        # Connect buttons.
        self.generate_report_button.clicked.connect(
            self.generate_report
        )

        self.export_report_button.clicked.connect(
            self.export_report
        )
                
        self.tabs.addTab(self.patient_tab,"Patient")
        self.tabs.addTab(self.doctor_tab,"Doctor")
        self.tabs.addTab(self.schedule_tab,"Schedule")
        self.tabs.addTab(self.appointment_tab,"Appointments")
        # Green: save or complete.
        self.savebutton.setProperty("role", "success")
        self.save_doctor.setProperty("role", "success")
        self.save_update_button.setProperty("role", "success")
        self.book_button.setProperty("role", "success")
        self.complete_appointment_button.setProperty("role", "success")

        # Red: cancel.
        self.cancel_appointment_button.setProperty("role", "danger")

        # Light background: secondary action.
        self.export_report_button.setProperty("role", "secondary")
        
        self.savebutton.setToolTip("Register a new patient")

        self.update_button.setToolTip(
            "Update the selected patient's details"
        )

        self.book_button.setToolTip(
            "Book an appointment after checking availability"
        )

        self.cancel_appointment_button.setToolTip(
            "Cancel the selected appointment and free its time slot"
        )

        self.generate_report_button.setToolTip(
            "Show appointments within the selected date range"
        )
        self.search_input.returnPressed.connect(
            self.search_patient
        )

        self.doctor_search_input.returnPressed.connect(
            self.search_doctor
        )

        self.schedule_search_input.returnPressed.connect(
            self.search_doctor_schedule
        )
        title = QLabel("Hospital Management")
        title.setObjectName("PageTitle")

        subtitle = QLabel(
            "Manage patients, doctors, schedules and appointments."
        )
        subtitle.setObjectName("PageSubtitle")
        tables = [
            self.patient_table,
            self.doctor_table,
            self.schedule_table,
            self.appointment_table,
            self.report_table
        ]

        for table in tables:
            table.setAlternatingRowColors(True)
            table.verticalHeader().setVisible(False)

            table.verticalHeader().setDefaultSectionSize(38)

            table.horizontalHeader().setSectionResizeMode(
                QHeaderView.Interactive
            )

            table.horizontalHeader().setStretchLastSection(True)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(12)

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addWidget(self.tabs, 1)

        self.setLayout(main_layout)
    
    def generate_report(self):
        start_date = self.report_start_input.date()
        end_date = self.report_end_input.date()
        
        if start_date > end_date:
             QMessageBox.warning(
            self,
            "Invalid dates",
            "From date cannot be after To date."
            )
             return
        start_at = (start_date.toString("yyyy-MM-dd") + " 00:00:00"
                    )
        
        end_before = (end_date.addDays(1).toString("yyyy-MM-dd")+ " 00:00:00")
        
        self.report_df = None
        self.export_report_button.setEnabled(False)
        
        try:
            df = get_appointment_report(start_at, end_before)
        except sqlite3.Error as e:
            self.report_summary.setText("Report generation failed")
            self.report_table.setRowCount(0)
            self.report_figure.clear()
            self.report_canvas.draw()
            QMessageBox.warning(
                self,
                "Report error",
                f"Could not generate the report: {e}"
            )
            return

        self.display_report(df)   
        
    def cancel_selected_appointment(self):
        self.change_selected_appointment_status("Cancelled")

    def complete_selected_appointment(self):
        self.change_selected_appointment_status("Completed")
        
    def change_selected_appointment_status(self, new_status):
        # 1. Find the selected row.
        selected_rows = (
            self.appointment_table
            .selectionModel()
            .selectedRows()
        )

        if not selected_rows:
            QMessageBox.warning(
                self,
                "No appointment selected",
                "Please select an appointment from the table."
            )
            return

        row = selected_rows[0].row()

        # 2. Read the appointment ID and current status.
        appointment_id = int( 
            self.appointment_table.item(row, 0).text()
        )

        current_status = (
            self.appointment_table.item(row, 5).text()
        )

        # 3. Only scheduled appointments can be changed.
        if current_status != "Scheduled":
            QMessageBox.warning(
                self,
                "Status cannot be changed",
                f"This appointment is already {current_status}."
            )
            return

        # 4. Prepare the confirmation message.
        if new_status == "Cancelled":
            question = (
                f"Do you want to cancel appointment {appointment_id}?"
            )
        else:
            question = (
                f"Mark appointment {appointment_id} as completed?"
            )

        # 5. Ask the user to confirm.
        answer = QMessageBox.question(
            self,
            "Confirm status change",
            question,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if answer != QMessageBox.Yes:
            return

        # 6. Update SQLite.
        try:
            update_appointment_status(
                appointment_id,
                new_status
            )

        except (ValueError, sqlite3.Error) as e:
            QMessageBox.warning(
                self,
                "Update failed",
                str(e)
            )
            return

        # 7. Show success and refresh the table.
        QMessageBox.information(
            self,
            "Appointment updated",
            f"Appointment {appointment_id} is now {new_status}."
        )

        self.load_appointments()
    def display_report(self, df):
        self.report_df = df

        self.report_table.clearContents()
        self.report_table.setRowCount(len(df))
        self.report_table.setColumnCount(len(df.columns))

        self.report_table.setHorizontalHeaderLabels(
            [str(column) for column in df.columns]
        )

        for row_number, row in enumerate(
            df.itertuples(index=False, name=None)
        ):
            for column_number, value in enumerate(row):
                self.report_table.setItem(
                    row_number,
                    column_number,
                    QTableWidgetItem(str(value))
                )

        self.report_table.resizeColumnsToContents()

        total = len(df)
        scheduled = int((df["status"] == "Scheduled").sum())
        completed = int((df["status"] == "Completed").sum())
        cancelled = int((df["status"] == "Cancelled").sum())

        self.report_summary.setText(
            f"Total: {total} | "
            f"Scheduled: {scheduled} | "
            f"Completed: {completed} | "
            f"Cancelled: {cancelled}"
        )

        self.export_report_button.setEnabled(not df.empty)

        self.draw_report(df)
    
    def draw_report(self,df):
        self.report_figure.clear()
        ax = self.report_figure.add_subplot(111)
        
        if df.empty:
            ax.text(0.5,0.5,"No appointments in this period",ha="center",va = "center",transform = ax.transAxes)
            ax.set_axis_off()
        else:
            counts = (df["status"].value_counts().reindex(["Scheduled", "Completed", "Cancelled"],fill_value = 0))
            ax.bar(counts.index,counts.values,color =["#3478c0", "#36945a", "#c95555"] )
            ax.set_title("Appointments by Status")
            ax.set_ylabel("Number of appointments")
            
            ax.yaxis.set_major_locator(MaxNLocator(integer = True))
            
            self.report_figure.tight_layout()
            self.report_canvas.draw()
    def export_report(self):
        if self.report_df is None or self.report_df.empty:
            QMessageBox.warning(
                self,
                "No report",
                "Generate a report with records before exporting."
            )
            return
        path,_ = QFileDialog.getSaveFileName(self,"Save Appointmnet report","appointment_report.csv","CSV Files (*.csv)")
        
        if not path:
            return
        if not path.lower().endswith(".csv"):
            path += ".csv"
        export_df = self.report_df.copy()
        
        def safe_csv_value(value):
            if isinstance(value,str):
                if value.lstrip().startswith(("=", "+", "-", "@")):
                    return "'"+value
            return value
        for column in export_df.columns:
            export_df[column] = export_df[column].map(safe_csv_value)
            
        try:
            export_df.to_csv(
                path,
                index=False,
                encoding="utf-8-sig"
            )
        except OSError as e:
                QMessageBox.warning(
                    self,
                    "Export failed",
                    str(e)
                )
                return

        QMessageBox.information(
                self,
                "Export complete",
                f"Report saved to:\n{path}"
            )
            
    def save_appointment(self):
        patient_id = self.patient.currentData()
        doctor_id = self.doctor.currentData()
        start = self.appointment_start_input.dateTime().toPyDateTime()
        duration = self.duration_input.currentData()
        reason = self.reason_input.text().strip()
        try:
            appointment_id = book_appointment(
                patient_id,
                doctor_id,
                start,
                duration,
                reason
            )

        except (ValueError, sqlite3.Error) as e:
            QMessageBox.warning(
                self,
                "Booking failed",
                str(e)
            )
            return

        QMessageBox.information(
            self,
            "Appointment booked",
            f"Appointment ID: {appointment_id}"
        )

        self.reason_input.clear()
        self.load_appointments()
        
    def load_appointments(self):
        try:
            appointments = get_appointments()

        except sqlite3.Error as e:
            QMessageBox.warning(
                self,
                "Loading failed",
                str(e)
            )
            return

        self.appointment_table.clearSelection()
        self.appointment_table.setRowCount(len(appointments))
        status_colours = {
            "Scheduled": ("#DBEAFE", "#1E40AF"),
            "Completed": ("#DCFCE7", "#166534"),
            "Cancelled": ("#FEE2E2", "#991B1B")
                        }

        for row_number, appointment in enumerate(appointments):
            for column_number, value in enumerate(appointment):
                item = QTableWidgetItem(str(value))

                # Column 5 contains Status in your appointment table.
                if column_number == 5:
                    colours = status_colours.get(str(value))

                    if colours is not None:
                        background, foreground = colours

                        item.setBackground(
                            QBrush(QColor(background))
                        )

                        item.setForeground(
                            QBrush(QColor(foreground))
                        )

                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)

                self.appointment_table.setItem(
                    row_number,
                    column_number,
                    item
                )
    def update_selected_patient(self):
        if self.selected_patient_id is None:
            QMessageBox.warning(self,
            "No patient selected",
            "Please select a patient from the table."
        )
            return

        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        
        if not name:
            QMessageBox.warning(
            self,
            "Missing name",
            "Please enter the patient name."
        )
            return

        if not phone:
            QMessageBox.warning(
            self,
            "Missing phone",
            "Please enter the phone number."
        )
            return
        
        try:
            update_patient(self.selected_patient_id,name,phone)
        except sqlite3.Error as e:
            QMessageBox.warning(
            self,
            "Update error",
            f"Could not update the patient: {e}"
                )
            return
        else:
            QMessageBox.information(self,"patient updated","Patient details updated successfully.")
        
        self.patient_table.clearSelection()
        self.selected_patient_id = None
        self.update_button.setEnabled(False)
        
        self.search_patient()

    def load_selected_patient(self):
        selected_rows = self.patient_table.selectionModel().selectedRows()
        
        if not selected_rows:
            self.selected_patient_id = None
            self.update_button.setEnabled(False)
            return
        row = selected_rows[0].row()
        
        self.selected_patient_id = int(self.patient_table.item(row,0).text())
        
        name = self.patient_table.item(row,1).text()
        phone = self.patient_table.item(row,2).text()
        
        self.name_input.setText(name)
        self.phone_input.setText(phone)
        self.update_button.setEnabled(True)
        self.name_input.setFocus()
        
        
        
    def search_patient(self):
        search_text = self.search_input.text().strip()
        try:
            patients = search_patients(search_text)
        except sqlite3.Error as e:
            QMessageBox.warning(self,"Search Error",str(e))
            return
        
        self.patient_table.clearSelection()
        self.selected_patient_id = None
        self.update_button.setEnabled(False)
        self.patient_table.setRowCount(len(patients))
        
        for row_number, patient in enumerate(patients):
            for column_number,value in enumerate(patient):
                item = QTableWidgetItem(str(value))
                
                self.patient_table.setItem(row_number,column_number,item)
        
        
    def save_patient(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        
        if not name:
            QMessageBox.warning(self,"Patient name is empty","Please enter patient name")
            return
        if not phone:
            QMessageBox.warning(self,"Patient phone is empty","Please enter patient phone number")
            return
        
        try:
            patient_id = add_patient(name,phone)
        except sqlite3.Error as e:
            QMessageBox.Warning(self,"Database Error",f"An error occurred while saving the patient: {e}")
            return
        else:
            QMessageBox.information(self,"Patient Saved",f"Patient saved successfully! Patient ID: {patient_id}")
        
            self.name_input.clear()
            self.phone_input.clear()
            self.name_input.setFocus()
    def save_doctors(self):
            name = self.doctor_name_input.text().strip()
            specialty = self.doctor_specialty_input.text().strip()
            
            if not name:
                QMessageBox.warning(self,"Doctor name is empty","Please enter doctor name")
                return
            if not specialty:
                QMessageBox.warning(self,"Doctor phone is empty","Please enter doctor specialty")
                return
                    
            try:
                doctor_id = add_doctor(name,specialty)
            except sqlite3.Error as e:
                QMessageBox.Warning(self,"Database Error",f"An error occurred while saving the doctor: {e}")
                return
            else:
                QMessageBox.information(self,"Doctor Saved",f"Doctor saved successfully! Doctor ID: {doctor_id}")
                    
                self.doctor_name_input.clear()
                self.doctor_specialty_input.clear()
                self.doctor_name_input.setFocus()
    
    def search_doctor(self):
        search_text = self.doctor_search_input.text().strip()
        
        try:
            doctors = search_doctors(search_text)
        
        except sqlite3.Error as e:
                QMessageBox.warning(self,"Search Error",str(e))
                return
        
        self.doctor_table.clearSelection()
        self.doctor_table.setRowCount(len(doctors))
        for row_number,doctor in enumerate(doctors):
            for column_number,value in enumerate(doctor):
                item = QTableWidgetItem(str(value))
                self.doctor_table.setItem(row_number,column_number,item)
    def load_selected_doctor(self):
        selected_row = self.doctor_table.selectionModel().selectedRows()
        
        if not selected_row:
            self.selected_doctor_id = None
            return
        
        row = selected_row[0].row()
        
        self.selected_doctor_id = int(self.doctor_table.item(row,0).text())
        
        name = self.doctor_table.item(row,1).text()
        specialty = self.doctor_table.item(row,2).text()
        
        self.doctor_name_input.setText(name)
        self.doctor_specialty_input.setText(specialty)
    
    def save_schedule(self): 
        doctor_id = self.schedule_doctor_input.currentData()
        weekday = self.weekday_input.currentData()
        
        start_time = self.starttime_input.time().toString()
        end_time = self.endtime_input.time().toString()
        
        if doctor_id is None:
            QMessageBox.warning(
                self, "Missing doctor", "Please select a doctor."
            )
            return

        if start_time >= end_time:
            QMessageBox.warning(
                self,
                "Invalid hours",
                "End time must be after start time."
            )
            return
        try:
            schedule_id = save_update_schedule(doctor_id,weekday,start_time,end_time)
            QMessageBox.information(self,"Save Sucessful",f"Schedule saved succesfully with the id : {schedule_id}")
        except sqlite3.Error as e:
            QMessageBox.warning(self,"Save error","Schedule not saved properly")
    
    def search_doctor_schedule(self):
        search_id = self.schedule_search_input.text().strip()
        
        if not search_id:
            QMessageBox.warning(self,"Doctor ID is Empty","Enter doctor id for search")
            return
        schedules = search_schedule(search_id)
        self.schedule_table.setRowCount(len(schedules))
        
        for row_number,schedule in enumerate(schedules):
            for column_number,value in enumerate(schedule):
                item = QTableWidgetItem(str(value))
                self.schedule_table.setItem(row_number,column_number,item)
           
         
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)
    try:    
        create_tables()
        first_run = not has_staff_accounts()
    except sqlite3.Error as e:
        QMessageBox.critical(None,"Startup error",
        "Could not create or open the database.")
        return 1
    login = LoginDialog(first_run = first_run)
    if login.exec() != QDialog.Accepted:
        return 0
    window = HospitalWindow()
    window.show()
    return app.exec_()
if __name__ == "__main__":
    sys.exit(main())
