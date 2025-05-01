'''
from lxml import html
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil
import os
from random import randint
'''

import logging
mlog = logging.getLogger(__name__)


import datetime
import constants

import requests
from selenium.webdriver.common.by import By

import json
import time
# For agate - image captcha solve
import undetected_chromedriver as uc
import os
from PIL import Image
from antigate import AntiGate
try:
    import http.cookiejar as clib
except ImportError:
    import cookielib as clib

import csv

glb_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
glb_proxy = ""
glb_headers = {
    "Connection": "close",  # another way to cover tracks
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
glb_dr_ckJar = clib.CookieJar()

prxCount = 0

current_file_full_path = os.path.realpath(__file__)
current_folder = os.path.dirname(os.path.dirname(current_file_full_path))
PyWorksFolderPath = os.path.dirname(current_folder)
resources_directory = os.path.expanduser('~/_bants_resources/m_resources')
data_directory = constants.data_folder_name
geckodriver_path = resources_directory + r"/geckodriver64.exe"
phantom_driverPath = resources_directory + r"/phantomjs.exe"
chrome_driverPath = resources_directory + r"/chromedriver.exe"

folder_for_all_files = data_directory + "/"

proxy_list = []

# get agate key


with open(resources_directory + r"/_basic_captcha_agate_key.txt") as f:
    content = f.readlines()
agate_key = content[0]

with open(resources_directory + r"/_recaptcha_2captcha_key.txt") as f:
    content = f.readlines()
recaptcha_2captcha_api_key = content[0]

with open(resources_directory + r"/_crawlera_key.txt") as f:
    content = f.readlines()
crawlera_key = content[0]

#print(agate_key)
#print(recaptcha_2captcha_api_key)





def beat_captcha_basic(driver, image_element, answer_box_element, submit_button_element):
    time.sleep(2)
    captcha = ""

    p_id = os.getpid()

    time.sleep(5)

    driver.execute_script("arguments[0].scrollIntoView(true);", image_element)

    location = image_element.location
    size = image_element.size
    driver.save_screenshot(resources_directory + '/screenshot_' + str(p_id) + '.png')
    im = Image.open(resources_directory + '/screenshot_' + str(p_id) + '.png')
    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    im = im.crop((left, top, right, bottom))
    im.save(resources_directory + '/captcha_' + str(p_id) + '.png')

    captcha = AntiGate(agate_key, resources_directory + '/captcha_' + str(p_id) + '.png')
    if str(captcha) == "":
        raise ValueError('Did not get response from antigate')

    print(str(captcha))

    # Write down answer
    answer_box_element.clear()
    answer_box_element.send_keys(str(captcha))

    # Click submit button
    driver.execute_script("arguments[0].click();", submit_button_element)
    time.sleep(2)

    return driver


def beat_captcha_recaptcha(driver, my_proxy, running_site_key, element_answer_text_area, element_submit_button):
    # Add these values
    API_KEY = recaptcha_2captcha_api_key  # Your 2captcha API KEY
    site_key = running_site_key  # site-key, read the 2captcha docs on how to get this
    url = driver.current_url
    proxy = my_proxy

    proxy = {'http': 'http://' + proxy, 'https': 'https://' + proxy}

    s = requests.Session()

    # here we post site key to 2captcha to get captcha ID (and we parse it here too)
    captcha_id = s.post(
        "http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(API_KEY,
                                                                                                site_key, url),
        proxies=proxy).text.split('|')[1]
    # then we parse gresponse from 2captcha response
    print('captcha_id is ' + str(captcha_id))

    recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id),
                             proxies=proxy).text
    print("solving ref captcha...")
    while 'CAPCHA_NOT_READY' in recaptcha_answer:
        time.sleep(5)
        recaptcha_answer = s.get(
            "http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id),
            proxies=proxy).text
    recaptcha_answer = recaptcha_answer.split('|')[1]

    print('recaptcha_answer is ' + str(recaptcha_answer))

    # Now paste the answer and submit
    driver.execute_script(
        "arguments[0].style.visibility = 'visible'; arguments[0].style.height = '40px'; arguments[0].style.width = '250px'; arguments[0].style.opacity = 1; arguments[0].style.display = 'inline-block';",
        element_answer_text_area)
    print('element made visible')
    time.sleep(2)

    element_answer_text_area.clear()
    element_answer_text_area.send_keys(recaptcha_answer)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", element_submit_button)
    time.sleep(2)
    return driver


