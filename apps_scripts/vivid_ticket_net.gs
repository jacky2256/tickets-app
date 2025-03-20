function readVenueData() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
  var artist_name = sheet.getRange(ARTIST_NAME_CELL).getValue();
  Logger.log("Artist Name: " + artist_name);

  var keywords = [];
  var row = START_NUM_CELL;
  
  while (true) {
    var state = sheet.getRange(VENUE_CELL + row).getValue();
    
    if (!state) break;

    var keyword = {
      "id": row, 
      "name": state + " " + artist_name
    };
    keywords.push(keyword);
    
    row++;
  }

  var payload = {
    "keywords": keywords
  };

  Logger.log("Generated Payload: " + JSON.stringify(payload));
  return payload;
}

function readSityData() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
  var artist_name = sheet.getRange(ARTIST_NAME_CELL).getValue();
  Logger.log("Artist Name: " + artist_name);

  var keywords = [];
  var row = START_NUM_CELL;
  
  while (true) {
    var state = sheet.getRange(STATE_CELL + row).getValue();
    
    if (!state) break;

    var keyword = {
      "id": row, 
      "name": state + " " + artist_name
    };
    keywords.push(keyword);
    
    row++;
  }

  var payload = {
    "keywords": keywords
  };

  Logger.log("Generated Payload: " + JSON.stringify(payload));
  return payload;
}

function fetch_start(payload) {
  var apiUrl = BASE_URL + "/start";

  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload)
  };

  var response = UrlFetchApp.fetch(apiUrl, options);
  Logger.log("Start Response: " + response.getContentText());

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.getRange(STATUS_CELL).setValue("Processing");

  return response;
}


function start_city_vivid_ticket_net() {
  var payload = readSityData();
  fetch_start(payload);
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.getRange(STATUS_CELL).setValue('Processing');
}

function start_venue_vivid_ticket_net() {
  var payload = readVenueData();
  fetch_start(payload);
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.getRange(STATUS_CELL).setValue('Processing');
}


function check_vivid_ticket_net_status() {
  var statusUrl = BASE_URL + "/status";
  var response = UrlFetchApp.fetch(statusUrl);
  var statusData = JSON.parse(response.getContentText());

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var statusValue = statusData.status ? "Processing" : "Completed";

  sheet.getRange(STATUS_CELL).setValue(statusValue);
  Logger.log("Current Status: " + statusValue);
}


function get_data_vivid_ticket_net() {
  var dataUrl = BASE_URL + "/data";
  var response = UrlFetchApp.fetch(dataUrl);
  var data = JSON.parse(response.getContentText());

  Logger.log("Data Received: " + JSON.stringify(data));

  saveVividTicketNetToGoogleSheet(data.data.keywords);
}


function saveVividTicketNetToGoogleSheet(keywords) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  for (var i = 0; i < keywords.length; i++) {
    var row = START_NUM_CELL + i;
    
    sheet.getRange(MIN_PRICE_VIVID_CELL + row).setValue(keywords[i].min_price_vivid);
    sheet.getRange(MIN_PRICE_TICKET_NETWORK_CELL + row).setValue(keywords[i].min_price_ticket);
  }

  Logger.log("Data was saved in Google Sheet!");
}
