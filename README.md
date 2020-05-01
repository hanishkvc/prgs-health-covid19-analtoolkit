# COVID19 Data Analysis

## Updating logic to be more generic; Branch:master WIP

This contains a set of simple python scripts to process and plot
covid19 data about India and World.

Option1: Fetch and AnalPlot EUWorld and Cov19In based datasets

hkvc-covid19-analtoolkit.py

Option2: Load and AnalPlot EUWorld and or Cov19In previously
fetched/converted csv datasets

hkvc-covid19-analtoolkit.py [--cov19in data/Cov19In-DATE-confirmed.csv] [--euworld data/EUWorld-DATE.csv]

NOTE: Remember to look at the saved image. The Plot window shown
will be messed up due to too many plots which wont fit the screen.

To test datasrc class/module on its own

python datasrc.py

## Old working logic; Branch:v20200423IST2000_BasicFull

This contains a set of simple python scripts to process and plot
covid19 data about India.

hkvc-covid19india.py
hkvc-mygov-india.py

