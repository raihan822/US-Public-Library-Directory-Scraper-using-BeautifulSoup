##########Following are LOGGING related sttings
import sys
import logging
root = logging.getLogger()
mlog = logging.getLogger(__name__)
##################
def loggerSetup(level_indicator):
    root.setLevel(level_indicator)

    if root.hasHandlers():
        root.handlers = []
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level_indicator)
    formatter = logging.Formatter('%(asctime)s %(levelname)s || %(message)s || %(name)s || %(lineno)s',
                                  '%A %Y-%m-%d %H:%M:%S %Z')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    mlog = logging.getLogger(__name__)
##################

#>>>Set the following Values Before you run :
data_folder_name = "csv_data"

#Era: Links Scrape
# era_links_source_filename = "link_initial_csv.csv"
era_links_source_filename = "source_error_link_out.csv"
era_links_output_filename = "link_out.csv"

#Era: Data Scrape
# era_data_source_filename = "link_out_1.csv"
era_data_source_filename = "error_data_out.csv"
# era_data_source_filename = "test_data_now.csv"
era_data_output_filename = "data_out.csv"

#Era: Image
era_image_source_filename = "link_out_1.csv"
era_image_output_filename = "image_out.csv"


err_col_index = 30
new_output_after_row = 300000


#No need to change num_of_columns_in_output_file unless absolutely necessary.
#Increase this number only when more than 100 columns is required in the output file.
num_of_columns_in_output_file = 40
driver_page_load_timeout = 60 #Increase time for Selenium
driver_implicit_wait = 0 # Please keep this 0 all the time.


#>>>How many processes do you want to run in parallel?
num_of_processes_in_links = 1
num_of_processes_in_data = 1
num_of_processes_in_image = 1 #img downloading

#use_proxies_from must be any one of the 4:
#Note:-  'storm_rot_15', 'storm_rot_3', 'storm_rot_rand', 'mpp_plain'
# use_proxies_from = 'storm_rot_rand'
# use_proxies_from = 'storm_rot_15'   # highest 8 threads
use_proxies_from = 'storm_rot_3'  # highest 32 threads
# use_proxies_from = 'mpp_plain'    # unlimited


##################
level_indicator = logging.INFO

loggerSetup(level_indicator)
