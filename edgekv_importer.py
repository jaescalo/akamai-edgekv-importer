import os
import csv
from concurrent.futures import ThreadPoolExecutor
from akamai_apis import Session

import time
import click

from dotenv import load_dotenv
load_dotenv()

# Get all the necessary env variables
network = os.environ.get('AKAMAI_NETWORK')
namespace_id = os.environ.get('AKAMAI_EKV_NAMESPACE_ID')
group_id = os.environ.get('AKAMAI_EKV_GROUP_ID')
account_key = os.environ.get('AKAMAI_CREDS_ACCOUNT_KEY')

# Check for account key switch for API calls
if account_key:
    session = Session(switch_key=account_key)
else:
    session = Session()


@click.command()
@click.option('--filename', '-f', required=True, type=click.Path(exists=True), help='Path to the CSV file')
@click.option('--key-column', '-k', required=True, help='Column name to use as the key')
@click.option('--delete', '-d', is_flag=True, help='Delete the items in EdgeKV instead of upserting')
def process_csv(filename, key_column, delete):
    """Read the CSV file and upsert the data to Akamai EdgeKV in parallel"""
    try:
        # Get the number of rows in the CSV file
        with open(filename, 'r') as csvfile:
            reader_rows = csv.reader(csvfile)
            row_count = sum(1 for row in reader_rows)
        print(f"CSV file has {row_count} rows")
        
        # Track progress
        processed_rows = 0
        
        start_time = time.time()
        
        # Get the DictReader object
        with open(filename, "r") as csvfile:
            dict_reader = csv.DictReader(csvfile)
            tasks = []
            # Upload redirects in parallel. Based on https://techdocs.akamai.com/edgekv/docs/limits:
            # - Burst limit: 24 hits per second (during any 5 second period)
            # - Average limit: 18 hits per second (during any 2 minute period)
            # Limiting the max_workers=9
            with ThreadPoolExecutor(max_workers=9) as executor:
                for row in dict_reader:
                    key = row[key_column]
                    if delete:
                        tasks.append(executor.submit(session.delete_ekv_item, namespace_id, group_id, key, network))
                    else:
                        tasks.append(executor.submit(session.upsert_ekv_item, namespace_id, group_id, key, row, network))

                # Wait for all the tasks to complete
                for task in tasks:
                    processed_rows += 1
                    print(f"Processed {processed_rows}/{row_count} URLs", end="\r")
                    task.result()
        
            end_time = time.time()

            execution_time = end_time - start_time
            operations_per_second = row_count / execution_time

            print(f"\nProcessed {row_count} URLs in {execution_time:.2f} seconds")
            print(f"Average rate: {operations_per_second:.2f} operations per second")

            # Create a response message
            response = f"Successfully processed {row_count} URLs at a rate of {operations_per_second:.2f} ops/sec"

            return response
    
    except Exception as err:
        # If an error occurs, return None for the response and the error message
        return str(err)

def main():
    """Entry point for the script"""
    # filename = input("Enter the CSV filename: ")
    # key_column = input("Enter the column name to use as the key: ")
    #process_csv(filename, key_column)
    process_csv()

if __name__ == "__main__":
    main()