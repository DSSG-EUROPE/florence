<p align="center">
  <img src="http://dssg-eu.org/florence/img/dssg_logo_website.svg" width="640"/>
</p>

## Data-Driven Planning for Sustainable Tourism in Tuscany

Project website with interactive visualizations: http://dssg-eu.org/florence. 

> Note that images, formatting, and some interactive visualizations are currently not working on the site, because of a change in hosting. We are working to move the hosting service in order to restore the website, but in the mean time, the code underyling the website is still available in this repo at https://github.com/DSSG-EUROPE/florence/tree/master/src/website-template. 

### Project & Partners
Mass tourism is at a tipping point. Larger populations now have the budget for travel and the awareness of historic destinations. High-speed trains and low-cost airlines give greater mobility options. Online resources such as travel information sites, social media, and mapping applications help people aspire to destinations and plan itineraries. Cities working with analog management of their cultural resources may be ill-equipped to react to new patterns of mass tourism. Local, regional, and national governments are asking how they can accommodate tourists and sustain the sector while maintaining the quality of life for residents. 

Together with Toscana Promozione Turistica, we looked into the patterns of tourism in Florence using data. The city of Florence has already made remarkable innovations in its tourism management. The Firenzecard, a museum card that creates a common entry scheme for the top 72 attractions in Florence, is a major achievement in making the city accessible and spreading visits among museums.

Through this project, we outline a vision of a future system of smart tourism management in Florence, where the digital traces created by new tourists can feed back into the city’s knowledge of tourist patterns to inform decision-making and management. Our work attempts to shed light on what current data sources can tell us about what is happening in the city. 

Our main data sources were telecom call detail records (CDR) from 1st June 2016 through 30th September 2016 and museum entry logs from the Florence museum card (Firenze card). Together, this data allows us to provide a situation analyses: a partial assessment of the status quo of mass tourism in Florence, aiming to gain insight on the sites experiencing crowding (and vice versa), and specific times of the day, week, month or entire summer of 2016.

### Key questions and Data
Refer to our final report in `docs/` to get a sense of the key questions we attempted to address with our analysis. The report also contains a description of all of the data sources we received and how we used each source for our analysis.

### Getting Started with the Repo

#### Software

##### Installing git and forking the repo
Fork a copy of this repository onto your own GitHub account and `clone` your fork of the repository onto your computer.

`git clone https://github.com/<your_github_username>/optourism.git`

##### Installing Python and setting up the virtual environment
[Install Python 2.7.13](https://www.python.org/downloads/release/python-2713/) and the [conda package manager](https://conda.io/miniconda.html) (use miniconda, not anaconda, because we will install all the packages we need).

Navigate to the project directory inside a terminal and create a virtual environment (replace <environment_name>, for example, with "dssg") and install the [required packages](https://github.com/DSSG2017/optourism/blob/master/requirements.txt):

`conda create -n <environment_name> --file requirements.txt python=2.7.13`

Activate the virtual environment:

`source activate <environment_name>`

By installing these packages in a virtual environment, we avoid dependency clashes with other packages that may already be installed elsewhere on your computer.

#### Database

The data was originally obtained in various CSV files and text files from our project partners. These are then cleaned imported into a PostgreSQL database. To see the SQL scripts used to create tables and materialized views for this project, reference `src/sql/`.

We recommend accessing the database through a client with a GUI such as [DBeaver](https://dbeaver.jkiss.org/download/).

Following installation, please ask one of the fellows for instructions on setting up a connection to the database [:

Once you have set up a database, fill in your credentials in a new file called `src/utils/dbcreds.py` which should be modeled off of `src/utils/dbcreds.example`. This step will allow you to use our database utility file.

### Directory structure

The project directory is structured into 5 main folders:
* `src/` includes source code for pipeline, feature analysis, data wrangling for visualizations, and our website report.
* `notebooks/` includes python notebooks for data exploration and analysis with descriptive text in a human readable format.
* `viz/` includes source code for visualizations built from [Deck.GL](https://uber.github.io/deck.gl) examples.
* `docs/` includes documents and reports produced during the fellowship with early results and commentary.
* `dev/` includes development scripts which were used during the early development stages and are still in a rough format.

```
optourism/
├── src/
|   ├── features/
|   ├── output/
│   ├── sql/
|   |   | |_<postgresql_scripts>.sql
|   |   | |_ ...
|   ├── utils/
|   |   ├── database/
|   |   ├── plotting/
|   ├── website-template/
|   ├── pipeline.py
|
├── notebooks/
|   | |_<analysis_notebook>.ipynb
|   | |_ .../
|
├── viz/
|    ├── fountain/
|    ├── paths/
|
├── docs/
|   | |_DSSG_Florence_report.pdf
|
├── dev/
|   ├── notebooks/
|   ├── sql/
|
└── requirements.txt
```

### Authors
This project was conducted as part of Data Science for Social Good (DSSG) Europe 2017 fellowship, further details of 
the twelve week summer fellowship can be found here:
https://dssg.uchicago.edu/europe/

**DSSG Fellows**: Io Flament, Cristina Lozano, Momin Malik

**Technical Mentor**: Qiwei Han

**Project Manager**: Laura Szczuczak

### Acknowledgments

We would like to acknowledge all of the hard work of our partners, data partners, and mentors. Thank you to Alberto Peruzzini and Laura Morelli at Toscana Promozione Turistica for introducing us to the problem, and for coordinating dataset collection. Additionally, many thanks to the following organizations for making the following data open and available to us:


- Comune di Firenze, Assessorato al Turismo e Direzione Cultura.
- Linea Comune S.p.A. for the detailed logs of Firenzecard visits.
- The Ufficio di Statistica at Ministero dei Beni e delle Attività Culturali e del Turismo for the monthly aggregates of visitors to Florence State Museums. 
- Centro Studi Turistici di Firenze for their analysis of tourism flows in Florence.
- Toscana Aeroporti for the daily airport arrivals at the Florence airport.
- Uffici informazioni turistiche della Città Metropolitana di Firenze and Uffici Informazioni Turistiche del Comune di Firenze for the tourism office data.
- Servizi alla Strada S.p.A. for the tourism bus data.
- Istituto Regionale Programmazione Economica Toscana for the data from cruise ship arrivals in the Port of Livorno and their studies of tourism in Tuscany.
- Vodafone Italy and the Collective Sensing (CS) Research Foundation for providing and managing access to the Telecommunications data for Florence.
- Nova School of Business and Economics for its leadership to make this project possible, and all the logistic and other support during the project execution.
- Amazon Web Services for the Cloud for Research Credits.


*All analysis and opinions contained here are the authors’ own, and are not necessarily held or endorsed by any of the partners or data-providing agencies.*

### License
This project is licensed under the MIT License - see the LICENSE.md file for details


