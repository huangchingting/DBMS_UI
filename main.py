import sys  #python模組，輸入輸出都可用
from project_UI import Ui_MainWindow
import project_UI
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
import pymysql 


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


all_table = []
table_attr = {}
choose = False
db = pymysql.connect(host = 'localhost', user = 'root', password = 'mj1314520', database ='hotel')
cursor = db.cursor()
try:
        cursor.execute('SHOW TABLES;')
        results = cursor.fetchall() #取所有筆
        for r in results:
            table_name = str(r[0])
            all_table.append(table_name)
            cursor.execute("SHOW COLUMNS FROM %s" % table_name)
            table_attr[table_name] = [column[0] for column in cursor.fetchall()]
        print(table_attr)
except:
    print("Error: unable to fetch data")



class MainWindow(QMainWindow, project_UI.Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.output_table = self.ui.tableWidget
        self.MouseClick()

    def __del__(self):
        self.close()
        print("Database closed")

    def MouseClick(self):   #滑鼠點擊事件設置
        self.ui.pushButton.clicked.connect(self.on_click_query)
        self.ui.comboBox.addItems([' ', 'SELECT-FROM-WHERE', 'DELETE', 'INSERT', 'UPDATE',
                                'IN', 'NOT IN', 'EXISTS', 'NOT EXISTS',
                                'COUNT', 'SUM', 'MAX', 'MIN', 'AVG', 'HAVING','MYSQL'])
    
    def on_click_query(self):
        self.ui.output_table.clear()
        query_tool = self.ui.comboBox.currentText()
        command = self.ui.textEdit.toPlainText()
        if query_tool != 'MYSQL':
            if query_tool == 'SELECT-FROM-WHERE':
                command = 'SELECT * FROM VIP_ROOM WHERE extra_cost > 15000 '
            elif query_tool == 'DELETE':
                command = 'DELETE FROM FAMILY WHERE name = "Keely"'
            elif query_tool == 'INSERT':
                command = "INSERT INTO WINE VALUES(66, 7000, 'Brandy', 19500601)"
            elif query_tool == 'UPDATE': 
                command = "UPDATE EMPLOYEE SET department_id = 2 WHERE id = 39"
            elif query_tool == 'IN':
                command = "SELECT * FROM EMPLOYEE WHERE department_id IN (2, 3)"
            elif query_tool == 'NOT IN':
                command = "SELECT * FROM EMPLOYEE WHERE department_id NOT IN (2, 3)"
            elif query_tool == 'EXISTS':
                command = "SELECT FAMILY.*,EMPLOYEE.* FROM FAMILY,EMPLOYEE " \
                          "WHERE EXISTS " \
                          "(SELECT * FROM DEPARTMENT " \
                          "WHERE EMPLOYEE.id = DEPARTMENT.manager_id " \
                          "AND FAMILY.employee_id = EMPLOYEE.id " \
                          "AND DEPARTMENT.id_department = 2)" #department 2 manager的家屬
            elif query_tool == 'NOT EXISTS':
                command = "SELECT * FROM EMPLOYEE " \
                          "WHERE NOT EXISTS " \
                          "(SELECT * FROM FAMILY " \
                          "WHERE FAMILY.employee_id = EMPLOYEE.id)" #沒有家屬被記載的員工
            elif query_tool == 'COUNT':
                command = "SELECT COUNT(id) FROM EMPLOYEE WHERE birth >= 19910101" #小於30歲的員工個數
            elif query_tool == 'SUM':
                command = "SELECT SUM(extra_cost) FROM VIP_ROOM" #所有VIP_ROOM額外cost加總
            elif query_tool == 'MAX':
                command = "SELECT MAX(age) FROM EMPLOYEE"
            elif query_tool == 'MIN':
                command = "SELECT MIN(age) FROM EMPLOYEE"
            elif query_tool == 'AVG':
                command = "SELECT AVG(age) FROM EMPLOYEE"
            elif query_tool == 'HAVING':
                command = "SELECT brand, SUM(price) FROM WINE GROUP BY brand " \
                          "HAVING SUM(price) > 100000"


        try:
            cursor.execute(command)
            self.ui.textEdit_2.setText(command)
            action = command.split(' ')[0]
            if action == 'DELETE':
                cursor.execute('SELECT * FROM FAMILY')
            if action == 'INSERT':
                cursor.execute('SELECT * FROM WINE')
            if action == 'UPDATE':
                cursor.execute('SELECT * FROM EMPLOYEE')
            
            results = cursor.fetchall()
            #print(results)
            output = np.array(results)
            row, column = output.shape
            header = [x[0] for x in cursor.description]
            self.ui.output_table.setRowCount(row)
            self.ui.output_table.setColumnCount(column)
            self.set_header_attr(header)
            
            if output.shape == (1, 1) and is_number(output[0][0]):
                self.ui.output_table.setItem(0, 0, QTableWidgetItem(str(output[0][0])))
            else:
                for i in range(0, row):
                    for j in range(0, column):
                        item = QTableWidgetItem(str(output[i][j]))
                        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                        self.ui.output_table.setItem(i, j, item)

        except:
            print("Error: unable to fetch data")
            self.ui.textEdit_2.setText("Error: unable to fetch data")

        QTableWidget.resizeColumnsToContents(self.ui.output_table)
        QTableWidget.resizeRowsToContents(self.ui.output_table)

    
    def set_header_attr(self, header):
        self.ui.output_table.horizontalHeader().setStyleSheet('QHeaderView::section{'
                                                            'background: rgb(205, 179, 128); '
                                                            'border-color: rgb(226, 233, 233); '
                                                            'border-width: 1.2px; border-style:inset}')
        self.ui.output_table.horizontalHeader().setFixedHeight(35)
        self.ui.output_table.setHorizontalHeaderLabels(header)
        for x in range(self.ui.output_table.columnCount()):
            head = self.ui.output_table.horizontalHeaderItem(x)

        self.ui.output_table.setSelectionBehavior(QAbstractItemView.SelectRows)

            

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
