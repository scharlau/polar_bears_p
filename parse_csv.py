import csv
import sqlite3

# open the connection to the database
conn = sqlite3.connect('polar_bear_data.db')
cur = conn.cursor()

# drop the data from the table so that if we rerun the file, we don't repeat values
conn.execute('DROP TABLE IF EXISTS deployments')
conn.execute('DROP TABLE IF EXISTS statuses')
print("tables dropped successfully");
# create table again
conn.execute('CREATE TABLE deployments (deploy_id INTEGER PRIMARY KEY AUTOINCREMENT, BearID INTEGER, PTT_ID INTEGER, capture_lat REAL, capture_long REAL, Sex TEXT, Age_class TEXT, Ear_applied TEXT)')
conn.execute('CREATE TABLE statuses (status_id INTEGER PRIMARY KEY AUTOINCREMENT, deployID INTEGRER, received TEXT, latitude REAL, longitude REAL, temperature REAL, deployment_id INTEGER)')
print("table created successfully");

# open the file to read it into the database
with open('PolarBear_Telemetry_southernBeaufortSea_2009_2011/USGS_WC_eartag_deployments_2009-2011.csv', newline='') as f:
    reader = csv.reader(f, delimiter=",")
    next(reader) # skip the header line
    for row in reader:
        print(row)

        BearID = int(row[0])
        PTT_ID = int(row[1])
        capture_lat = float(row[6])
        capture_long = float(row[7])
        Sex = row[9]
        Age_class = row[10]
        Ear_applied = row[11]

        cur.execute('INSERT INTO deployments VALUES (NULL,?,?,?,?,?,?,?)', (BearID, PTT_ID, capture_lat, capture_long, Sex, Age_class, Ear_applied))
        conn.commit()
print("data parsed successfully");

# open the file to read it into the database - look up bear in deployement for deployment_id value
with open('PolarBear_Telemetry_southernBeaufortSea_2009_2011/USGS_WC_eartags_output_files_2009-2011-Status.csv', newline='') as f:
    reader = csv.reader(f, delimiter=",")
    next(reader) # skip the header line
    for row in reader:
        print(row)
        
        # sanity checking for empty cells - this clears up most missing data to parse the file
        temp_temp = 0
        temp_bear_id = 0
        if row[4] is not '':
            if row[9] is not '':
                temp_temp = row[9]
            else:
                temp_temp = 0 # this works but not if we want to be correct

            bear_temp = row[0]
            print(bear_temp)
            cur.execute('SELECT * from deployments WHERE BearID=?', (bear_temp,))
            temp_row = cur.fetchall() #temp_row is a tuple, and not an array, so need first item from first item
            print(temp_row[0][0])

            deployID = int(row[0])
            deployment_id = int(temp_row[0][0])
            received = row[2]
            latitude = float(row[4])
            longitude = float(row[5])
            temperature = float(temp_temp)

            cur.execute('INSERT INTO statuses VALUES (NULL,?,?,?,?,?,?)', (deployID, received, latitude, longitude, temperature, deployment_id))
            conn.commit()
        else: # skip the row
            next(reader)
print("data parsed successfully");

conn.close()
        
