from PyQt5.QtWidgets import QApplication, QTextEdit

app = QApplication([])
text_edit = QTextEdit()
text_edit.setText("Hello, PyQt5!")
text_edit.show()
app.exec_()
