Fundamentals analysis procedure:
1. Generate list of all stock tickers & values with extract_company_data.py and store
   (remotely or otherwise)

   Allows to filters stock by:
   -Industry
   -Sector
   -Market Cap   (converts to US$ using today's rate)
   -Currency
   -Country
   -Exchange

   Allows to set a window of mktCap to include as a fraction of target company mktCap for instance
   MKT_CAP_WINDOW = {'lower': .2, (20% to 5x the target market cap)
                     'upper': 5}

   Update URL in plotter_defaults to reflect location of remote storage
   Run time on 2.9 GHz 6-Core Intel Core i9 (26957 companies)  = 6 hours

2. Comparison plots : a/ optionally generate suggested list of peers with suggest_peers.py
                      b/ load to list generated in a into comparison_plot_driver.py
                      usage: python comparison_plot_driver.py filename
                      NB: the first ticker symbol in the csv file must be the target ticker

3. Time series plots: fundamentals_plot_driver.py
