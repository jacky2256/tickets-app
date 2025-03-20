# Tickets App

This application fetches event and ticket data from multiple sources (Ticket Master, Vivid Seats, Ticket Network) and processes it. It can be run using Docker, integrated with Google Sheets via Apps Script, or executed manually using Python.

## Table of Contents

- [Installation](#installation)
- [Running via Docker](#running-via-docker)
- [Google Sheets Integration](#google-sheets-integration)
- [Manual Execution](#manual-execution)
- [Configuration](#configuration)
- [Notes](#notes)

## Installation

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   ```

2. **Running via Docker**
    start te containers:
    ```bash
   docker compose up -d
   ```
   monitoring the logs:
     ```bash
    docker logs -f api
   ```
   ```bash
    docker logs -f redis
   ```
   ```bash
    docker logs -f nginx
   ```

## Google Sheets Integration
In the `apps_scripts` folder, you will find two files:

`ticket_master.gs` – for interacting with the Ticket Master website.
`vivid_ticket_net.gs` – for interacting with Vivid Seats and Ticket Network.

### Steps to Set Up:
1. Add Apps Script Files:
    * Import both `.gs` files into your Google Apps Script project.
2. Create Buttons in Google Sheets:
    * Create buttons and attach the following functions to them:
        * `start_ticket_network_filter()` – Fetches presale venue data from Ticket Master.
        * `start_ticket_network()` – Fetches venue data from Ticket Master. 
        * `clearGoogleSheetData()` – Clears data from the Google Sheet. 
        * `start_city_vivid_ticket_net()` – Sends a request with cities and the artist name to the server for Vivid and Ticket Network parsing. 
        * `start_venue_vivid_ticket_net()` – Sends a request with venue names and the artist name to the server for Vivid and Ticket Network parsing. 
        * `check_vivid_ticket_net_status()` – Checks the parsing status (returns Processing if running and Completed when finished). 
        * `get_data_vivid_ticket_net()` – Retrieves parsed data from the server and populates the fields with the minimum prices from Vivid and Ticket Network.

## How to Use:
1. #### Step 1:
    Click either `start_ticket_network` or `start_ticket_network_filter`. The Ticket Master data will be fetched and written into the sheet automatically (approximately 4–8 seconds).

2. ### Step 2:
    Click either `start_city_vivid_ticket_net` or `start_venue_vivid_ticket_net` (takes about 2–3 seconds).

3. ### Step 3:
    Manually click `check_vivid_ticket_net_status` to verify the parsing status.

    * If the status shows __Processing__, wait and click again.
    * The parsing time depends on the number of records sent to the server, averaging about 15 seconds per record.
4. ### Step 4:
    * Once the status is __Completed__, click `get_data_vivid_ticket_net`. The data, including the minimum prices from both Vivid and Ticket Network, will be populated in your Google Sheet.

**! Note**: Due to Google Sheets’ execution time limits (scripts cannot run longer than 6 minutes), you must manually check the status. Parsing may take more than 20 minutes, depending on the volume of data.


## Manual Execution
If you cannot run the server locally (for example, if your ISP blocks inbound connections), you can run the script manually:

1. **Prepare the Input CSV**:

    * Create a file at data/in/base.csv with the necessary columns.
    * Important:
      * The header for the city/state/venue or other tiles column must be named `Keyword`. 
      * List the city/states/venue or other titles in a single column. 
      * Next to it, include a column named `artist` with the artist’s name.
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```
3. **Activate the virtual environment:**
   * Linux/Mac:
   
   
      ```bash
      source venv/bin/activate
      ```
   * Windows:

      ```bash
      venv\Scripts\activate
      ```
4. **Install the required dependencies:**
    ```bash
      pip install -r requirements.txt
      ```
   
5. **Run the Application:**
    ```bash
   python main.py
   ```
6. **Review the Output:**
    * After parsing completes, the results will be available in d`ata/out/output.csv`.

## Configuration
### Google Sheets Variables
The variables for Google Sheets are configured in the `ticket_master.gs` file. Example configuration:
```bash
const API_KEY = 'h9wsOp0TdyJ0GbXpUaBY6LKH3x33OKWj';  // API key from Ticket Master
const BASE_URL = 'http://135.181.158.178';             // Server IP address for Vivid and Ticket Network parsing
const STATUS_CELL = 'J1';                             // Cell to display the parsing status
const ARTIST_NAME_CELL = 'G1';                        // Cell to input the artist name
const COUNTRY_LIST = ['US', 'CA'];                    // Countries to search on Ticket Master
const SIZE = 100;                                   // Maximum records to fetch per request from Ticket Network (max 100)
const SHEET_NAME = 'Sales Data';                      // Sheet name where data will be populated
const START_NUM_CELL = 5;                             // Starting row for data entry

// Column settings:
const EVENT_DATE_CELL = 'A';                          // Event date
const EVENT_PRESALE_START_DATE_CELL = 'B';            // Presale date
const EVENT_PRESALE_START_TIME_CELL = 'C';            // Presale time
const EVENT_PRESALE_TYPE_CELL = 'D';                  // Presale type
const CITY_CELL = 'E';                                // City
const STATE_CELL = 'F';                               // State
const VENUE_CELL = 'G';                               // Venue
const TOTAL_CAPACITY_CELL = 'H';                      // Venue capacity
const MIN_PRICE_VIVID_CELL = 'I';                     // Minimum price from Vivid Seats
const MIN_PRICE_TICKET_NETWORK_CELL = 'J';            // Minimum price from Ticket Network
const TOTAL_MIN_COST_CELL = 'K';                      // Minimum total cost
const TOTAL_MAX_COST_CELL = 'L';                      // Maximum total cost
```

### Application Settings (tickets-app)
Configure the following variables in your application as needed:
* USE_PROXY = False

    Use a proxy or not (proxies are listed in data/in/proxies.txt).

* THREADS = 2

    Number of drivers to run concurrently (it is recommended not to use more than 5).

## Notes
* __Logs__:

    Monitor Docker container logs using docker logs -f <container-name> for real-time feedback.

* __Google Sheets Limitations__:

    Since Google Sheets scripts cannot run for more than 6 minutes, you must manually check the parsing status using the provided functions.

* __Parsing Time__:

    The total parsing time depends on the number of records. On average, expect around 15 seconds per record.