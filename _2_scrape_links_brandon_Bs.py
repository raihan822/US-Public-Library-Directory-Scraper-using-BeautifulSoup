from constants import *
from custom_utils import *

import re
from datetime import datetime
import time
import csv
import multiprocessing
import requests
from bs4 import BeautifulSoup
import random
import traceback

# Logging related codes/settings follows: (Main logging formatter and handlers added in the 'constants.py
# module
import logging
mlog = logging.getLogger(__name__)

# START TIME:
start_time = time.time()

# Driver Keyboard btn pressing:
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains



# Driver Explicite Watings:
#Importing---
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


# Project Based helper function:

# Universal Helper function:
def is_captcha_checking(driver, url):
    # Captcha Checking Section:-------------------          # captcha selector: div.px-captcha-container div.px-captcha-message
    print("Captcha Checking section!")
    captcha_error_message_txt = ""
    captcha_message_txt = ""
    try:
        el_captcha_error_message = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.px-captcha-error-container div.px-captcha-error-message")))
        captcha_error_message_txt = el_captcha_error_message.text.strip()
    except:
        captcha_error_message_txt = ""

    try:
        el_captcha_message = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.px-captcha-container div.px-captcha-message")))
        captcha_message_txt = el_captcha_message.text.strip()
    except:
        captcha_message_txt = ""

    cp_err_ctr=0
    if "Press & Hold to confirm" in captcha_error_message_txt:
        while "Press & Hold to confirm" in captcha_error_message_txt and cp_err_ctr <= 3:
            print("Captcha got Freeze! Reloading..")
            cp_err_ctr += 1

            # Updating captcha_error_message_txt and captcha_message_txt both:
            try:
                el_captcha_error_message = WebDriverWait(driver, 15).until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "div.px-captcha-error-container div.px-captcha-error-message")))
                captcha_error_message_txt = el_captcha_error_message.text.strip()
            except:
                captcha_error_message_txt = ""
            try:
                el_captcha_message = WebDriverWait(driver, 15).until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "div.px-captcha-container div.px-captcha-message")))
                captcha_message_txt = el_captcha_message.text.strip()
            except:
                captcha_message_txt = ""

            # Reloading...
            driver.get(url)
            time.sleep(random.uniform(2.3,4.8))
            try:
                # Wait until there are no active network connections
                print("Waiting to finish loading the page..")
                WebDriverWait(driver, 30).until(lambda d: d.execute_script("return document.readyState") == "complete")
                print("Loading finished, no active connection.!")
            except:
                # minimum 60s wait or continue!
                print("loading may not finished! continuing..")
                pass
        if cp_err_ctr == 4:
            raise ValueError("Err: Captcha got Freeze!") #brings to outer except block!

    if "Press & Hold to confirm" in captcha_message_txt:
        print("You have 50 second to solve the captcha !!!")
        time.sleep(40)
        print("You only have 10s!..")
        time.sleep(10)
        try:
            WebDriverWait(driver, 40).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"ul.photo-cards")))
        except:
            try:
                el_captcha_message = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.px-captcha-container div.px-captcha-message")))
                raise ValueError("You didn't solve the captcha. Time ran-out!")
            except:
                pass
    else:       #if no captcha Triggerd!
        print("No captcha found. Proceeding")
        pass

def is_page_loaded_correctly(driver, url):
    indicator_searchboxDiv = "div#masterContentArea input#location-input-tab"
    #Loading page correctly:--
    try:
        try:        # Soft Wait -until there are no active network connections
            print("Waiting min 60s to finish loading the page..")
            WebDriverWait(driver, 60).until(lambda d: d.execute_script("return document.readyState") == "complete")
            print("Loading finished, no active connection.!")
        except:
            # minimum 60s wait or just continue!
            print(f"Still loading... {url}! ignoring...")
            pass

        #Checking if outer_div is present.
        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR,f"{indicator_searchboxDiv}")))
            print(f"page loaded correctly.. {url}")
        except:
            pass
            # div.rtsLevel.rtsLevel1

    except:
        print(f"Refreshing the URL {url} cause target element not found!")
        # driver.refresh()
        driver.get(url) # refreshes with new proxy?

        retry_ctr=0
        while retry_ctr <= 2:
            retry_ctr += 1
            try:
                WebDriverWait(driver, 50).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"{indicator_searchboxDiv}")))
                print(f"page loaded correctly.. {url}")
                break
            except:
                print(f"Refreshing the URL again {url}")
                # driver.refresh()
                driver.get(url)
                time.sleep(random.uniform(2.3,4.8))
        if retry_ctr >=3:
            raise ValueError(">>>>> The IP used to access the URL maybe blocked by the site??")
        else:
            pass

