# total: 17153

import traceback
from urllib.parse import urlparse
import re
from datetime import datetime


from selenium.webdriver.support.expected_conditions import none_of

from constants import *
from custom_utils import *
import time
import csv
import multiprocessing
import requests
from bs4 import BeautifulSoup
import random

# Logging related codes/settings follows:
import sys
# Logging related codes/settings follows: (Main logging formatter and handlers added in the 'constants.py
# module
import logging
mlog = logging.getLogger(__name__)

# START TIME:
start_time = time.time()

# Driver Explicite Watings:
#Importing---
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def normalize_org(text: str) -> str:
    # 1. Collapse all whitespace (remove newlines & extra spaces)
    flat = " ".join(text.split())

    # 2. Drop any single trailing period
    flat = flat.rstrip(".")

    # 3. Handle the three different prefixes:
    low = flat.lower()
    if low.startswith("this is a "):
        flat = flat[len("this is a "):]
    elif low.startswith("the library is part of a "):
        # replace with "Part of a "
        flat = "Part of a " + flat[len("the library is part of a "):]
    elif low.startswith("it "):
        # drop just "It "
        flat = flat[len("it "):]

    # 4. Strip off a trailing " library" if present
    flat = re.sub(r'\s+library$', "", flat, flags=re.I)

    # 5. Split into “main” vs. “detail” on the first sentence‐break
    parts = flat.split(". ", 1)
    main_raw = parts[0].strip()
    # Capitalize *only* the first letter, preserve the rest
    main = main_raw[:1].upper() + main_raw[1:] if main_raw else ""

    # 6. If there *is* a second sentence, pull it into parentheses
    if len(parts) == 2 and parts[1].strip():
        detail_raw = parts[1].strip()
        # drop a leading "It " if present
        if detail_raw.lower().startswith("it "):
            detail_raw = detail_raw[len("it "):]
        detail = detail_raw[:1].upper() + detail_raw[1:]
        return f"{main} ({detail})"

    return main