# Setting up the proxy list
def set_proxy_list():
    global proxy_list
    proxy_list = []

    proxy_filepath = os.path.expanduser('~/_bants_resources/mproxies.csv')

    with open(proxy_filepath, newline='', encoding='utf-8') as csvfile:
        resultset = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in resultset:
            if row[1].strip() == constants.use_proxies_from:
                proxy_list.append(str(row[2]).strip())



def get_driver_cookie_jar(driver):
    print('Waiting 20 seconds before getting cookies...')
    time.sleep(20)
    driver_cookies = driver.get_cookies()
    new_cookie_jar = clib.CookieJar()

    for dr_cookie in driver_cookies:
        ck = clib.Cookie(name=dr_cookie['name'], value=dr_cookie['value'], domain=dr_cookie['domain'],
                         path=dr_cookie['path'],
                         secure=dr_cookie['secure'],
                         rest=False, version=0, port=None, port_specified=False, domain_specified=False,
                         domain_initial_dot=False, path_specified=True, expires=dr_cookie['expiry'], discard=True,
                         comment=None,
                         comment_url=None, rfc2109=False)
        new_cookie_jar.set_cookie(ck)

    return new_cookie_jar


def wait_if_country_is_bd_set_user_agent(driver):
    # This one's from class
    # Use the following adjusted code (without useragent) for checking country.
    ctr = 0
    while True:

        try:
            driver.get("http://ip-api.com/json")
            time.sleep(0.5)
            try:
                el = driver.find_element(By.LINK_TEXT, "Raw Data")
                driver.execute_script("arguments[0].click();", el)
            except:
                pass

            json_text = driver.find_element(By.TAG_NAME, "pre").text.strip()
            print("json_text: " + str(json_text))
            hey = json.loads(json_text)
            mcountry = hey["country"].strip()

            if mcountry.lower() == "Bangladesh".lower():
                print("IPCheck: Failure. The IP is from Bangladesh. Please change IP before proceeding.")
                time.sleep(5)
            else:
                print("IPCheck: Success. The IP is from " + mcountry + ". We shall now proceed.")
                break

        except Exception as e:

            try:
                driver.close()
                driver.quit
            except:
                pass

            raise ValueError(
                "IPCheck: Failure. Cannot complete requests: Probably no internet connection exists. Trying again ...Err Message is: \n " + str(
                    e))

    return driver

