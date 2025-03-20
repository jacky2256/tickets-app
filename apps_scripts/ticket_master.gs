const API_KEY = 'api_key';
BASE_URL = 'http://your_ip';
const STATUS_CELL = 'J1';

const ARTIST_NAME_CELL = 'G1';
const KEYWORD = getArtistName();
const COUNTRY_LIST = ['US', 'CA'];
const SIZE = 100;

const SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID'; 
const SHEET_NAME = 'Sales Data';

const START_NUM_CELL = 5;

const EVENT_DATE_CELL = 'A';  
const EVENT_PRESALE_START_DATE_CELL = 'B';
const EVENT_PRESALE_START_TIME_CELL = 'C';
const EVENT_PRESALE_TYPE_CELL = 'D';
const CITY_CELL = 'E';
const STATE_CELL = 'F';
const VENUE_CELL = 'G';
const TOTAL_CAPACITY_CELL = 'H';
const MIN_PRICE_VIVID_CELL = 'I'
const MIN_PRICE_TICKET_NETWORK_CELL = 'J'
const TOTAL_MIN_COST_CELL = 'K';
const TOTAL_MAX_COST_CELL = 'L';

let FILTER_WILL_PRESALE = true;

function getSheet() {
    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = spreadsheet.getSheetByName(SHEET_NAME);
    
    if (!sheet) {
        throw new Error(`Sheet with name "${SHEET_NAME}" not found.`);
    }
    return sheet;
}

function clearGoogleSheetData() {
    const sheet = getSheet();
    const lastRow = sheet.getLastRow();

    if (lastRow < START_NUM_CELL) {
        Logger.log("No data to clear.");
        return;
    }

    Logger.log(`Clearing data from row ${START_NUM_CELL} to ${lastRow}...`);

    const range = sheet.getRange(`${EVENT_DATE_CELL}${START_NUM_CELL}:${TOTAL_MAX_COST_CELL}${lastRow}`);
    range.clearContent();

    Logger.log("Data cleared successfully!");
}

function saveTicketMasterToGoogleSheet(events) {
    if (events.length === 0) {
        Logger.log("No events to save.");
        return;
    }

    const sheet = getSheet();
    Logger.log(`Saving ${events.length} events to Google Sheet...`);

    let row = START_NUM_CELL; 

    events.forEach(event => {
        sheet.getRange(`${EVENT_DATE_CELL}${row}`).setValue(event.eventDateTime);
        sheet.getRange(`${EVENT_PRESALE_START_DATE_CELL}${row}`).setValue(event.presaleStartDate);
        sheet.getRange(`${EVENT_PRESALE_START_TIME_CELL}${row}`).setValue(event.presaleStartTime);
        sheet.getRange(`${EVENT_PRESALE_TYPE_CELL}${row}`).setValue(event.presaleType);
        sheet.getRange(`${CITY_CELL}${row}`).setValue(event.city);
        sheet.getRange(`${STATE_CELL}${row}`).setValue(event.state);
        sheet.getRange(`${VENUE_CELL}${row}`).setValue(event.venueName);
        sheet.getRange(`${TOTAL_CAPACITY_CELL}${row}`).setValue("N/A");
        sheet.getRange(`${MIN_PRICE_VIVID_CELL}${row}`).setValue("N/A");
        sheet.getRange(`${MIN_PRICE_TICKET_NETWORK_CELL}${row}`).setValue("N/A");
        sheet.getRange(`${TOTAL_MIN_COST_CELL}${row}`).setValue(event.priceMin);
        sheet.getRange(`${TOTAL_MAX_COST_CELL}${row}`).setValue(event.priceMax);

        row++;
    });

    Logger.log("Events saved successfully!");
}

function fetchEvents() {
    const apiKey = API_KEY;
    const keyword = KEYWORD;
    const countries = COUNTRY_LIST;
    const size = SIZE;
    const onsaleStartDateTime = getTodayISODate();
    const baseUrl = 'https://app.ticketmaster.com/discovery/v2/events.json';

    let allEvents = [];
    
    if (!keyword || keyword.trim() === '') {
        Logger.log("Keyword is empty. Exiting function.");
        return;
    }

    for (let country of countries) {
        let events = [];
        let page = 0;
        let totalPages = 1;

        while (page < totalPages) {
            const url = `${baseUrl}?size=${size}&apikey=${apiKey}&keyword=${keyword}&countryCode=${country}&page=${page}&onsaleStartDateTime=${encodeURIComponent(onsaleStartDateTime)}`;
            Logger.log(`Fetching URL: ${url}`);

            try {
                const response = UrlFetchApp.fetch(url, { method: 'get' });
                const data = JSON.parse(response.getContentText());

                if (!data || !data.page) {
                    Logger.log(`No data received for ${country}. Skipping.`);
                    break;
                }

                if (page === 0) {
                    totalPages = data.page.totalPages;
                    Logger.log(`Country: ${country}, Total events: ${data.page.totalElements}, Total pages: ${totalPages}`);
                }

                const pageEvents = extractInfoEvents(data);
                events = events.concat(pageEvents);

            } catch (error) {
                Logger.log(`Error fetching page ${page} for ${country}: ${error.message}`);
                break;
            }
            page++;
            Utilities.sleep(1000);
        }

        allEvents = allEvents.concat(events);
    }

    printResults(allEvents);
    saveTicketMasterToGoogleSheet(allEvents);
}

