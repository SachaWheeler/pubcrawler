#!/usr/bin/python
import csv
import psycopg2
from config import config
from time import process_time
import xmltodict
import pprint
import glob
import os
import json


if __name__ == '__main__':
    t1_start = process_time()
    # read database configuration
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    # for file in glob.glob("src_data/ratings/FHRS520en-GB.xml", recursive=True):
    count = 0
    added = 0
    skipped = 0
    for file in glob.glob("src_data/ratings/*.xml", recursive=True):
        with open(file) as fd:
            doc = xmltodict.parse(fd.read(), process_namespaces=True)

        types = dict()
        for item in doc['FHRSEstablishment']['EstablishmentCollection']['EstablishmentDetail']:
            if item['BusinessTypeID'] == '7843':
                count += 1
                print("\n")
                pprint.pprint(item)
                if 'PostCode' not in item:
                    skipped += 1
                    continue

                # find pub
                cur.execute("SELECT * from pub where PostCode = %s", (item['PostCode'],))
                pub = cur.fetchone()
                if pub:
                    added += 1
                    pub_id = pub[0]
                    pprint.pprint(pub)

                    try:
                        rating = int(item['RatingValue'])
                    except:
                        rating = 0
                    try:
                        hygiene = item['Scores']['Hygiene']
                    except:
                        hygiene = 0
                    try:
                        structural = item['Scores']['Structural']
                    except:
                        structural = 0
                    try:
                        confidence = item['Scores']['ConfidenceInManagement']
                    except:
                        confidence = 0

                    cur.execute("""UPDATE pub
                        SET rating = %s,
                            hygiene = %s,
                            structural = %s,
                            confidence = %s
                        where id = %s

                            """ % (rating, hygiene, structural, confidence, pub_id)
                            )

    conn.commit()
    cur.close()
    t1_stop = process_time()

    print(f"{added} added of {count}. {skipped} skipped.")
    print("time taken: :", t1_stop-t1_start)