def parse_profile(soup, url):
    print("Entered to Function...")
    # =============================================================================
    # library name [already have]
    a_library_dict = {}

    # The Outer Div:
    el_outer_div = soup.select_one("div#maincontencolumn")

    # Address section:
    el_address_div = ""
    try:
        el_address_div = el_outer_div.select_one("div[itemprop='address']")
    except:
        pass
    # ---------------------------
    try:
        el_street_addrs = el_address_div.select_one("span[itemprop='streetAddress']")
        street_addrs = el_street_addrs.text.strip()
    except:
        street_addrs = ""

    try:
        el_mailing_addrs = el_address_div.select_one("span[itemprop='postOfficeBoxNumber']")
        mailing_addrs = el_mailing_addrs.text.strip()
    except:
        mailing_addrs = ""

    try:
        el_city = el_address_div.select_one("span[itemprop='addressLocality']")
        city = el_city.text.strip()
    except:
        city = ""

    try:
        el_state_name = el_address_div.select_one("span[itemprop='addressRegion']")
        state_name = el_state_name.text.strip()
    except:
        state_name = ""

    try:
        el_zip_code = el_address_div.select_one("span[itemprop='postalCode']")
        zip_code = el_zip_code.text.strip()
    except:
        zip_code = ""

    try:
        el_country = el_address_div.select_one("span[itemprop='addressCountry']")
        country = el_country.text.strip()
    except:
        country = ""

    # County:
    try:
        el_county = el_address_div.select("p a strong")[-1]  # last er ta!
        county = el_county.text.strip()
    except:
        county = ""

    try:
        el_phone_num = el_outer_div.select_one("span[itemprop='telephone']")
        phone_num = el_phone_num.text.strip()
    except:
        phone_num = ""

    try:
        el_library_own_website = el_outer_div.select_one("p a[itemprop='url']")
        library_own_website_str = el_library_own_website['href'].strip()
        # ----------------------------------------
        parsed_url = urlparse(library_own_website_str)
        library_own_website = f"{parsed_url.scheme}://{parsed_url.netloc}"  # Output: scheme = https :// netloc = www.cityofashlandal.com
        # ----------------------------------------
    except:
        library_own_website = ""

    try:
        el_online_catalog = el_outer_div.select_one("p a[onclick*='Catalog']")
        online_catalog = el_online_catalog['href']
    except:
        online_catalog = ""

    # Details Section:
    el_details_div = ""
    full_details_txt = ""
    try:
        el_details_div = el_outer_div.select_one("p span[itemprop='description']")
        # full_details_txt = el_details_div.text.strip()
        full_details_txt = el_details_div.get_text(strip=True)
    except:
        pass
    # ---------------------------

    try:
        el_library_type = el_details_div.select("strong")[1]
        library_type = el_library_type.text.strip()
    except:
        library_type = ""

    try:
        el_parent_org = el_details_div.select("strong")[2]
        parent_org = el_parent_org.text.strip()
    except:
        parent_org = ""


    try:
        el_permalink = el_outer_div.select_one("p a[href*='https://librarytechnology.org/library/']")
        permalink = el_permalink['href']
    except:
        permalink = ""

    try:
        el_director_name = el_outer_div.select_one("div span[itemprop='name']")
        director_name = el_director_name.text.strip()
    except:
        director_name = ""

    org_structure = ""
    full_org_structure_txt = ""
    try:
        el_org_structure_p = el_outer_div.select("div p")
        for p in el_org_structure_p:
            span = p.select_one("span.detailheader")
            if span and span.get_text(strip=True) == "Organizational structure:":
                el_full_p_str = p.text.strip()
                el_rest_full = el_full_p_str.replace("Organizational structure:","",1).strip()

                full_org_structure_txt = el_rest_full

                # version 1: -
                ## If it’s not present, they just return the original string unchanged: # No exception will ever be thrown if the prefix or suffix isn’t there—el_org_structure will just equal rest.
                ## org_structure = org_structure_full_txt.removeprefix("This is a ").removesuffix(" library.").strip()
                ## org_structure = org_structure.capitalize()

                # version 2: -
                org_structure = normalize_org(el_rest_full)

    except:
        print("err in org_struct. :\n", traceback.format_exc())
        org_structure = ""

    # Table Section 1 (Statistics Public):    # div table th[style = 'text-align: center']
    service_population = ""
    collection_size = ""
    annual_circulation = ""
    try:
        for tbl in el_outer_div.select('div table'):
            th = tbl.find('th', attrs={'style': 'text-align: center'})
            if th and th.get_text(strip=True) == 'Statistics Public':
                all_tds = tbl.find_all('td')
                try:
                    el_service_population = all_tds[0]
                    service_population_str = el_service_population.text.strip()
                    service_population = f"{service_population_str} residents"
                except:
                    pass
                try:
                    el_collection_size = all_tds[1]
                    collection_size_str = el_collection_size.text.strip()
                    collection_size = f"{collection_size_str} volumes"
                except:
                    pass
                try:
                    el_annual_circulation = all_tds[2]
                    annual_circulation_str = el_annual_circulation.text.strip()
                    annual_circulation = f"{annual_circulation_str} transactions"
                except:
                    pass
    except:
        pass

    """
    # street_addrs
    # mailing_addrs
    # city
    # state name [already have]
    # zip_code
    # county

    # phone_num
    # library_own_website
    # online_catalog

    # library_type
    # parent_org

    # permalink

    # director_name
    # org_structure

    # service_population -"residents"
    # collection_size -"volumes"
    # annual_circulation -"transactions"

    # current_automation_sys
    # previous_automation_sys
    # consortium_membership

    # libraries_org_id
    # oclc_symbol
    # worldcat_registry_id
    # nces_fscs_key
    # nces_libid


    # created_on
    # last_mod
    """

    # Table Section 2 (Technology Profile):    # div table th[style = 'text-align: center']
    current_automation_sys = ""
    previous_automation_sys = ""
    consortium_membership = ""

    temp_prev_list = []
    try:
        for tbl in el_outer_div.select('div table'):
            th = tbl.find('th', attrs={'style': 'text-align: center'})
            if th and th.get_text(strip=True) == 'Technology Profile':
                all_trs = tbl.find_all('tr')[2:]
                # print(f"technology table has {len(all_trs)} tbl rows")  # technology table has 3 tbl rows
                try:
                    for tr in all_trs:
                        idx0_th_name = tr.select_one("th")
                        if idx0_th_name and idx0_th_name.get_text(strip=True) == 'Current Automation System':
                            # el_cur_aut_sys_name = idx0_th_name.next_sibling
                            el_cur_aut_sys_name = idx0_th_name.find_next_sibling("td")
                            el_cur_aut_sys_year = el_cur_aut_sys_name.find_next_sibling("td")

                            el_cur_aut_sys_name_str = el_cur_aut_sys_name.get_text(strip=True)
                            el_cur_aut_sys_year_str = el_cur_aut_sys_year.text.strip()
                            if el_cur_aut_sys_year_str:
                                current_automation_sys = f"{el_cur_aut_sys_name_str} ({el_cur_aut_sys_year_str})"
                            else:
                                current_automation_sys = f"{el_cur_aut_sys_name_str}"

                        elif idx0_th_name and idx0_th_name.get_text(strip=True) == 'Previous Automation System':
                            # just need to make a list and save them from here!
                            el_prev_aut_sys_name = idx0_th_name.find_next_sibling("td")
                            el_prev_aut_sys_year = el_prev_aut_sys_name.find_next_sibling("td")

                            el_prev_aut_sys_name_str = el_prev_aut_sys_name.get_text(strip=True)
                            el_prev_aut_sys_year_str = el_prev_aut_sys_year.get_text(strip=True)

                            if el_prev_aut_sys_year_str:
                                previous_automation_sys = f"{el_prev_aut_sys_name_str} (until {el_prev_aut_sys_year_str})"
                            else:
                                previous_automation_sys = f"{el_prev_aut_sys_name_str}"

                            # Assigning to the list:
                            temp_prev_list.append(previous_automation_sys)

                        elif not idx0_th_name:
                            consortium_membership = tr.select_one("td a").text.strip()
                except:
                    print(f"Table2 full Error det (maybe an extra tr triggerd!): {url}\n {traceback.format_exc()}")
    except Exception as e:
        print(f"err of current+prev+consortium: {e}")
    # Adding back as a string:
    previous_automation_sys = ", ".join(temp_prev_list)

    # Table Section 3 (Identifiers):    # div table th[style = 'text-align: center']
    libraries_org_id = ""
    oclc_symbol = ""
    worldcat_registry_id = ""
    nces_fscs_key = ""
    nces_libid = ""

    try:
        for tbl in el_outer_div.select('div table'):
            th = tbl.find('th', attrs={'style': 'text-align: center'})
            if th and th.get_text(strip=True) == 'Identifiers':
                all_trs = tbl.find_all('tr')[1:]
                # print(f"Identifiers table has {len(all_trs)} tbl rows") # Identifiers table has 5 tbl rows
                try:
                    for tr in all_trs:
                        idx0_th_name = tr.select_one("th")
                        if idx0_th_name and idx0_th_name.get_text(strip=True) == 'libraries.org ID':
                            el_libraries_org_id = idx0_th_name.find_next_sibling("td")
                            libraries_org_id = el_libraries_org_id.get_text(strip=True)
                        elif idx0_th_name and 'OCLC' in idx0_th_name.get_text(strip=True):
                            el_oclc_symbol = idx0_th_name.find_next_sibling("td")
                            oclc_symbol = el_oclc_symbol.get_text(strip=True)
                        elif idx0_th_name and idx0_th_name.get_text(strip=True) == 'WorldCat Registry ID':
                            el_worldcat_registry_id = idx0_th_name.find_next_sibling("td")
                            worldcat_registry_id = el_worldcat_registry_id.get_text(strip=True)
                        elif idx0_th_name and idx0_th_name.get_text(strip=True) == 'NCES FSCSKEY':
                            el_nces_fscs_key = idx0_th_name.find_next_sibling("td")
                            nces_fscs_key = el_nces_fscs_key.get_text(strip=True)
                        elif idx0_th_name and idx0_th_name.get_text(strip=True) == 'NCES LIBID':
                            el_nces_libid = idx0_th_name.find_next_sibling("td")
                            nces_libid = el_nces_libid.get_text(strip=True)
                except:
                    print("Table3 Identifiers table full Error det:\n", traceback.format_exc())
    except Exception as e:
        print(f"err of lib+OCLC+worldCat+nfKey+n_libid: {e}")

    # Conclusion Section:   # div p span.detailheader
    # --------------------
    record_history_full_txt = ""
    created_on = ""
    last_mod = ""
    try:
        el_record_history_p = el_outer_div.select("div p")
        for p in el_record_history_p:
            span = p.select_one("span.detailheader")
            if span and span.get_text(strip=True) == "Record History:":
                el_rest_full = span.next_sibling
                record_history_full_txt = el_rest_full.get_text(strip=True)

                # Pattern to match dates like "Oct 6, 2005"
                # "This listing was created on Oct 6, 2005 and was last modified on Nov 22, 2024."
                pattern = r'([A-Z][a-z]{2}) (\d{1,2}), (\d{4})'

                matches = re.findall(pattern, record_history_full_txt)  # Find all date matches

                # Convert to full month names
                created_on = datetime.datetime.strptime(' '.join(matches[0]), '%b %d %Y').strftime(
                    '%B %d, %Y')  # October 06, 2005
                last_mod = datetime.datetime.strptime(' '.join(matches[1]), '%b %d %Y').strftime(
                    '%B %d, %Y')  # November 22, 2024
    except:
        print("err in conclusion (record section). :\n", traceback.format_exc())
        pass

    # Assigning to Dictonary:
    a_library_dict['street_addrs'] = street_addrs
    a_library_dict['mailing_addrs'] = mailing_addrs
    a_library_dict['city'] = city
    a_library_dict['state_name'] = state_name
    a_library_dict['zip_code'] = zip_code
    a_library_dict['country'] = country
    a_library_dict['county'] = county
    a_library_dict['phone_num'] = phone_num
    a_library_dict['library_own_website'] = library_own_website
    a_library_dict['online_catalog'] = online_catalog
    a_library_dict['full_details_txt'] = full_details_txt
    a_library_dict['library_type'] = library_type
    a_library_dict['parent_org'] = parent_org
    a_library_dict['permalink'] = permalink
    a_library_dict['director_name'] = director_name
    a_library_dict['org_structure'] = org_structure
    a_library_dict['service_population'] = service_population
    a_library_dict['collection_size'] = collection_size
    a_library_dict['annual_circulation'] = annual_circulation
    a_library_dict['current_automation_sys'] = current_automation_sys
    a_library_dict['previous_automation_sys'] = previous_automation_sys
    a_library_dict['consortium_membership'] = consortium_membership

    a_library_dict['libraries_org_id'] = libraries_org_id
    a_library_dict['oclc_symbol'] = oclc_symbol
    a_library_dict['worldcat_registry_id'] = worldcat_registry_id
    a_library_dict['nces_fscs_key'] = nces_fscs_key
    a_library_dict['nces_libid'] = nces_libid

    a_library_dict['created_on'] = created_on
    a_library_dict['last_mod'] = last_mod
    a_library_dict['record_history_full_txt'] = record_history_full_txt
    a_library_dict['full_org_structure_txt'] = full_org_structure_txt

    print("Exiting Function...")
    return a_library_dict


