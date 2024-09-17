import csv

def create_csv(parsed_results, output_file='output.csv'):
    """
    Create a CSV file from the parsed results.
    """
    # Define the column headers
    headers = ['Filename', 'Booking Date', 'Date', 'Start', 'Destination', 'Passenger Count', 'Price', 'Ticket Number']
    
    # Write to a CSV file
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        # Write the headers
        writer.writeheader()

        # Write the rows from parsed results
        for result in parsed_results:
            row = {
                'Filename': result['filename'],
                'Booking Date': result['parsed_data']['Booking Date'],
                'Date': result['parsed_data']['Date'],
                'Start': result['parsed_data']['Start'],
                'Destination': result['parsed_data']['Destination'],
                'Passenger Count': result['parsed_data']['Passenger Count'],
                'Price': result['parsed_data']['Price'],
                'Ticket Number': result['parsed_data']['Ticket Number']
            }
            writer.writerow(row)
