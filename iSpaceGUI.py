import sys
from datetime import datetime, timedelta
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QPixmap, QGuiApplication
from PyQt6.QtCore import QThread
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright


            #     start_date = input("Start date (YYYY/MM/DD): ")
            #     end_date = input("End date (YYYY/MM/DD): ")

                    #     date_1 = datetime.datetime.strptime(start_date,'%Y/%m/%d')
                    #     date_2 = datetime.datetime.strptime(end_date,'%Y/%m/%d')

                    #     interval = abs(date_2 - date_1).days

                    #     for i in range(interval):
                    #         await page.frame_locator('#contentframe').frame_locator('#iframePage').get_by_title('新增暫停使用空間').click()
                    #         await page.frame_locator('#contentframe').locator('#floor').select_option('圖書館1F')
                    #         await page.wait_for_timeout(2000)
                    #         await page.frame_locator('#contentframe').locator('label.chkboxAll').set_checked(True)
                    #         await page.wait_for_timeout(2000)
                    #         await page.frame_locator('#contentframe').locator('input.YYYYMMDD').click()
                    #         await page.wait_for_timeout(2000)
                    #         await page.frame_locator('#contentframe').get_by_title(date_1.strftime('%Y/%m/%d')).click()
                    #         await page.wait_for_timeout(2000)
                    #         await page.frame_locator('#contentframe').get_by_text('23:30~23:59').click()
                    #         await page.wait_for_timeout(2000)
                    #         await page.frame_locator('#contentframe').locator('div.pagefun').nth(0).get_by_title('新增暫停使用空間').click()
                    #         await page.wait_for_timeout(2000)

                    #         date_1 = date_1 + datetime.timedelta(days=1)



                    #     await page.wait_for_timeout(50000)

                # browser.close()

