# Akamai EdgeKV Python Importer

This tool aids the initial EdgeKV seeding. The script reads from a CSV file, converts each row to a JSON string which then is used as the value in EdgeKV. As for the item id for EdgeKV it can be any of the column names, just pass it as part of the arguments for the script.
The script also allow for EdgeKV delete operations.

## Modes of Operation
There are 2 modes of operation for writing/deleting to EdgeKV: `edgeworker` or `api`.

### EdgeWorker Mode
This mode leverages an EdgeWorker to perform the writes/deletes to EdgeKV. The main reason is because EdgeKV allows for more writes/deletes per second than the administrative API. See the [rate limits at techdocs.akamai.com](https://techdocs.akamai.com/edgekv/docs/limits)

* An EdgeWorker is required for this mode and you can check the code in charge to writing/deleting to EdgeKV in `./edgeworker/main.js`. 

* To enable the EdgeWorker mode use the `--mode edgeworker` or `-m edgeworker` option. Examples below.

* This mode additionally requires the URL where the EdgeWorker is configured. The URL is passed with the `-u` option.

* Keep in mind that the `edgekv.js` [helper library](https://techdocs.akamai.com/edgekv/docs/library-helper-methods) and the `edgekv_tokens.js` [access tokens](https://techdocs.akamai.com/edgekv/docs/generate-and-retrieve-edgekv-access-tokens) are required for the EdgeWorker to successfully write/delete to EdgeKV. 

**Test shows this method to be 10x faster**

### API Mode
This mode uses the Akamai APIs to perform the writes/deletes to EdgeKV. No EdgeWorker needs to be configured, however the write/delete speed is limited to the administrative API. See the [rate limits at techdocs.akamai.com](https://techdocs.akamai.com/edgekv/docs/limits)

* To enable the API mode use the `--mode api` or `-m api` option. Examples below.

## CSV File
The CSV must contain all the entries to import including the item id. Here's an example:
```
key,code,language,isd
Afghanistan,AFG,ps|da,93
Albania,ALB,sq,355
Algeria,DZA,ar|fr,213
Andorra,AND,ca|es|fr,376
Angola,AGO,pt,244
```
In this particular example the first column is named `key`. And we will use this column as the item ID for EdgeKV.

## Usage

```
Usage: edgekv_importer.py [OPTIONS]

  Read the CSV file and upsert the data to Akamai EdgeKV in parallel

Options:
  -m, --mode [api|edgeworker]  Write to EKV via the admin API or an EdgeWorker
                               [required]
  -f, --filename PATH          Path to the CSV file  [required]
  -k, --key-column TEXT        Column name to use as the key  [required]
  -d, --delete                 Delete the items in EdgeKV instead of upserting
  -u, --upload-url TEXT        The URL to upload data to for EdgeWorker mode
  --help                Show this message and exit.
```

### Example #1
To import all entries using the Edgeworker mode in CSV and use the `code` column as the item ID for EdgeKV:
```
$ python3 edgekv_importer.py --mode edgeworker --filename example_input.csv -k code -u "https://some.akamaized.host/path"
```

### Example #2
To delete all entries using the Edgeworker mode in CSV and use the `key` column as the item ID for EdgeKV:
```
$ python3 edgekv_importer.py --mode edgeworker --filename example_input.csv -k code -u "https://some.akamaized.host/path" --delete
```

### Example #3
To import all entries using the API mode in CSV and use the `code` column as the item ID for EdgeKV:
```
$ python3 edgekv_importer.py --mode api --filename example_input.csv -k code 
```

### Example #4
To delete all entries using the API mode in CSV and use the `key` column as the item ID for EdgeKV:
```
$ python3 edgekv_importer.py --mode api --filename example_input.csv -k code --delete
```
