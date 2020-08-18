import os
import time

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException



#### initialization ####
conf = None
log = None
dut = None
wd = None


def initialize():
    global wd
    url = "https://www.opencart.com/"
    wd = openWebDriver(url)
    webLogin()


def cleanup():
    closeWebDriver()



#### utilities ####
def openWebDriver(url=None):
    global wd
    wd = webdriver.Firefox()
    wd.set_page_load_timeout(30)
    wd.get(url)
    print('Web Driver Initialized')
    time.sleep(2)
    return (wd)


def closeWebDriver():
    global wd
    if (wd == None):
        return
    print('Closing WebDriver')
    wd.close()
    wd = None


def _sel2py(value):
    if (type(value) == unicode):
        value = str(value)
        if (value.isdigit()):
            value = int(value)
    return (value)


def _webElement(funcPointer):
    def funcWrapper(*args, **kwargs):
        timeout = kwargs.pop('timeout', 20)
        waitForEnabled = kwargs.pop('waitForEnabled', True)
        # log.debug('kwargs: %s', kwargs)
        if (len(kwargs.keys()) > 1):
            assert (False), '_webElement() did not support multiple element'
        funcDict = {
            'text': wd.find_element_by_link_text,
            'xpath': wd.find_element_by_xpath,
            'id': wd.find_element_by_id,
            'name': wd.find_element_by_name,
        }
        eType = kwargs.keys()[0]
        element = kwargs[eType]
        findElementFunc = funcDict[eType]
        timeSlice = 0.4
        err = None
        for i in range(int(timeout / timeSlice)):
            try:
                eObj = findElementFunc(element)
                if (waitForEnabled):
                    if (not eObj.is_displayed()):
                        log.debug('waiting for element display')
                        time.sleep(timeSlice)
                        continue
                    if (not eObj.is_enabled()):
                        log.debug('waiting for element enable')
                        time.sleep(timeSlice)
                        continue
                (ret, infoStr) = funcPointer(eObj, *args, **kwargs)
                log.debug('%s %s: %s', infoStr, eType, element)
                return (_sel2py(ret))
            except exceptions.NoSuchElementException as err:
                log.warning(str(err).strip())
            except exceptions.StaleElementReferenceException as err:
                log.warning(str(err).strip())
            time.sleep(timeSlice)
        err and log.exception(err)
        assert False, 'TIMEOUT: did not found element %s: %s' % (eType, element)

    return (funcWrapper)


@_webElement
def click(eObj, *args, **kwargs):
    eObj.click()
    time.sleep(0.5)
    infoStr = 'clicked on'
    return (True, infoStr)


@_webElement
def sendKeys(eObj, sendKeys, *args, **kwargs):
    eObj.clear()
    eObj.send_keys(str(sendKeys))
    time.sleep(1)  # min wait for value to reflect on web page
    infoStr = 'sent keys[%s] to' % (sendKeys)
    return (True, infoStr)


@_webElement
def mouseOver(eObj, *args, **kwargs):
    action = ActionChains(wd).move_to_element(eObj)
    action.perform()
    infoStr = 'moved mouse pointer to'
    return (True, infoStr)


@_webElement
def selectText(eObj, selectText, *args, **kwargs):
    selectObj = Select(eObj)
    selectObj.select_by_visible_text(str(selectText))
    infoStr = 'selected text[%s] in' % (selectText)
    return (True, infoStr)


@_webElement
def selectValue(eObj, selectValue, *args, **kwargs):
    selectObj = Select(eObj)
    selectObj.select_by_value(str(selectValue))
    infoStr = 'selected value[%s] in' % (selectValue)
    return (True, infoStr)


@_webElement
def getText(eObj, *args, **kwargs):
    ret = eObj.text
    infoStr = '%s: text got from' % (ret)
    return (ret, infoStr)


@_webElement
def getAttrib(eObj, attrib, *args, **kwargs):
    ret = eObj.get_attribute(attrib)
    infoStr = '%s: value got from attrib[%s] of' % (ret, attrib)
    return (ret, infoStr)


@_webElement
def getValue(eObj, *args, **kwargs):
    ret = eObj.get_attribute('value')
    infoStr = '%s: value got from text box of' % (ret)
    return (ret, infoStr)


@_webElement
def getSelect(eObj, *args, **kwargs):
    selectObj = Select(eObj)
    ret = selectObj.first_selected_option.text
    infoStr = '%s: value currently selected in' % (ret)
    return (ret, infoStr)


@_webElement
def getRadio(eObj, *args, **kwargs):
    ret = eObj.is_selected()
    infoStr = '%s: radio value got from' % (ret)
    return (ret, infoStr)


@_webElement
def getCheckbox(eObj, *args, **kwargs):
    ret = eObj.is_selected()
    infoStr = '%s: checkbox value got from' % (ret)
    return (ret, infoStr)


@_webElement
def getTableData(eObj, *args, **kwargs):
    # wait for table to visible
    while (eObj.text.find('Loading') != -1):
        log.debug('Waiting for table data')
        time.sleep(0.5)
    # parsing headers
    tableHeaders = []
    headerList = eObj.find_elements_by_xpath('thead/tr/th')
    for header in headerList:
        tableHeaders.append(str(header.text))
    # parsing rows
    tableData = []
    trList = eObj.find_elements_by_xpath('tbody/tr')
    for tr in trList:
        tdList = tr.find_elements_by_xpath('td')
        row = []
        for td in tdList:
            if (td.text.isdigit()):
                row.append(int(td.text))
            else:
                row.append(str(td.text))
        tableData.append(row)
    ret = [tableHeaders, tableData]
    infoStr = 'successfully read table' % (ret)
    return (ret, infoStr)


def webLogin():
    dutUser = conf.get('UMPLUS', 'dutUser')
    sendKeys(dutUser, id=fc.loginUserId)
    dutPasswd = conf.get('UMPLUS', 'dutPasswd')
    sendKeys(dutPasswd, id=fc.loginPassId)
    click(xpath=fc.loginBtnXpath)