class IspaceController(QtCore.QObject):
    
    pixmap_ready = QtCore.pyqtSignal(QPixmap)
    clear_widget = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.page = None

    def capture_login_page(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('https://ispace-lis.nsysu.edu.tw/manager/loginmgr.aspx')
            
            clip_area = {
                'x': 760,
                'y': 325,
                'width': 150,
                'height': 26
            }
            screenshot = page.screenshot(clip=clip_area)
            self.page = page
            yield screenshot

    def on_login_button_clicked(self, userID, pwd, vc):
        # Fetch text from input fields and call the do_setting method
        id = self.page.get_by_placeholder('請輸入系統登入帳號')
        pw =  self.page.get_by_placeholder('請輸入系統登入密碼')
        captcha =  self.page.get_by_placeholder('請輸入認證文字')
        login_button =  self.page.get_by_title('登 入')

        id.fill(userID)
        pw.fill(pwd)
        captcha.fill(vc)
        login_button.click()

        if self.page.url == 'https://ispace-lis.nsysu.edu.tw/manager/loginmgr.aspx':
            return
        else:
            self.clear_widget.emit()
            self.page.frame_locator('#mainframe').get_by_title('空間管理').click()
            self.page.frame_locator('#subframe').get_by_title('小型討論室').click()
            self.page.frame_locator('#subframe').get_by_title('討論室暫停使用列表').first.click()        
    
    def display_screenshot(self):
        screenshot_generator = self.capture_login_page()

        pixmap = QPixmap()
        pixmap.loadFromData(QtCore.QByteArray(next(screenshot_generator)))
        self.pixmap_ready.emit(pixmap)




class ISpaceLoginPage(QtWidgets.QWidget):

    pixmap_ready = QtCore.pyqtSignal(QPixmap)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ISpace Settings")
        self.resize(500,300)
    
        self.controller = IspaceController()
        self.controllerThread = QThread()
        self.controller.moveToThread(self.controllerThread)
        self.controllerThread.start()
        self.controller.pixmap_ready.connect(self.display_pixmap)
        self.controller.clear_widget.connect(self.clear_all_widgets)
        self.ui()

    def ui(self):

        style_box = '''
            background:#fff;
            padding: 5px;
            border: None;
        '''

        info_style = '''
            border: None;
            text-align: end;
        '''

        input_bar_style = '''
            border: 1px solid black;
            border-radius: 10px;
            padding-right: 50px;
        '''

        captcha_style = '''
            border: None;
        '''

        grid_box = QtWidgets.QWidget(self)
        grid_box.setGeometry(0,0,500,300)
        grid_box.setStyleSheet(style_box)
        self.grid_layout = QtWidgets.QGridLayout(grid_box)

        self.userID = QtWidgets.QLabel(self)
        self.password = QtWidgets.QLabel(self)
        self.captcha = QtWidgets.QLabel(self)
        self.userID.setText("User ID: ")
        self.password.setText("Password: ")
        self.captcha.setText("Verification Code: ")
        self.userID.setStyleSheet(info_style)
        self.password.setStyleSheet(info_style)
        self.captcha.setStyleSheet(info_style)


        self.idInput = QtWidgets.QLineEdit(self)
        self.pwInput = QtWidgets.QLineEdit(self)
        self.captchaInput = QtWidgets.QLineEdit(self)
        self.image_label = QtWidgets.QLabel(self)
        self.loginButton = QtWidgets.QPushButton(self)
        self.loginButton.setText("Login")
        self.idInput.setStyleSheet(input_bar_style)
        self.pwInput.setStyleSheet(input_bar_style)
        self.captchaInput.setStyleSheet(input_bar_style)
        self.loginButton.setStyleSheet('''
            QPushButton {
                border: 1px solid black;
                border-radius: 10px;
            }

            QPushButton:hover {
                background: black;
                color: white;
            }
        ''')
        
        self.pwInput.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.image_label.setStyleSheet(captcha_style)

        self.controller.display_screenshot()

        self.grid_layout.addWidget(self.userID, 0, 0)
        self.grid_layout.addWidget(self.password, 1, 0)
        self.grid_layout.addWidget(self.captcha, 2, 0)
        self.grid_layout.addWidget(self.idInput, 0, 1)
        self.grid_layout.addWidget(self.pwInput, 1, 1)
        self.grid_layout.addWidget(self.captchaInput, 2, 1)
        self.grid_layout.addWidget(self.image_label, 2, 2)
        self.grid_layout.addWidget(self.loginButton, 3, 1)

        self.loginButton.clicked.connect(lambda: self.controller.on_login_button_clicked(self.idInput.text(), self.pwInput.text(), self.captchaInput.text()))

    def clear_all_widgets(self):
        
        # while self.grid_layout.count():
        #     item = self.grid_layout.takeAt(0)
        #     widget = item.widget()
        #     if widget:
        #         widget.deleteLater()
        
        # self.grid_layout.deleteLater()
        # self.deleteLater()
        self.setting_window = ISpaceSettingPage(self.controller)
        self.setting_window.show()

        self.close()

    # @QtCore.pyqtSlot(QPixmap)
    def display_pixmap(self,pixmap):
        self.image_label.setPixmap(pixmap)
        self.image_label.setFixedHeight(50)
        self.image_label.setFixedWidth(160)

    def center_window(self):
        # Get the screen size
        screen = QtWidgets.QApplication.screens()
        screen_size = screen[0].size()
        print(screen_size)
        screen_w = screen_size.width()
        screen_h = screen_size.height()

        w = self.width()
        h = self.height()

        center_x = int((screen_w - w)/2)
        center_y = int((screen_h - h)/2)
        self.move(center_x, center_y)


class ISpaceSettingPage(QtWidgets.QWidget):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.checkedDate_list = []
        self.setWindowTitle("ISpace Discussion Room")
        self.ui()
        self.showMaximized()

    def ui(self):
        
        layout_style = '''
            border: 1px solid #000;
            border-radius: 5px;
        '''

        label_style = '''
            border: None;
        '''

        select_style = '''
            border: 1px solid #000;
            border-radius: 0px;
        '''

        suspend_label_style = '''
            border: None;
            margin-left: 5px;
        '''

        layout_widget = QtWidgets.QWidget(self)
        layout_widget.setStyleSheet(layout_style)
        layout_widget.setGeometry(200,250,1500,500)
        self.layout = QtWidgets.QGridLayout(layout_widget)

        start_time = datetime.strptime('00:00', '%H:%M')
        end_time = datetime.strptime('23:59', '%H:%M')
        time_intervals = self.generate_time_intervals(start_time, end_time, 30)

        self.time_list = []
        
        self.container_floor = QtWidgets.QWidget(self)
        self.floor = QtWidgets.QComboBox(self.container_floor)
        self.floor.setStyleSheet(select_style)
        self.floor.setFixedSize(150,30)
        self.floor.addItems(['','圖書館1F', '圖書館6F', '圖書館7F', '圖書館8F'])
        self.floor.currentIndexChanged.connect(self.rooms_selections)
        self.layout.addWidget(self.floor, 0, 0)
        self.layout.setAlignment(self.floor, QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.setColumnMinimumWidth(0, 300)

        self.container = QtWidgets.QWidget(self)
        self.suspend_all = QtWidgets.QCheckBox(self.container)
        self.suspend_all.setText('暫停使用全部空間')
        self.suspend_all.setStyleSheet(label_style)
        self.suspend_all.setDisabled(True)
        self.suspend_all.clicked.connect(self.suspend_all_rooms)

        self.layout.addWidget(self.suspend_all, 1, 0)
        self.layout.setAlignment(self.suspend_all, QtCore.Qt.AlignmentFlag.AlignCenter)

        self.room_layout = QtWidgets.QHBoxLayout()
        self.room_1 = QtWidgets.QCheckBox(self)
        self.room_2 = QtWidgets.QCheckBox(self)

        self.room_1.setStyleSheet(label_style)
        self.room_2.setStyleSheet(label_style)

        self.room_layout.addWidget(self.room_1)
        self.room_layout.addWidget(self.room_2)
        self.room_layout.setAlignment(self.room_1, QtCore.Qt.AlignmentFlag.AlignRight)
        self.room_layout.setAlignment(self.room_2, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.room_layout.setContentsMargins(0,0,0,0)
        self.layout.addLayout(self.room_layout, 2, 0)
        self.room_1.setVisible(False)
        self.room_2.setVisible(False)


        column_index = 1
        row_index = 0
        
        for i in range(48):
            
            time = QtWidgets.QCheckBox(self)
            time.setText(time_intervals[i])
            time.setStyleSheet(label_style)
            time.clicked.connect(lambda checked, time=time: self.checked_date(time))

            self.time_list.append(time)
            self.layout.addWidget(time, row_index, column_index)
            self.layout.setAlignment(time, QtCore.Qt.AlignmentFlag.AlignRight)
            column_index += 1

            if column_index == 9: 
                column_index = 1
                row_index += 1

        self.suspend_date_container_a = QtWidgets.QHBoxLayout()
        self.suspend_date_start = QtWidgets.QDateEdit(calendarPopup=True)
        self.suspend_date_start.setFixedSize(120,30)
        self.suspend_date_start.setDisplayFormat('yyyy/MM/dd')
        self.suspend_date_start.setDate(QtCore.QDate.currentDate())
        self.suspend_date_start_label = QtWidgets.QLabel(self)
        self.suspend_date_start_label.setFixedSize(220,30)
        self.suspend_date_start_label.setStyleSheet(suspend_label_style)
        self.suspend_date_start_label.setText('暫停開始日期: ')
        self.suspend_date_container_a.addWidget(self.suspend_date_start_label)
        self.suspend_date_container_a.addWidget(self.suspend_date_start)

        self.suspend_date_container_b = QtWidgets.QHBoxLayout()
        self.suspend_date_end = QtWidgets.QDateEdit(self)
        self.suspend_date_end.setFixedSize(120,30)
        self.suspend_date_end.setDisplayFormat('yyyy/MM/dd')
        self.suspend_date_end.setDate(QtCore.QDate.currentDate())
        self.suspend_date_end_label = QtWidgets.QLabel(self)
        self.suspend_date_end_label.setStyleSheet(suspend_label_style)
        self.suspend_date_end_label.setText('暫停結束日期 : ')
        self.suspend_date_end_label.setFixedSize(220, 30)
        self.suspend_date_container_b.addWidget(self.suspend_date_end_label)
        self.suspend_date_container_b.addWidget(self.suspend_date_end)

        self.layout.addLayout(self.suspend_date_container_a, 3, 0)
        self.layout.addLayout(self.suspend_date_container_b, 4, 0)
      
        self.suspend_reason_container = QtWidgets.QHBoxLayout()
        self.suspend_reason_label = QtWidgets.QLabel(self)
        self.suspend_reason_label.setText('暫停使用原因: ')
        self.suspend_reason_label.setFixedSize(220,30)
        self.suspend_reason = QtWidgets.QLineEdit(self)
        self.suspend_reason.setFixedSize(120,30)
        self.suspend_reason_label.setStyleSheet(suspend_label_style)
        self.suspend_reason_container.addWidget(self.suspend_reason_label)
        self.suspend_reason_container.addWidget(self.suspend_reason)

        self.layout.addLayout(self.suspend_reason_container, 5, 0)

        self.add_suspend_button = QtWidgets.QPushButton(self)
        self.add_suspend_button.setText('新增暫停使用空間')
        self.add_suspend_button.setFixedSize(150,30)
        # self.add_suspend_button.clicked.connect(self.suspend_submit)
        self.layout.addWidget(self.add_suspend_button, 8, 7)

        # for i in range(48):
            # self.time_list[i].clicked.connect(lambda time=time: self.checked_date(time))

    def generate_time_intervals(self, start_time, end_time, interval_minutes):
        intervals = []
        current_time = start_time
        while current_time < end_time:
            end_interval = current_time + timedelta(minutes=interval_minutes - 1)
            intervals.append(f"{current_time.strftime('%H:%M')}~{end_interval.strftime('%H:%M')}")
            current_time += timedelta(minutes=interval_minutes)
        return intervals

    def rooms_selections(self):

        current_floors = self.floor.currentText()
        if current_floors == '':
            self.room_1.setVisible(False)
            self.room_2.setVisible(False)
            self.suspend_all.setDisabled(True)

        elif current_floors == '圖書館1F':
            self.room_1.setVisible(True)
            self.room_2.setVisible(True)
            self.room_1.setText('1A')
            self.room_2.setText('1B')
            self.suspend_all.setDisabled(False)

        elif current_floors == '圖書館6F':
            self.room_1.setVisible(True)
            self.room_2.setVisible(True)
            self.room_1.setText('6A')
            self.room_2.setText('6B')
            self.suspend_all.setDisabled(False)

        elif current_floors == '圖書館7F':
            self.room_1.setVisible(True)
            self.room_2.setVisible(True)
            self.room_1.setText('7A')
            self.room_2.setText('7B')
            self.suspend_all.setDisabled(False)

        elif current_floors == '圖書館8F':
            self.room_1.setVisible(True)
            self.room_2.setVisible(True)
            self.room_1.setText('8A')
            self.room_2.setText('8B')
            self.suspend_all.setDisabled(False)

    def checked_date(self, time):
        if time.isChecked():
            if time.text() not in self.checkedDate_list:
                self.checkedDate_list.append(time.text())
        else:
            if time.text() in self.checkedDate_list:
                self.checkedDate_list.remove(time.text())

        print(self.checkedDate_list)

    def suspend_all_rooms(self):

        self.room_1.setChecked(self.suspend_all.isChecked())
        self.room_2.setChecked(self.suspend_all.isChecked())

    # def suspend_submit(self):
        # print(self.controller.page.url)
        # try:
        #     date_1 = datetime.datetime.strptime(self.suspend_date_start.text(),'%Y/%m/%d')
        #     date_2 = datetime.datetime.strptime(self.suspend_date_end.text(),'%Y/%m/%d')

        # except:
        #     if len(self.checkedDate_list) == 0:
        #         if(date_1 == '' and date_2 != '')

        # interval = abs(date_2 - date_1).days



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    controller = ISpaceLoginPage()
    controller.show()
    
    sys.exit(app.exec())