# >>>"https://www.zillow.com/homes/for_rent/2_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A2%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-119.19130123730463%2C%22east%22%3A-117.58455074902338%2C%22south%22%3A33.44635227517352%2C%22north%22%3A34.30148490405707%7D%2C%22customRegionId%22%3A%228364767eb8X1-CRovfszra4pyjg_verfo%22%2C%22savedSearchEnrollmentId%22%3A%22X1-SSlsfgw658bc9i0000000000_540h4%22%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22mostrecentchange%22%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D
# property details,
# rental prices,
# and contact information

from constants import data_folder_name
import csv
def write_data_to_csv(csv_name, src_list):
    csv.register_dialect(
        'mydialect',
        delimiter=',',
        quotechar='"',
        doublequote=True,
        skipinitialspace=True,
        lineterminator='\r\n',
        quoting=csv.QUOTE_MINIMAL)

    with open(f"{data_folder_name}/{csv_name}", 'w', newline='', encoding='utf-8') as mycsv:
        dat_writer = csv.writer(mycsv, dialect='mydialect')
        for a in src_list:
            if isinstance(a, str):
                mlst = []
                mlst.append(a)
                dat_writer.writerow(mlst)
            else:
                dat_writer.writerow(a)

    return csv_name


states = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "District of Columbia",
    "Delaware",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Puerto Rico",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming"
]

print(len(states))  # Outputs: 52


# if Multiple pages page to scrape:- #design your page links here:
initial_csv = []
for stateName in states:
    # https://librarytechnology.org/libraries/public.pl?State=New%20Jersey
    # https://librarytechnology.org/libraries/public.pl?State=Alabama
    url = f"https://librarytechnology.org/libraries/public.pl?State={stateName.replace(" ","%20")}"
    initial_csv.append(url)

print(f"len in csv: {len(initial_csv)}")
for i in initial_csv:
    print(i)


# if One single page to scrape:-
# url = ["https://auspost.com.au/mypost/track/search"]

# Make changes here:
write_data_to_csv(csv_name="link_initial_csv.csv",src_list= initial_csv)