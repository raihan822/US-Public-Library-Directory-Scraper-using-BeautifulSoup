````markdown
# 📚 US Public Library Directory Scraper – LibraryTechnology.org

This project is a Python-based web scraper that extracts detailed information about public libraries in the United States from [LibraryTechnology.org](https://librarytechnology.org/libraries/uspublic/). Built using **BeautifulSoup**, it collects, cleans, and structures the data into a CSV file or optionally uploads it to a Google Sheet.

## 🔍 Features

- Scrapes all library listings from the directory
- Extracts the following fields:
  - **Library Name**
  - **Website URL**
  - **Root Domain**
  - **City**
  - **State (2-letter abbreviation)**
  - **Zip Code** (if available)
  - **Phone Number**
  - **Library Type** (e.g., Public, County, Regional)
  - **Library System** (if applicable)
- Outputs the data into a structured CSV file
- Google Sheets integration (optional)

## 🛠️ Technologies Used

- Python 3
- BeautifulSoup (bs4)
- Requests
- Pandas
- (Optional) gspread & Google Sheets API

## 📁 Output

- `us_public_libraries.csv` — structured file containing all scraped library data.
- (Optional) Google Sheet output if enabled.

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/raihan822/US-Public-Library-Directory-Scraper-using-BeautifulSoup.git
cd US-Public-Library-Directory-Scraper-using-BeautifulSoup
````

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Scraper

```bash
python scraper.py
```

You’ll find the output file `us_public_libraries.csv` in your working directory.

## ✅ Optional: Export to Google Sheets

To export results to Google Sheets:

* Set up the [Google Sheets API](https://developers.google.com/sheets/api/quickstart/python)
* Enable and configure your `credentials.json`
* Modify the script to push data to your chosen spreadsheet

---

## 📌 Source

Data sourced from: [https://librarytechnology.org/libraries/uspublic/](https://librarytechnology.org/libraries/uspublic/)

## 📄 License

This project is licensed under the MIT License.

---

⭐ Star this repo if you found it useful!

```
