IHG Activity Scraper
####################

Fetch all activity for the last year from your IHG account and print all stays.

Additionally, print the IC stays plus a guesstimate of USD spend (elite qualifying points / 10).

HOWTO
-----

Copy ihg-credentials.json.example to ihg-credentials.json:
```cp ihg-credentials.json.example ihg-credentials.json```

Edit the file, add your IHG Username and PIN.

Then run the ihg-account-data.py to fetch the activity data and write it out to a
ihg-activities-<timestamp>.json file. This is done using selenium with the firefox/geckodriver
combo and requests.

You can then run the analytics using the parsr script:
```ihg-parse-activities.py ihg-activities-<timestamp>.json```

Docker
------

To make things easier, a Dockerfile is included:

```make docker-build
make docker-run```

This will build a docker container and run the script. After a little bit of time, the
data will be printed to the screen.

