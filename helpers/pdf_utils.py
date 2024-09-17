import pdfplumber
import re
import os
import glob


# Define if ticket is regional or international
def is_international_ticket(text):
    # Search for international pattern (pattern 'Preis Hinfahrt: ' is unique to international tickets)
    match = re.search(r'(?<=Preis)\sHinfahrt:\s', text)
    if match:
        return True


# Define if ticket is round trip
def is_round_trip_ticket(text):
    # Search for "Hin- und Rückfahrt" pattern
    match = re.search(r'Hin- und Rückfahrt', text)
    if match:
        return True


# Extract origin and destination from parsed regional ticket
def get_origin_and_destination(text):
    # Search for "Hinfahrt: Origin ->Destination" pattern (including +City suffixes and regional suffixes like "Hinfahrt: Forchheim(Oberfr) München+City")
    match = re.search(r'Hinfahrt:\s([A-Za-zäöüÄÖÜß]+(?:\([A-Za-zäöüÄÖÜß]+\))?(\+City)?)\s([A-Za-zäöüÄÖÜß]+(\+City)?)', text)
    if match:

        extracted_text = match.group(0)

        start = extracted_text.split(' ')[1].replace("+City", "").strip()
        destination = extracted_text.split(' ')[2].replace("+City", "").strip()

        return start, destination


# Extract origin and destination from parsed international ticket
def get_origin_and_destination_intl(text):
    # Search for "VON ->NACH" pattern (including station suffixes)
    match = re.search(r'[A-ZÖÜÄ][a-zöüäß]+(\s\W)?\s->[A-ZÖÜÄ][a-zöüäß]+(\s\W)?', text)
    if match:

        extracted_text = match.group(0)

        start = extracted_text.split('->')[0].strip()
        destination = extracted_text.split('->')[1].strip()

        return start, destination


# Extract origin and destination from outward journey of round trip ticket
def get_origin_and_destination_outward(text):
    # Find match for "Hinfahrt Origin Destination" pattern that doesn't match "Hinfahrt Zangenabdruck Rückfahrt" pattern
    match = re.search(r'Hinfahrt\s([A-Za-zäöüÄÖÜß]+)\s([A-Za-zäöüÄÖÜß]+)(?!.*(Zangenabdruck|Rückfahrt))', text)
    if match:
        
        extracted_text = match.group(0)

        start = extracted_text.split(' ')[1]
        destination = extracted_text.split(' ')[2]

        return start, destination
    

# Extract origin and destination from return journey of round trip ticket
def get_origin_and_destination_return(text):
    # Find match for "Rückfahrt Origin Destination" pattern that doesn't match "Rückfahrt Firstname Lastname" pattern
    match = re.search(r'(?<!Zangenabdruck\s)Rückfahrt\s([A-Za-zäöüÄÖÜß]+)\s([A-Za-zäöüÄÖÜß]+)', text)
    if match:
        
        extracted_text = match.group(0)

        start = extracted_text.split(' ')[1]
        destination = extracted_text.split(' ')[2]

        return start, destination


def extract_origin_and_destination(text):
    if is_international_ticket(text):
        start, destination = get_origin_and_destination_intl(text)
    else:
        start, destination = get_origin_and_destination(text)
    return start, destination


def get_travel_date(text):
    # Search for "Gültig ab: DD.MM.YYYY" pattern
    match = re.search(r'Gültig ab:\s\d{2}.\d{2}.\d{4}', text)
    if match:

        date = match.group(0).split(' ')[2]

        return date


def get_travel_date_intl(text):
    # Search for "Gültigkeit: abDD.MM.YYYY" pattern
    match = re.search(r'Gültigkeit: ab\d{2}.\d{2}.\d{4}', text)
    if match:

        date = match.group(0).split('ab')[1]

        return date


def get_travel_date_outward(text):
    # Search for "Hinfahrt am DD.MM.YYYY" pattern
    match = re.search(r'Hinfahrt am \d{2}.\d{2}.\d{4}', text)
    if match:

        date = match.group(0).split(' ')[2]

        return date


def get_travel_date_return(text):
    # Search for "Rückfahrt am DD.MM.YYYY" pattern
    match = re.search(r'Rückfahrt am \d{2}.\d{2}.\d{4}', text)
    if match:

        date = match.group(0).split(' ')[2]

        return date


def extract_travel_date(text):
    if is_international_ticket(text):
        date = get_travel_date_intl(text)
    else:
        date = get_travel_date(text)
    return date


