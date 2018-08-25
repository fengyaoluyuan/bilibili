import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

EMAIL = ''
PASSWORD = ''
BORDER = 2
INIT_LEFT = 70


class CrackGeetest():
    def __init__(self):
        self.url = 'https://passport.bilibili.com/login?gourl=https://space.bilibili.com'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.email = EMAIL
        self.password = PASSWORD
    
    def __del__(self):
        self.browser.close()
    
    def get_geetest_button(self):
        """
        获取初始验证按钮
        :return:
        """
        button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#gc-box > div > div.gt_slider > div.gt_slider_knob.gt_show')))
        return button
    
    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        img = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#gc-box > div > div.gt_widget.gt_clean.gt_show')))
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)
    
    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot
    
    # def get_slider(self):
    #     """
    #     获取滑块
    #     :return: 滑块对象
    #     """
    #     slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
    #     return slider
    
    def get_geetest_image(self, name='captcha.png'):
        """
        获取验证码图片
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha
    
    def open(self):
        """
        打开网页输入用户名密码
        :return: None
        """
        self.browser.get(self.url)
        email = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#login-username')))
        password = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#login-passwd')))
        email.clear()
        email.send_keys(self.email)
        password.clear()
        password.send_keys(self.password)
    
    def get_gap(self, image1, image2):
        """
        获取缺口偏移量
        :param image1: 不带缺口图片
        :param image2: 带缺口图片
        :return:
        """
        left = INIT_LEFT
        for i in range(left, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    gap = i
                    print(gap)
                    return gap

        return gap

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        #效果不佳
        # thresholdL = 40
        # print(type(image1))
        # image1L = image1.convert('L')
        # table1 = []
        # for i in range(256):
        #     if i < thresholdL:
        #         table1.append(0)
        #     else:
        #         table1.append(1)
        # image1 = image1L.point(table1, '1')
        # print(type(image1))
        # image1.save('1.png')
        # image2L = image2.convert('L')
        # table2 = []
        # for i in range(256):
        #     if i < thresholdL:
        #         table2.append(0)
        #     else:
        #         table2.append(1)
        # image2 = image2L.point(table2, '1')
        # image2.save('2.png')

        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        #阈值的选取
        threshold = 60
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False
    
    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0
        
        while current < distance:
            if current < mid:
                # 加速度为正2
                a = 2
            else:
                # 加速度为负3
                a = -3
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return track
    
    def move_to_gap(self, button, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.browser).click_and_hold(button).perform()
        for x in track:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()
    
    def login(self):
        """
        登录
        :return: None
        """
        submit = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#login-app > div > div > div.login-box.clearfix > div.login-right > div > div > ul > li.btn-box > a.btn.btn-login')))
        submit.click()
        time.sleep(10)
        print('登录成功')
    
    def crack(self):
        # 输入用户名密码
        self.open()
        # 点击验证按钮
        button = self.get_geetest_button()
        ActionChains(self.browser).move_to_element(button).perform()
        time.sleep(0.5)
        # 获取验证码图片
        image1 = self.get_geetest_image('captcha1.png')
        # 点按呼出缺口
        # slider = self.get_slider()
        button.click()
        # 获取带缺口的验证码图片
        image2 = self.get_geetest_image('captcha2.png')
        # 获取缺口位置
        gap = self.get_gap(image1, image2)
        print('缺口位置', gap)
        # 减去缺口位移
        gap -= BORDER
        # 获取移动轨迹
        track = self.get_track(gap)
        print('滑动轨迹', track)
        # 拖动滑块
        self.move_to_gap(button, track)
        print('释放滑块')
        time.sleep(5)
        if not self.browser.current_url == self.url:
            print('success')
            self.login()
        
        # 失败后重试
        else:
            self.crack()


if __name__ == '__main__':
    crack = CrackGeetest()
    crack.crack()
