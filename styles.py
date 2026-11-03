APP_STYLE = """
QWidget {
    font-family: "Segoe UI";
    font-size: 10pt;
    color: #243247;
}

QWidget#HospitalWindow,
QDialog {
    background-color: #F1F5F9;
}

QLabel#PageTitle {
    font-size: 22pt;
    font-weight: bold;
    color: #153451;
}

QLabel#PageSubtitle {
    color: #64748B;
    font-size: 10pt;
}

QLabel#SummaryCard {
    background-color: #DBEAFE;
    color: #1E3A8A;
    border: 1px solid #BFDBFE;
    border-radius: 8px;
    padding: 12px;
    font-weight: bold;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #CBD5E1;
    background-color: white;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #E2E8F0;
    color: #475569;
    padding: 11px 18px;
    margin-right: 4px;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
}

QTabBar::tab:selected {
    background-color: #2563EB;
    color: white;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #DBEAFE;
    color: #1D4ED8;
}

/* Input fields */
QLineEdit,
QComboBox,
QDateEdit,
QTimeEdit,
QDateTimeEdit {
    background-color: white;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 7px;
    min-height: 22px;
    selection-background-color: #BFDBFE;
    selection-color: #172554;
}

QLineEdit:focus,
QComboBox:focus,
QDateEdit:focus,
QTimeEdit:focus,
QDateTimeEdit:focus {
    border: 2px solid #2563EB;
}

QComboBox QAbstractItemView {
    background-color: white;
    color: #243247;
    selection-background-color: #DBEAFE;
    selection-color: #1E3A8A;
}

/* Default buttons */
QPushButton {
    background-color: #2563EB;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 9px 16px;
    min-height: 22px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1D4ED8;
}

QPushButton:pressed {
    background-color: #1E40AF;
}

/* Save and completion buttons */
QPushButton[role="success"] {
    background-color: #15803D;
}

QPushButton[role="success"]:hover {
    background-color: #166534;
}

QPushButton[role="success"]:pressed {
    background-color: #14532D;
}

/* Cancellation buttons */
QPushButton[role="danger"] {
    background-color: #DC2626;
}

QPushButton[role="danger"]:hover {
    background-color: #B91C1C;
}

QPushButton[role="danger"]:pressed {
    background-color: #991B1B;
}

/* Secondary actions */
QPushButton[role="secondary"] {
    background-color: #E2E8F0;
    color: #334155;
}

QPushButton[role="secondary"]:hover {
    background-color: #CBD5E1;
}

QPushButton:disabled {
    background-color: #E2E8F0;
    color: #94A3B8;
}

/* Tables */
QTableWidget {
    background-color: white;
    alternate-background-color: #F1F5F9;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    gridline-color: #E2E8F0;
    selection-background-color: #DBEAFE;
    selection-color: #172554;
}

QTableWidget::item {
    padding: 6px;
}

QHeaderView::section {
    background-color: #153451;
    color: white;
    padding: 9px;
    border: none;
    border-right: 1px solid #36536F;
    font-weight: bold;
}

QToolTip {
    background-color: #153451;
    color: white;
    border: none;
    padding: 6px;
}
"""