def is_items_revealed(driver, url):
    print("Revealing items....")

    # random scroll to refresh 'All Lots' btn read!
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(1.1,3.1))
    driver.execute_script("window.scrollTo(0, 0);")
    try:  # Soft Wait -until there are no active network connections
        print("waiting again as page still loading...")
        WebDriverWait(driver, 50).until(lambda d: d.execute_script("return document.readyState") == "complete")
        print(f"Loading finished during rev {url}")

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(0.5,1))
        driver.execute_script("window.scrollTo(0, 0);")
    except:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(0.5,1))
        driver.execute_script("window.scrollTo(0, 0);")
        # minimum 60s wait or just continue!
        print(f"continuing of revealing {url} thou load not finished")
        pass
    # ----------------------------------

    # Main section for waiting to reveal all:---------------
    item_cards_outerdiv = driver.find_element(By.CSS_SELECTOR, "div.group.mt-8.grid.w-full")
    try:
        item_cards = item_cards_outerdiv.find_elements(By.CSS_SELECTOR, "a")
        if not item_cards:
            raise ValueError("anchor not present")
    except:     # No item in the given auction link
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        try:
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.cursor-default.border-b.border-primary.font-din-pro span")))
        except:
            pass
        el_total_in_all_lots = driver.find_element(By.CSS_SELECTOR,"div.cursor-default.border-b.border-primary.font-din-pro span").text.strip()
        total_in_all_lots = int(el_total_in_all_lots.split('(')[-1].rstrip(')'))

        if total_in_all_lots == 0:
            print(f"There is NO item to reveal (item=0) at {url}!")
            init_total_in_all_lots = total_in_all_lots
            final_total_in_all_lots = total_in_all_lots
            return init_total_in_all_lots, final_total_in_all_lots
        else:
            try:
                WebDriverWait(item_cards_outerdiv, 12).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a")))
                item_cards = item_cards_outerdiv.find_elements(By.CSS_SELECTOR, "a")
            except:
                raise ValueError("something went wrong during catching anchor tags of cards")


    print("<<< Mini scroll_n_reveal test >>>")
    last_card_idx = len(item_cards) - 1
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item_cards[last_card_idx])
    try:
        # temporary card reveal trial..
        WebDriverWait(driver, 60).until(lambda d: len(item_cards_outerdiv.find_elements(By.CSS_SELECTOR, "a")) > len(item_cards))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item_cards[last_card_idx])

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0);")
    except:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0);")


    # Retrieving Total Card read count:------
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.cursor-default.border-b.border-primary.font-din-pro span")))
    except:
        pass
    el_total_in_all_lots = driver.find_element(By.CSS_SELECTOR, "div.cursor-default.border-b.border-primary.font-din-pro span").text.strip()
    total_in_all_lots = int(el_total_in_all_lots.split('(')[-1].rstrip(')'))
    init_total_in_all_lots = total_in_all_lots
    # print(f"'All Lots' = {total_in_all_lots} in URL: {url}")
    # --------------------------------

    print("<<< Now Revealing >>>")
    last_card_idx = len(item_cards) - 1
    print(f"initial last card idx: {last_card_idx}")
    while len(item_cards) < total_in_all_lots:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item_cards[last_card_idx])
        print("Waiting min 80s to load new cards...")
        try:
            WebDriverWait(driver, 80).until(lambda d: len(item_cards_outerdiv.find_elements(By.CSS_SELECTOR, "a")) > len(item_cards))
        except:
            print("waiting 20 more seconds...")
            WebDriverWait(driver, 20).until(lambda d: len(item_cards_outerdiv.find_elements(By.CSS_SELECTOR, "a")) > len(item_cards))
        time.sleep(random.uniform(1,1.8))

        # Refresh the card list and index
        item_cards = item_cards_outerdiv.find_elements(By.CSS_SELECTOR, "a")
        last_card_idx = len(item_cards) - 1
        print(f"now last card idx: {last_card_idx}")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    ## Double check:
    if total_in_all_lots != len(item_cards):
        print("'All Lots' and retrieved items are not equal. trying to fix...")
        time.sleep(random.uniform(1,1.5))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item_cards[last_card_idx])
    else:
        pass

    ##
    print(f"'All Lots' = {total_in_all_lots} | items revealed = {len(item_cards)} on URL: {url}")
    print("<<< Done Revealing! >>>")


    el_total_in_all_lots = driver.find_element(By.CSS_SELECTOR, "div.cursor-default.border-b.border-primary.font-din-pro span").text.strip()
    final_total_in_all_lots = int(el_total_in_all_lots.split('(')[-1].rstrip(')'))
    return init_total_in_all_lots, final_total_in_all_lots

