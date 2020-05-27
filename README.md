# COVID19 Data Analysis
Author: HanishKVC
Version: v20200527IST1852

## Covid19 Analtoolkit, Branch:master WIP

### Overview

This contains a set of simple python scripts to process and plot
covid19 data about India and World. This is the version built on
top of generic helper modules.

NOTE: It contains two useful python modules, which can be used by
other programs they are datasrc.py and analplot.py

Option1: Fetch and AnalPlot EUWorld and Cov19In based datasets

hkvc-covid19-analtoolkit.py

Option2: Load and AnalPlot EUWorld and or Cov19In previously
fetched/converted csv datasets

hkvc-covid19-analtoolkit.py [--cov19in data/Cov19In-DATE-confirmed.csv] [--euworld data/EUWorld-DATE.csv]

NOTE: Remember to look at the saved image. The Plot window shown
may be messed up due to too many plots which wont fit the screen.

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
it to do its job. With the latest update the underlying program uses
a better way of connecting to libreoffice, so chances of this issue
creeping up should be less. The current default timeout is around
128 seconds, if libreoffice doesnt start even after 128 seconds, then
it will timeout.


### Data got from

#### India related data got from

http://api.covid19india.org/states_daily_csv/confirmed.csv

This contains data till the day (or the prev date, depending on at what time it was fetched), when it is fetched.

#### World related data got from

https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-YYYY-MM-DD.xlsx

Note: Replace YYYY, MM and DD with the date one is interested in. It will contain data till that date.


### Misc

#### Other arguments

--test_mixmatch : allows one to test/compare different data operations

--no_scalediff : Dont scale the diff data used in plotxy inset.

--scalediff : scale the diff data used in plotxy inset.

--plotxy_gsp : group the plotxy regions using Top30% percentile

--plotxy_gsn : group the plotxy regions based on whether they are neighbours or not.

--plotsel_partial : plot only the top two rows, which are summary plots.


## DataSrc/AnalPlot classes/Modules

### Overview

These are two useful python modules, which can be used by other programs.
Go through the source as well as the usage/test sample code at the end
to understand these modules and use them.

Also from within python one can do help(analplot) or help(datasrc) to get
details about these python modules.

#### DataSrc

DataSrc allows one to download and convert data from the net, so that it
can be used.

#### AnalPlot

AnalPlot allows one to load data and inturn look at the data after applying
different data operations on it, as required. Analplot allows one to just
ask for a given processed data to be printed/displayed and the logic will
automatically generate the required data by calling the data operations
as required on the available data, in a efficient way. This requires the
user to specify the data in AnalPlot's dataKey DataOpsChaining notation.

dataKey DataOpsChaining notation:

'MyData>DataOp1>DataOp2>DataOpWithArgs3(Arg1=Val1,Arg2=Val2)>...>DataOpN'

Available DataOps are

* diff, cumsum, movavg, scale

* rel2sum, rel2mean

However if one wants, one can even directly call the calc functions, as
required, and later use the generated data for futher processing and or
plotting.

In either case the results of each data op step is internally cached, so
that if the same is needed as part of some other calculation, it can be
reused directly without needing to calculate again.

The available plot types are plot, plotxy and boxplot.

### Test

To test datasrc/analplot class/module on its own, one could run

python datasrc.py
python analplot.py



## Old working logic; Branch:v20200423IST2000_BasicFull

This contains a set of simple python scripts to process and plot
covid19 data about India.

hkvc-covid19india.py
hkvc-mygov-india.py

