# auto_auto
Automatically fetch automobile data (for folks from BC)

First, set up your environment using `requirements.txt` (pip) or `conda_reqs.txt` (conda).

Next, decide your car filters, and set these in `main.py`. Allowed for now are max/min price, km, year.  
Filters should be strict, the ideal is < 100 cars per search.

Also set a subset of (make, model) pairs, or set this to `None` to allow all.  
Note that `clutch.py` maintains its own make/model -> numeric ID mapping that Clutch uses, so more may need to be added
if your make/model values are not yet used.

Finally, run the script, which will dump the results for today into a folder:
```
$ python main.py
...opens a browser, does the scraping, and writes to data/yyyy-mm-dd.csv
```


To dig deeper into today's results, either import into an application (e.g. excel or google sheets),
or run the analysis tool for today, in which you can put some filters to narrow your search even further:
```
$ python -i today.py
```