# ---------------------------

### ------ Hero Function ------
def parse_page(soup, url):
    print("Entered to Function...")
    #------------------------------------
    el_state_name = soup.select_one("div#simplesearch p strong")
    state_name = el_state_name.text.strip()

    # el_library_anchors = soup.select("div#pagebodycontainer p a[href*='/library/']")
    el_all_library_outer_p_tags = soup.select("div#pagebodycontainer p:has(a)")

    all_library_links_in_a_state = []
    for lib_p_tag in el_all_library_outer_p_tags:   #setted a limit from 3rd item
        el_library_a_tag = lib_p_tag.select_one("a")
        a_library = {}

        try:

            #                              /library/14424
            el_library_link = el_library_a_tag['href'].strip()
            # https://librarytechnology.org/library/13004
            #                              /library/14424
            library_link = f"https://librarytechnology.org{el_library_link}"
        except:
            library_link = ""

        try:
            library_name = el_library_a_tag.text.strip()
        except:
            library_name = ""


        a_library['state_name'] = state_name
        a_library["lib_name"] = library_name
        a_library["lib_link"] = library_link
        print(f"===> {a_library}")

        all_library_links_in_a_state.append(a_library)

    print("Exiting Function...")
    return all_library_links_in_a_state



def scrape(qu_read, qu_write, st_Token, proxy_in_use):
    global glb_proxy
    glb_proxy = {"http": "http://" + proxy_in_use,
                 "https": "http://" + proxy_in_use}

    # disable when working with Selenium!
    proxy_in_use = {"http": "http://" + str(proxy_in_use).strip(),
                    "https": "http://" + str(proxy_in_use).strip()}
    headers = {
        "Connection": "close",  # another way to cover tracks
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
    }

    # Start Selenium Driver!!!! ===>>>
    driver = None
    # driver = get_uc_driver(proxy_in_use)

    while True:
        arr_in = qu_read.get()
        print("There are now " + str(qu_read.qsize()) + " unprocessed items in the input queue.")
        if arr_in == st_Token:
            try:
                driver.close() # only closes the active Tab
                driver.quit() # closes all Tabs and Quits the browser
            except:
                pass
            qu_read.task_done()
            break

        murl = arr_in.split("|")[0]
        err_ctr = 0
        while True:
            print("Processing url: " + murl)
            try:
                time.sleep(random.uniform(2.2, 3.5))

                #-----------BS-----------
                # s = requests.session()
                # s.headers = headers
                r = requests.get(murl, proxies=proxy_in_use, headers=headers, timeout=55)
                if r.status_code != 200:
                    raise ValueError("Could Not Fetch")
                soup = BeautifulSoup(r.content, "lxml")
                # print(soup.prettify())
                #______________________________________


                # # #-----------Selenium-----------
                # driver.get(murl) # Opens browser.
                # time.sleep(random.uniform(2.25, 3.7))

                library_links_in_a_state = parse_page(soup, murl)

                for dict in library_links_in_a_state:
                    arr_out = initiate_results_array() # has total size of 40
                    arr_out[0] = murl   # Main link
                    arr_out[1] = dict.get('state_name')
                    arr_out[2] = dict.get('lib_name')   # Auction Link
                    arr_out[3] = dict.get('lib_link')   # Auction Link

                    # Writer:
                    qu_write.put(arr_out)
                break

            except Exception as e:
                err_ctr+=1
                if err_ctr > 3:
                    mlog.error(f"ERR IS :{str(e)}. ---> URL WAS: {murl}")
                    print(f"Full error details after 3 retry: \n{traceback.format_exc()}")

                    arr_out = initiate_results_array()
                    arr_out[0] = murl
                    arr_out[err_col_index] = "[ERROR]"

                    # Writer:
                    qu_write.put(arr_out)
                    mlog.warning("Aborting a URL after 3 retries")
                    break
                else:
                    print("the error before trying again:\n",e)
                    print(f"ctr:{err_ctr} Trying again... {murl}")

        print("\n/////////////////// Done one row ////////////////////\n==================================================================")
        qu_read.task_done()