def scrape(qu_read, qu_write, st_Token, proxy_in_use):
    global glb_proxy
    glb_proxy = {"http": "http://" + proxy_in_use,
                 "https": "http://" + proxy_in_use}

    # disable when working with Selenium!
    proxy_in_use = {"http": "http://" + str(proxy_in_use).strip(),
                    "https": "http://" + str(proxy_in_use).strip()
                    }
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
            if arr_in == st_Token:

                try:
                    driver.close()
                    driver.quit()
                except:
                    pass
                qu_read.task_done()
                break


        murl = arr_in.split("|")[3]
        err_ctr = 0
        while True:
            print("\nProcessing url: " + murl)
            try:
                time.sleep(random.uniform(1.2, 2.5))
                #__________________BS__________________

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

                result_dict = parse_profile(soup, murl)

                # Saving Results:------
                arr_out = initiate_results_array()
                arr_out[0] = arr_in.split("|")[2]   #Library Name
                arr_out[1] = result_dict.get('library_type')
                arr_out[2] = result_dict.get('parent_org')
                arr_out[3] = result_dict.get('permalink')
                arr_out[4] = result_dict.get('street_addrs')
                arr_out[5] = result_dict.get('mailing_addrs')
                arr_out[6] = result_dict.get('city')
                arr_out[7] = result_dict.get('state_name')
                arr_out[8] = result_dict.get('zip_code')
                arr_out[9] = result_dict.get('county')
                arr_out[10] = result_dict.get('phone_num')
                arr_out[11] = result_dict.get('library_own_website')
                arr_out[12] = result_dict.get('online_catalog')
                arr_out[13] = result_dict.get('director_name')
                arr_out[14] = result_dict.get('org_structure')
                arr_out[15] = result_dict.get('service_population')
                arr_out[16] = result_dict.get('collection_size')
                arr_out[17] = result_dict.get('annual_circulation')
                arr_out[18] = result_dict.get('current_automation_sys')
                arr_out[19] = result_dict.get('previous_automation_sys')
                arr_out[20] = result_dict.get('consortium_membership')

                arr_out[21] = result_dict.get('oclc_symbol')
                arr_out[22] = result_dict.get('worldcat_registry_id')
                arr_out[23] = result_dict.get('nces_fscs_key')
                arr_out[24] = result_dict.get('nces_libid')
                arr_out[25] = result_dict.get('libraries_org_id')
                arr_out[26] = result_dict.get('created_on')
                arr_out[27] = result_dict.get('last_mod')

                # Extra columns:
                arr_out[28] = ""    # Just a gap
                arr_out[29] = arr_in.split("|")[0]  # Master State Link
                arr_out[30] = arr_in.split("|")[1]  # State Name (again)
                arr_out[31] = arr_in.split("|")[3]  # lib_link (again? parmalink?)
                arr_out[32] = result_dict.get('country')
                arr_out[33] = result_dict.get('full_details_txt')
                arr_out[34] = result_dict.get('record_history_full_txt')
                arr_out[35] = result_dict.get('full_org_structure_txt')


                #result printout:
                print(f"____________________\n{arr_out}\n____________________")

                # Writer:
                qu_write.put(arr_out)
                break

            except Exception as e:
                err_ctr += 1
                print("Trying again...")
                if err_ctr > 2:
                    mlog.error(f"ERR IS :{str(e)}. ---> URL WAS: {murl}")
                    print(f"\nFull error details after 2 retry: {traceback.format_exc()}")

                    arr_out = initiate_results_array()
                    arr_out[0] = arr_in.split("|")[0]  # Master State Link
                    arr_out[1] = arr_in.split("|")[1]  # State Name
                    arr_out[2] = arr_in.split("|")[2]  # Library Name
                    arr_out[3] = arr_in.split("|")[3]  # Library link
                    arr_out[err_col_index] = "[ERROR]"

                    # Writer:
                    qu_write.put(arr_out)
                    mlog.warning("Aborting a URL after 2 retries")
                    break
                else:
                    print("the error before trying again:\n",e)
                    print(f"ctr:{err_ctr} Trying again... {murl}")

        print("\n/////////////////// Done one row ////////////////////\n==================================================================")
        qu_read.task_done()



if __name__ == "__main__":

    num_of_processes = num_of_processes_in_data
    rows_in_a_batch = num_of_processes * 3

    print("Program starts now at: " + time.ctime())

    # waitIfCountryIsBD(driver)

    source_file_full_name = folder_for_all_files + era_data_source_filename
    output_file_full_name = folder_for_all_files + era_data_output_filename
    output_file_full_name_error = folder_for_all_files + "error_" + era_data_output_filename

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

    # The processes are now ready and running. They shall start working as soon as
    # Data are being put into the q_input

    # Now we read to get data from the source-text file and
    # put them inside the Input Queue
    # Work Starts as soon as q_input starts to populate

    with open(source_file_full_name, newline='', encoding='utf-8') as f:
        csv_f = csv.reader(f, delimiter=',', quotechar='"')

        for row in csv_f:
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
            mlog.warning("All worker processes died now. Shall proceed to stop the writer. ")
            break
        else:
            time.sleep(5)
            mlog.warning("Atleast One Queue is running. Sent stop token to processing quues aready!")

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