function getTodayISODate() {
    const now = new Date();
    return now.toISOString().split('.')[0] + "Z";
}

function extractInfoEvents(data) {
    if (!data._embedded?.events) {
        Logger.log("No events found.");
        return [];
    }

    let extractedEvents = [];
    data._embedded.events.forEach(event => {
        const is_presale = !!event.sales?.presales?.[0];
        if (!is_presale) return;
        
        if (FILTER_WILL_PRESALE) {
          const isPresaleDateValidFlag  = isPresaleDateValid(event.sales?.presales?.[0]?.startDateTime);
          if (!isPresaleDateValidFlag) return;
        }

        const { date: presaleStartDate, time: presaleStartTime } = splitDateTime(event.sales?.presales?.[0]?.startDateTime);
        const { date: presaleEndDate, time: presaleEndTime } = splitDateTime(event.sales?.presales?.[0]?.endDateTime);

        let eventData = {
            eventName: event.name,
            eventDateTime: formatEventDate(event.dates?.start?.dateTime),
            presaleType: event.sales?.presales?.[0]?.name || "No presale",
            presaleStartDate: presaleStartDate, 
            presaleStartTime: presaleStartTime, 
            presaleEndDate: presaleEndDate,
            presaleEndTime: presaleEndTime,
            priceMin: event.priceRanges?.[0]?.min || "Unknown",
            priceMax: event.priceRanges?.[0]?.max || "Unknown",
            city: event._embedded?.venues?.[0]?.city?.name || "Unknown",
            state: event._embedded?.venues?.[0]?.state?.name || "Unknown",
            country: event._embedded?.venues?.[0]?.country?.name || "Unknown",
            venueName: event._embedded?.venues?.[0]?.name || "Unknown"
        };

        extractedEvents.push(eventData);
    });

    return extractedEvents;
}

function isPresaleDateValid(presaleDate) {
            if (!presaleDate) {
                return false;
            }

            const presaleTime = new Date(presaleDate).getTime();
            const now = new Date().getTime();
            const flag = presaleTime >= now;
            Logger.log(`Input - ${presaleDate} - ${presaleTime} - Now - ${now} - ${flag}`);
            return flag;
        }

function formatEventDate(isoDate) {
    if (!isoDate) return "Unknown";

    const date = new Date(isoDate);

    const daysOfWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const dayOfWeek = daysOfWeek[date.getUTCDay()]; 
    const month = date.getUTCMonth() + 1;
    const day = date.getUTCDate();
    const year = date.getUTCFullYear();

    return `${dayOfWeek} ${month}-${day}-${year}`;
}

function splitDateTime(isoDateTime) {
    if (!isoDateTime) return { date: "N/A", time: "N/A" };

    const dateObj = new Date(isoDateTime);

    const date = dateObj.toISOString().split("T")[0];

    const hours = dateObj.getUTCHours();
    const minutes = String(dateObj.getUTCMinutes()).padStart(2, "0");
    const seconds = String(dateObj.getUTCSeconds()).padStart(2, "0");
    const period = hours >= 12 ? "PM" : "AM";
    const formattedHours = hours % 12 || 12; 

    const time = `${formattedHours}:${minutes}:${seconds} ${period}`;

    return { date, time };
}

function printResults(events) {
    Logger.log("\n========================= RESULTS =========================");
    if (events.length === 0) {
        Logger.log("No events found.");
        return;
    }

    Logger.log(`Total events: ${events.length}\n`);
    events.forEach((event, index) => {
        Logger.log(`Event ${index + 1}: ${event.eventName}`);
        Logger.log(`Date: ${event.eventDateTime}`);
        Logger.log(`Venue: ${event.venueName}, ${event.city}, ${event.state}, ${event.country}`);
        Logger.log(`Price Range: $${event.priceMin} - $${event.priceMax}`);
        Logger.log(`Presale: ${event.presaleType} (Start: ${event.presaleStartDate}, End: ${event.presaleStartTime})`);
        Logger.log("---------------------------------------------------------");
    });
}

function getArtistName() {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    const artistName = sheet.getRange(ARTIST_NAME_CELL).getValue();
    const value = artistName ? artistName.toString().trim() : "";
    return value;
}

function start_ticket_network_filter() {
    clearGoogleSheetData();
    fetchEvents();
}

function start_ticket_network() {
  FILTER_WILL_PRESALE = false;
  clearGoogleSheetData();
  fetchEvents();
}
