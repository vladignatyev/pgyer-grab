import os
import re
import requests

from plistlib import readPlistFromString, writePlist

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class PgyerGrab(object):
    MOBILE_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53'
    ITUNES_USER_AGENT = 'itunesstored/1.0 iOS/8.3 model/iPhone4,1 build/12F70 (6; dt:73)'

    def __init__(self, app_link, password=None):
        self.app_link = app_link
        self.password = password
        pass

    def log(self, s):
        print s

    def extract_app_key(self, source):
        found = re.findall("aKey = '(\w+)'", source)
        if len(found) > 0:
            return found[0]
        return None

    def grab(self, save_files=True):
        self.log('Loading Pgyer page: %s' % self.app_link)
        webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.User-Agent'] = PgyerGrab.MOBILE_USER_AGENT
        driver = webdriver.PhantomJS()
        driver.set_window_size(640, 960)  # iPhone 4S
        driver.get(self.app_link)

        self.log('Page loaded successfully.')

        app_key = self.extract_app_key(driver.page_source)

        if not app_key: # requires password
            driver.find_element_by_id('password').send_keys(self.password)
            driver.find_element_by_id('submitButton').click()
            
            download_btn = WebDriverWait(driver, 240).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[2]/div[1]/a"))
            )

            driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/a").click()

            app_key = self.extract_app_key(driver.page_source)

        self.log('Application key is %s' % app_key)

        driver.close()

        plist_url = 'https://ssl.pgyer.com/app/plist/%s/' % app_key
        plist_file = requests.get(plist_url, verify=False, headers={
            'user-agent': PgyerGrab.ITUNES_USER_AGENT
        })

        self.log('Plist file loaded')

        ipa_url = None
        image_url = None
        plist = readPlistFromString(plist_file.content)
        for asset in plist['items'][0]['assets']:
            if asset['kind'] == 'software-package':
                ipa_url = asset['url']
            elif asset['kind'] == 'full-size-image':
                image_url = asset['url']

        app_title = plist['items'][0]['metadata']['title']

        cwd = os.getcwd()

        new_path = '%(cwd)s/%(app_title)s' % { 'cwd': cwd, 'app_title': app_title }
        if not os.path.exists(new_path): 
            os.makedirs(new_path)

        if save_files:
            self.log('Saving .plist file...')
            writePlist(plist, '%s/Info.plist' % new_path)

        image_file = requests.get(image_url, verify=False, stream=True, headers={
            'user-agent': PgyerGrab.ITUNES_USER_AGENT
        })

        chunk_size = 1024

        if save_files:
            self.log('Downloading icon...')
            with open('%s/icon.png' % new_path, 'wb') as fd:
                for chunk in image_file.iter_content(chunk_size):
                    fd.write(chunk)

        ipa_file = requests.get(ipa_url, verify=False, stream=True, headers={
            'user-agent': PgyerGrab.ITUNES_USER_AGENT
        })

        if save_files:
            self.log('Downloading .ipa file...')
            with open('%s/app.ipa' % new_path, 'wb') as fd:
                for chunk in ipa_file.iter_content(chunk_size):
                    fd.write(chunk)




