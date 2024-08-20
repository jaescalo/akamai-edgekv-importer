# Akamai EdgeKV Python Importer

This tool aids the initial EdgeKV seeding. The script reads from a CSV file, converts each row to a JSON string which then is used as the value in EdgeKV. As for the item id for EdgeKV it is passed as part of the arguments for the script. 

## Compatible CSV
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
  -f, --filename PATH    Path to the CSV file  [required]
  -k, --key-column TEXT  Column name to use as the key  [required]
  -d, --delete           Delete the items in EdgeKV instead of upserting
  --help                 Show this message and exit.
```

### Example #1
To import all entries in CSV and use the `code` column as the item ID for EdgeKV:
```
$ python3 edgekv_importer.py --filename example_input.csv -k code
```

### Example #2
To delete all entries in CSV and use the `key` column as the item ID for EdgeKV:
```
$ python3 edgekv_importer.py --filename example_input.csv -k key --delete
```