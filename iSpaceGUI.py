import sys
import asyncio
import datetime
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
            browser = p.chromium.launch(headless=False)
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
        self.center_window()
    
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
            border:1px solid #000;
            padding: 5px;
            border-radius: 10px;
        '''

        info_style = '''
            border: None;
            text-align: end;
        '''

        input_bar_style = '''
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
        
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        self.grid_layout.deleteLater()
        self.deleteLater()

    # @QtCore.pyqtSlot(QPixmap)
    def display_pixmap(self,pixmap):
        self.image_label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

    def center_window(self):
        # Get the screen size
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Get the window size
        window_width = self.width()
        window_height = self.height()

        # Calculate the center position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Set the window position
        self.move(x, y)

class ISpaceSettingPage(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ISpace Discussion Room")
        self.showMaximized()

    def ui(self):
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    controller = ISpaceLoginPage()
    controller.show()
    
    sys.exit(app.exec())