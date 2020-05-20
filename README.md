# COVID19 Data Analysis
Author: HanishKVC
Version: v20200520IST0241

## Basic working version of generic logic; Branch:master WIP

### Overview

This contains a set of simple python scripts to process and plot
covid19 data about India and World.

Option1: Fetch and AnalPlot EUWorld and Cov19In based datasets

hkvc-covid19-analtoolkit.py

Option2: Load and AnalPlot EUWorld and or Cov19In previously
fetched/converted csv datasets

hkvc-covid19-analtoolkit.py [--cov19in data/Cov19In-DATE-confirmed.csv] [--euworld data/EUWorld-DATE.csv]

NOTE: Remember to look at the saved image. The Plot window shown
will be messed up due to too many plots which wont fit the screen.

### Analyse and Plot user selected geoIDs

Instead of letting the program select the regions whose data should
be plotted automatically based on predefined criterias in the program,
the user can explicilty specify the regions whose data should be
plotted by passing the list of geoIds to the program like this

hkvc-covid19-analtoolkit.py --sel datasrc_name geoid1 geoid2 ...

example:

hkvc-covid19-analtoolkit.py --sel Cov19In  KL KA DL MH --sel EUWorld IN US IE AE CA BR RU

### logic to keep in mind

#### EUWorld xls to csv conversion

##### date field

The logic assumes that libreoffice is configured for language setting
to have date format of DD/MM/YYYY (for ex: English-India).

If the xls to csv conversion generates the date field in a format
different from DD/MM/YYYY, on your machine, then edit the iY, iM, iD
arguments passed within EUWorldDataSrc.conv_date func of EUWorld
datasrc class. OR ELSE, change the date format in language setting of
libreoffice to DD/MM/YYYY format.

##### loading libreoffice

The logic uses libreoffice internally to help with the xls to csv
conversion. So when the program is run for the first time in a given
user session, it may take more time than what is currently accounted
for the libreoffice to start up. In which case, the logic will timeout
and exit. So one is required to rerun the program a 2nd time to get
it to do its job.

### Misc

To test datasrc class/module on its own

python datasrc.py

## Old working logic; Branch:v20200423IST2000_BasicFull

This contains a set of simple python scripts to process and plot
covid19 data about India.

hkvc-covid19india.py
hkvc-mygov-india.py

