from selenium import webdriver
from HandlerVariable import HandlerVariable as hv
import time


def initialize(wd_path=None, url=None):
    global wd
    wd = webdriver.Chrome(executable_path=wd_path)
    wd.maximize_window()
    wd.get(url)
    time.sleep(2)
    print("Webdriver initialization is Successful!")
    return wd


def close_webdriver():
    global wd
    time.sleep(2)
    if wd is None:
        return
    print("Closing web driver.")
    wd.close()
    wd = None

def registration(wd_obj, user_name=None, password=None):
    pass



if __name__ == '__main__':
    url, wd_path = hv.url, hv.wd_path
    d = initialize(wd_path, url)
    d.find_element_by_xpath(hv.ac_xpath).click()
    d.find_element_by_xpath(hv.reg_xpath).click()
    print(d.title)
    # close_webdriver()