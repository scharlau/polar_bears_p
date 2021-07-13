# Parsing Polar Bear Data with Python and Flask
This is a demonstrator app focusing on different ways to use python and flask to parse data for a web application using polar bear tracking data. 

The goal of 'deliberate practice' is to think about how you'd solve this challenge, and to work at developing code to make this work. There is no single 'correct' version of this code. The purpose of the exercise it become familiar with different ways of making the application work. You should explore how this simple application is done in python with flask and sqlite3 so that you understand how the components work together to show up in the views you see in the browser.

Under 'deliberate practice' we offer up the challenge, then think about options for developing a solution, and code for 12 minutes. After that we pause to discuss how people are approaching the problem, and what they're trying to do. This should be repeated three times and then wrapped up with time for people to express what they found most useful during the session. This should take an hour.

Step 1) We'll use data on Polar bears in Alaska to develop our application Data is taken from https://alaska.usgs.gov/products/data.php?dataid=130 Download the zip file and unpack it to a folder. This will give us more data than we need, but that's ok. We're only using it to learn how to import data so that we can use it in our application.

#### Table Relationships for the Data

We'll import data from two related tables. Each polar bear is listed in the USGS_WC_eartag_deployments_2009-2011.csv file and is identified in the BearID column. Each subsequent sighting of a bear is recorded in the USGS_WC_eartags_output_files_2009-2011-Status.csv file. The DeployID column in the second file references the BearID column in the first file. Therefore we end up with a one_to_many relationship between the two files. 

We are not using all of the columns that are here. We could use all of the data, but as we're not biologists, we'll only take what looks interesting to us. You can see the table structure in the parse_csv.py file where we create the tables.

Step 2) We can start developing our application to display the data. Create a new project folder called 'polar_bears' and then cd into the folder via the terminal and execute these commands:

        pyenv local 3.7.9 # this sets the local version of python to 3.7.9
        python3 -m venv .venv # this creates the virtual environment for you
        source .venv/bin/activate # this activates the virtual environment
        pip install --upgrade pip [ this is optional]  # this installs pip, and upgrades it if required.

