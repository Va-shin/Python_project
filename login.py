import sqlite3

from PyQt5.QtWidgets import (
    QDialog,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QVBoxLayout,
    QMessageBox
)

from security import (
    create_first_account,
    create_staff_account,
    verify_login
)


class LoginDialog(QDialog):
    def __init__(self, first_run=False, register=False):
        super().__init__()

        self.first_run = first_run
        self.creating_account = first_run or register

        if self.creating_account:
            self.setWindowTitle("Create Staff Account")
        else:
            self.setWindowTitle("Staff Login")

        self.resize(380, 220)

        self.username_input = QLineEdit()

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.addRow("Username:", self.username_input)
        form.addRow("Password:", self.password_input)

        if self.creating_account:
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.Password)

            form.addRow(
                "Confirm Password:",
                self.confirm_input
            )

        button_text = (
            "Create Account"
            if self.creating_account
            else "Sign In"
        )

        self.submit_button = QPushButton(button_text)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.submit_button)

        # Show registration only on the sign-in screen.
        if not self.creating_account:
            self.register_button = QPushButton(
                "Create New Account"
            )

            layout.addWidget(self.register_button)

            self.register_button.clicked.connect(
                self.open_registration
            )

        self.setLayout(layout)

        self.submit_button.clicked.connect(self.submit)

    def open_registration(self):
        registration = LoginDialog(register=True)

        if registration.exec_() == QDialog.Accepted:
            # Copy the new username into the sign-in form.
            self.username_input.setText(
                registration.username_input.text().strip()
            )

            self.password_input.clear()
            self.password_input.setFocus()

    def submit(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(
                self,
                "Missing details",
                "Enter both username and password."
            )
            return

        try:
            if self.creating_account:
                confirmation = self.confirm_input.text()

                if password != confirmation:
                    raise ValueError(
                        "Passwords do not match."
                    )

                if self.first_run:
                    create_first_account(username, password)
                else:
                    create_staff_account(username, password)

                QMessageBox.information(
                    self,
                    "Account created",
                    "Staff account created successfully."
                )

            else:
                if not verify_login(username, password):
                    QMessageBox.warning(
                        self,
                        "Sign-in failed",
                        "Incorrect username or password."
                    )

                    self.password_input.clear()
                    self.password_input.setFocus()
                    return

        except (ValueError, sqlite3.Error) as e:
            QMessageBox.warning(
                self,
                "Account error",
                str(e)
            )
            return

        self.accept()