def get_booking_date(text):
    # Search for "erfolgte am DD.MM.YYYY" pattern
    match = re.search(r'erfolgte am \d{2}.\d{2}.\d{4}', text)
    if match:
            
        date = match.group(0).split(' ')[2]

        return date


def get_booking_date_round_trip(text):
    # Search for "Gebucht am DD.MM.YYYY" pattern
    match = re.search(r'Gebucht am \d{2}.\d{2}.\d{4}', text)
    if match:
                
        date = match.group(0).split(' ')[2]

        return date


def get_ticket_price(text):
    # Search for "Summe dd,dd€" pattern
    match = re.search(r'Summe\s\d+,\d{2}€', text)
    if match:
                
        price = match.group(0).split(' ')[1].strip('€').replace(',', '.')

        return float(price)


def get_ticket_price_round_trip(text):
    # Search for "Gesamtpreis dd,dd €" pattern
    match = re.search(r'Gesamtpreis\s\d+,\d{2}\s€', text)
    if match:
            
        price = match.group(0).split(' ')[1].strip('€').replace(',', '.')

        return float(price)


def get_ticket_number(text):
    # Search for "Auftragsnummer: alphanumeric" pattern
    match = re.search(r'Auftragsnummer:\s\w+', text)
    if match:

        number = match.group(0).split(' ')[1]

        return number


def get_passenger_count(text):
    # Search for "Erw: dd" pattern
    match = re.search(r'Erw:\s\d+', text)
    if match:

        count = match.group(0).split(' ')[1]

        return int(count)


def get_passenger_count_intl(text):
    # Search for "dd Erwachsene" pattern
    match = re.search(r'\d+\sErwachsene', text)
    if match:

        count = match.group(0).split(' ')[0]

        return int(count)



def get_passenger_count_round_trip(text):
    
    # Search for "Reisender dd Person" pattern
    match = re.search(r'Reisender\s\d+\sPerson', text)
    if match:
        count = match.group(0).split(' ')[1]

        return int(count)


def extract_passenger_count(text):
    if is_international_ticket(text):
        count = get_passenger_count_intl(text)
    else:
        count = get_passenger_count(text)
    return count


def extract_ticket_info(text):
    data = {}
    
    date = extract_travel_date(text)
    start, destination = extract_origin_and_destination(text)
    price = get_ticket_price(text)
    ticket_number = get_ticket_number(text)
    booking_date = get_booking_date(text)
    passenger_count = extract_passenger_count(text)

    data['Start'] = start
    data['Destination'] = destination
    data['Date'] = date
    data['Price'] = price
    data['Ticket Number'] = ticket_number
    data['Booking Date'] = booking_date
    data['Passenger Count'] = passenger_count

    return data

def extract_ticket_info_round_trip(text):
    data_outward = {}
    data_return = {}

    price_total = get_ticket_price_round_trip(text)
    ticket_number = get_ticket_number(text)
    booking_date = get_booking_date_round_trip(text)
    passenger_count = get_passenger_count_round_trip(text)

    start_outward, destination_outward = get_origin_and_destination_outward(text)
    date_outward = get_travel_date_outward(text)

    data_outward['Start'] = start_outward
    data_outward['Destination'] = destination_outward
    data_outward['Date'] = date_outward
    data_outward['Price'] = 0.00
    data_outward['Ticket Number'] = ticket_number
    data_outward['Booking Date'] = booking_date
    data_outward['Passenger Count'] = passenger_count

    start_return, destination_return = get_origin_and_destination_return(text)
    date_return = get_travel_date_return(text)

    data_return['Start'] = start_return
    data_return['Destination'] = destination_return
    data_return['Date'] = date_return
    data_return['Price'] = price_total
    data_return['Ticket Number'] = ticket_number
    data_return['Booking Date'] = booking_date
    data_return['Passenger Count'] = passenger_count

    return data_outward, data_return

def parse_pdf(file):
    print("Parsing PDF file")
    print("File: ", file)
    try:
        with pdfplumber.open(file) as pdf:
            print("Opened PDF file")
            print("File Details: ", pdf.metadata)
            print("Number of pages: ", len(pdf.pages))
            print("Parsing text from PDF")
            text = ''
            for page in pdf.pages:
                text += page.extract_text()

            print("Text: ", text)
            if is_round_trip_ticket(text):
                return extract_ticket_info_round_trip(text)

            return extract_ticket_info(text)
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return {'error': str(e)}