We will use Flask (https://flask.palletsprojects.com/en/1.1.x/) as our web framework for the application. We install that with 
        
        pip install flask

And that will install flask with its associated dependencies. We can now start to build the application.

### We need to parse a csv file and add the data to a database
The goal is to have the polar bear details on the website, which means we need to put the spreadsheet data into a database. There are a range of options for this, so we'll pick the easiest one for now, and point you in the direction of other options at the end.

We'll start with reading the csv file as that is simple. Put this code into a file called 'parse_csv.py'. This assumes that you put the whole directory (folder) of polar bear data into the application folder. We open the file, and create a reader that loops through each row and then prints it to the screen. The flag for newline='' is the default as we don't know which line ending we should expect. If you look at the documentation for the csv library, then you'll see this mentioned https://docs.python.org/3/library/csv.html. 

        import csv

        with open('PolarBear_Telemetry_southernBeaufortSea_2009_2011/USGS_WC_eartag_deployments_2009-2011.csv', newline='') as f:
        reader = csv.reader(f, delimiter=",")
        next(reader) # skip the header line
        for row in reader:
        print(row)

You should be able to run this to confirm the path is correct, and you can read the file with

        python3 parse_csv.py

With our parsing working fine, then we can move onto the next step of putting the data into a database.

We'll use Sqlite3 as it's simple to create and use for our purposes here.
Go to your terminal and enter this command to create the zero byte text file that will become our database:

        touch polar_bear_data.db

Now we need to connect to the database, and run a query to create our table. Notice in the code below, that we need to open the connection to the database, and then use a cursor to confirm where we are. We'll also drop the table so that we don't add to the data each time we run the file. That means we can add more tables, and still run the file, and not have the rows repeated.

You can find out more about Sqlite3 data types and how they map to python data types at https://docs.python.org/3/library/sqlite3.html 

Add this code between the 'import csv' line and the line that opens the csv file.

        import csv
        import sqlite3

        # open the connection to the database
        conn = sqlite3.connect('polar_bear_data.db')
        cur = conn.cursor()

        # drop the data from the table so that if we rerun the file, we don't repeat values
        conn.execute('DROP TABLE IF EXISTS deployments')
        print("table dropped successfully");
        # create table again
        conn.execute('CREATE TABLE deployments (BearID INTEGER, PTT_ID INTEGER, capture_lat REAL, capture_long REAL, Sex TEXT, Age_class TEXT, Ear_applied TEXT)')
        print("table created successfully");

With the database and table created, we can now turn to the parsing of the spreadsheet. We don't want all of the data, but only specific columns, which means we need to specify which colums we want, and then assign them values for insertion into the database. 

Add this code below the lines parsing the csv. Notice that (a) that we need to 'commit()' the query after it's executed, and that (b) we close the database connection at the very end too. We're only interested in some values, which is why we specify the ones we want to store.

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

            cur.execute('INSERT INTO deployments VALUES (?,?,?,?,?,?,?)', (BearID, PTT_ID, capture_lat, capture_long, Sex, Age_class, Ear_applied))
        print("data parsed successfully");
        conn.commit()
        conn.close()

Now that the data is in the database we can build the web front end to see the data.

### Building the web components
We need a landing page to show all of the bears, and then another to show a single bear. The single bear page could later also show the sightings of each bear, which are in the second csv file.

We can now start our actual app file, 'polar_bears.py', which needs to be in the main folder. This should look familiar to you if you've been doing a number of flask sites.

        import sqlite3
        from flask import Flask, render_template

        app = Flask(__name__)

        @app.route('/')
        def index():
            # open the connection to the database
            conn = sqlite3.connect('polar_bear_data.db')
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("select * from deployments")
            rows = cur.fetchall()
            conn.close()
            return render_template('index.html', rows=rows)

We can put together a simple html page to display the results in a template folder, so that we can add another one there later to 'show' the results for a specific bear. 

Create a 'templates' folder, and put an index.html file in there. You can put this code in the file to loop through the results of our general query to retrieve all of the bears.

        <html>
        <head><title>Polar Bear Tracking</title></head>
        <body>
        <h1>Polar rows Tagged for Tracking</h1>
    
            {% for row in rows %}
            <p>Bear: 
            <b>{{row["BearID"]}}</b> | 
            {{row["PTT_ID"]}} | 
            {{row["capture_lat"]}} | 
            {{row['capture_long']}}	| 
            {{row["Sex"]}} |
            {{row["Age_class"]}} |
            {{row['Ear_applied']}}	
            </p>
            {% endfor %}

        </body></html>

We can confirm this runs by setting a few variables in your environment via the terminal (this assumes you're either using Linux or MacOS)
        
        export FLASK_APP=polar_bears.py
        export FLASK_ENV=development
        python3 -m flask run

You can now view your site at localhost:5000 in the browser. It will show you a list of bears, and confirms that everything works correctly.

### Adding a second table

The file ending with ...status.csv holds details for sightings of bears, so that you could see where and when their radio transmitters were noticed. Again, we're only interested in some columns from the file. We can add an autoincrementing primary key too for later use.

 status_id INTEGER PRIMARY KEY AUTOINCREMENT, deployID INTEGRER, recieved TEXT, latitude REAL, longitude REAL, temperature REAL, deployment_id INTEGER

This will give us a table that references the deployments table via the deployment_id column, and let us show all sightings of a bear on the same page.

You can add more details to the parse_csv.py file to read the status.csv file in, and to store the details into a new 'status' table in a similar manner as before.

******************************************************
**** The data is messy and the parsing will break ****
******************************************************

When you run this new method you will find the parsing breaks due to gaps in the data. It broke because one of the cells had no data, or had the data format different from what the parser was expecting. This is the nature of real-world data. It's not always nice and tidy.

Given we're only parsing this data as an exercise, you can find the broken cell, and then you can either a) delete the row, and then re-run the rake command, or b) write a few lines of code as an 'if/else' statement to check the value of the cell and to either ignore it, or do something else as required to make it work.

For simplicity here, just delete the row and move on so that you get the file imported and the page views showing. You can see the start of this work if you switch to the 'solution' branch of this repository and look at the rake file there. You'll find the solution branch in the drop-down menu at the top of the file listing on the left.

We want to link the two tables together so that there is a relationship between them. In order to do this you need to modify the parsing file. You need to 'look up' the ID of each bear in the Deployment table in order to reference this in each 'Status' instance. You can do this with a few lines like this:

        bear_temp = row[0]
        print(bear_temp)
        cur.execute('SELECT * from deployments WHERE BearID=?', (bear_temp,))
        temp_row = cur.fetchall() #temp_row is a tuple, and not an array, so need first item from first item
        print(temp_row[0][0])

        deployID = int(row[0])
        deployment_id = int(temp_row[0][0])
        ...

Notice that we are dealing with tuples from a database, so we need to unwrap the data carefully to get the parts we want. We do this in order to ensure that each 'Status' instance is tied correctly to a 'Deployment' instance.

This is rough and ready

This works, but also shows issues. For example, BearID 20414 appears twice in deployments. If you select the second one, then you have no connected sightings. If you pick the first one, then you have LOTS of sightings.

From here you could show the locations of the sightings on a map using the GPS coordinates. You could also do a chart showing how many sightings there were for each bear by date. You could also do something with the other categories to produce visualisations to suit your needs.

## Doing the work
Now that the basics are working, we can see what else is possible in this application.
We have some basic things here done in a minimal manner. We could probably modify the database operations to pull them together better in one place, and while we have the concept of a 'bear' we haven't created a model of one either. That means we do everything as database queries, instead of as object orientated programming to manipulate the data.

Round one - you've done already by adding the second table with data from the 'status.csv' file. You should probably add a primary key to both the deployments and status table to make queries easier.
Round two should be pulling together the code for bears into models and database commands.
Round three should be exploring what else might be possible, even if only to total up some values of the bear attributes to display on a page.