def get_uc_driver(proxy_to_use):

    options = uc.ChromeOptions()

    proxy_to_use = str(proxy_to_use).strip()
    if proxy_to_use is None:
        raise ValueError("No proxy is supplied to the chromedriver. Must supply ip address while initiating.")
    elif str(proxy_to_use).strip() == "":
        raise ValueError("No proxy is supplied to the chromedriver. Must supply ip address while initiating.")
    elif ":" not in str(proxy_to_use).strip():
        raise ValueError("The supplied proxy is not of proper structure.")
    else:
        print("We shall proceed on with the following supplied proxy: " + str(proxy_to_use).strip())

    brain_folder = os.path.expanduser('~/_bants_resources')

    print("parent folder of resources folder is: " + str(brain_folder))

    # Adding proxy:
    options.add_argument(f'--proxy-server={proxy_to_use}')
    options.add_argument('--proxy-server=socks5://' + str(proxy_to_use).strip())  # socks5
    options.add_argument('--proxy-server=https://' + str(proxy_to_use).strip())  # https
    options.add_argument(
        '--proxy-server=http://' + str(proxy_to_use).strip())  # http: This one is added by me. the http, without 's'

    options.page_load_strategy = "eager"  # Wait for Dom load complete, but not other resources like CSS or javascript

    # We add all the addons in one line:
    options.add_argument(
        '--load-extension=' + brain_folder + "/m_resources" + '/webrtc_leak_shield,' +  brain_folder + "/m_resources" + '/canvasf')


    options.add_argument("--no-sandbox")  # To avoid issues in some environments (e.g., Docker)
    options.add_argument("--disable-dev-shm-usage") # Reduces the possibility of running into shared memory issues.

    print("We shall initiate the driver now.")

    try:
        driver = uc.Chrome(options=options, headless=False, use_subprocess=True, version_main=114)
    except Exception as e:
        raise ValueError("The driver could not be initiated. Error was: " + str(e))

    driver.set_page_load_timeout(constants.driver_page_load_timeout)
    #driver.implicitly_wait(constants.driver_implicit_wait)

    for window_handle in driver.window_handles:
        driver.switch_to.window(window_handle)
        if "trace" not in driver.title.strip().lower():
            chosen_window_handle = window_handle

    driver.switch_to.window(chosen_window_handle)

    driver = wait_if_country_is_bd_set_user_agent(driver)

    return driver

def initiate_results_array():
    results_array = []
    for a in range(constants.num_of_columns_in_output_file):
        results_array.append("")

    return results_array


def set_requests_details_from_driver(driver):
    global glb_dr_ckJar
    global glb_headers

    glb_dr_ckJar = get_driver_cookie_jar(driver)
    glb_headers = {
        "Connection": "close",  # another way to cover tracks
        "User-Agent": glb_user_agent}
    return driver


def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i + n]

def writer_main(dest_file_name, error_file_name, output_queue, the_stop_token, communicate_queue,
               num_of_rows_in_a_batch, err_col_index, new_output_after_row):
    print("Main output writer is initiated")

    stTime = datetime.datetime.now()
    rCount = 1
    g_arr = []

    csv.register_dialect(
        'mydialect',
        delimiter=',',
        quotechar='"',
        doublequote=True,
        skipinitialspace=True,
        lineterminator='\r\n',
        quoting=csv.QUOTE_ALL)

    # Before loop starts (for appending serials after the det file name.
    fcycle = 1
    fname_cycle = 1
    dest_file_name_root = dest_file_name.replace(".csv", "")

    while True:

        line = output_queue.get()

        communicate_queue.put("GOTTEN")
        rCount = rCount + 1

        fcycle = fcycle + 1
        if fcycle > new_output_after_row:
            fname_cycle = fname_cycle + 1
            fcycle = 1

        dest_file_name = dest_file_name_root + "_" + str(fname_cycle) + ".csv"
        # print("dest_file_name is: " + dest_file_name)

        if line == the_stop_token:

            with open(dest_file_name, 'a', newline='', encoding='utf-8') as mycsvfile:
                thedatawriter = csv.writer(mycsvfile, dialect='mydialect')
                for row in g_arr:
                    thedatawriter.writerow(row)

            g_arr = []

            print("Main Main Writer Now Stops")

            return

        # New part log errrors @ start
        if line[err_col_index].strip() == "[ERROR]":
            with open(error_file_name, 'a', newline='', encoding='utf-8') as mycsvfile:
                thedatawriter = csv.writer(mycsvfile, dialect='mydialect')
                thedatawriter.writerow(line)
        else:
            g_arr.append(line)

        if len(g_arr) >= num_of_rows_in_a_batch:

            with open(dest_file_name, 'a', newline='', encoding='utf-8') as mycsvfile:
                thedatawriter = csv.writer(mycsvfile, dialect='mydialect')
                for row in g_arr:
                    thedatawriter.writerow(row)
            g_arr = []

            diff = datetime.datetime.now() - stTime

            print("A Batch of records is now written to file. Time spent per record (from beginning) is " + str(
                (diff.seconds) / rCount) + " seconds.")




set_proxy_list()