if __name__ == "__main__":


    num_of_processes = num_of_processes_in_links
    rows_in_a_batch = num_of_processes * 3

    print("Program starts now at: " + time.ctime())

    # waitIfCountryIsBD(driver)

    source_file_full_name = folder_for_all_files + era_links_source_filename
    output_file_full_name = folder_for_all_files + era_links_output_filename
    output_file_full_name_error = folder_for_all_files + "error_" + era_links_output_filename

    print("Program Starts Now ...")

    # <<<<<< Creating The Queues
    manager = multiprocessing.Manager()
    q_input = manager.Queue()
    q_output = manager.Queue()
    q_communicate = manager.Queue()

    STOP_TOKEN = "STOP!!!"
    STOP_TOKEN_WRITER = "STOP_WRITER!!!"

    # <<<<<<Setting Up the Writer Process

    writer_process_main = multiprocessing.Process(target=writer_main, args=(
        output_file_full_name, output_file_full_name_error, q_output, STOP_TOKEN_WRITER, q_communicate, rows_in_a_batch,
        err_col_index, new_output_after_row))


    writer_process_main.daemon = True
    writer_process_main.start()

    # >>>>>>>>>>>>>>
    # Start up the Main Scraper Processes

    jobs = []

    for a in range(num_of_processes):
        proc = multiprocessing.Process(target=scrape, args=(q_input, q_output, STOP_TOKEN, proxy_list[a]))
        jobs.append(proc)

    for j in jobs:
        j.daemon = True
        j.start()

    # The processes aouter_containerre now ready and running. They shall start working as soon as
    # Data are being put into the q_input

    # Now we read to get data from the source-text file and
    # put them inside the Input Queue
    # Work Starts as soon as q_input starts to populate

    with open(source_file_full_name, newline='', encoding='utf-8') as f:
        csv_f = csv.reader(f, delimiter=',', quotechar='"')

        for row in csv_f:
            print(row)
            ctr = 1
            strRow = ""
            for col in row:
                col = col.replace("|", "◆")
                if ctr == 1:
                    strRow = str(col)
                else:
                    strRow = strRow + "|" + str(col)
                ctr = ctr + 1

            q_input.put(strRow)

    # The job has now started in full.

    # We check if data has started to be produced by getting assurance from the writer via the
    # q_communicate queue
    while True:
        myString = q_communicate.get()
        if myString == "GOTTEN":
            print("The Writer has initiated")
            q_communicate.task_done()
            break

    # Wait for the main input queue (with input data) to become empty
    while not q_input.empty():
        print("Waiting for the input queue to become empty. Stop Token still NOT sent. All input data are NOT fed yet.")
        time.sleep(3)

    print(
        "All input data is consumed up by processs now. Maybe they are still processing them. But, the input queue is now empty for the first time.")

    # Send the Stop Token for the procedures to be fed.
    for a in range(num_of_processes):
        q_input.put(STOP_TOKEN)

    # now check if any of the process is still alive. if it is, just wait.
    # When all of them are dead - that shall mean that all of them consumed up the
    # stop tokens sent to them.

    while True:

        blnStillOneRunningAtleast = False
        for j in jobs:
            if j.is_alive():
                blnStillOneRunningAtleast = True

        if blnStillOneRunningAtleast == False:
            print("All worker processes died now. Shall proceed to stop the writer. ")
            break
        else:
            time.sleep(5)
            print("Atleast One Queue is running. Sent stop token to processing quues aready!")

    # Send the STOP_TOKEN_WRITER to the main writer through the output queue
    # Output queue shall have output data to be processed first.
    # therefore we can be sure that the stop token is processed last
    # This shall stop the writer process
    q_output.put(STOP_TOKEN_WRITER)

    # waiting for the main writer process to finish
    while writer_process_main.is_alive():
        print("Stop Token Sent to writer. waiting for the writer to process")
        time.sleep(1)

    print("Primary Scrape Procedure Ended at " + time.ctime())


#//////////////////////////////////////////////////////////////////////////////////
## END TIME & TIME CALCULATION:
end_time = time.time()
elapsed_time = end_time - start_time
minutes = int(elapsed_time // 60)
seconds = elapsed_time % 60
print("\nElapsed Time: {} minutes and {:.2f} seconds".format(minutes, seconds))