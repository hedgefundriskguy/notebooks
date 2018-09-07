"""
    Functions for getting maket data
"""
import urllib as u
import json

import pandas as pd
from datetime import datetime

class MarketData:
    """ Encapsulates functions for getting data out of XIgnite and Yahoo """
    xigniteToken = "Get your own token"

    def get_stock_quote_by_any_id(self, ticker, idtype, eff_date):
        """
        Returns stock quote from XIgnite by specifying id type
        """
        urlfun = "http://www.xignite.com/xGlobalHistorical.json"
        urlfun = urlfun + "/GetGlobalHistoricalQuote"
        urlfun = urlfun + "?IdentifierType={0}"
        urlfun = urlfun + "&Identifier={1}&AdjustmentMethod=SplitOnly"
        urlfun = urlfun + "&AsOfDate={2}&_Token={3}"
        url = str.format(urlfun, idtype, ticker, eff_date, self.xigniteToken)
        resp = u.request.urlopen(url)
        bytearr = resp.read()
        text = bytearr.decode()
        data = json.loads(text)
        if len(data) > 0:
            return data
        else:
            return []

    def get_stock_quote(self, ticker, eff_date):
        """
            Get Stock quote by symbol
        """
        res = self.get_stock_quote_by_any_id(ticker, 'Symbol', eff_date)
        return res


    def get_13f(self, cik):
        """
        Download 13F form Edgar using XIgnite
        """
        urlfun = "http://www.xignite.com/xHoldings.json/GetLatestHoldings?"
        urlfun = urlfun + "ManagerCIK={0}&_Token={1}"
        url = str.format(urlfun, cik, self.xigniteToken)
        resp = u.request.urlopen(url)
        bytearr = resp.read()
        text = bytearr.decode()
        data = json.loads(text)
        if len(data) > 0:
            if data['Outcome'] == 'Success':
                filing = data['Filing']
                holdingsarray = filing['Holdings']
                port = pd.DataFrame(holdingsarray)
                tot_v = port['Value'].sum()
                port['Weight'] = [v / tot_v for v in port['Value']]
                port['Symbol'] = [s['Symbol'] for s in port['Security']]
                port['Industry'] = [s['CategoryOrIndustry'] for s \
                    in port['Security']]
                port = port[['Name', 'CUSIP', 'Shares', 'Symbol', 'Value', \
                    'Industry', 'Weight']]
                return port
            else:
                return []
        else:
            return []


    

    def get_stock_history(self, ticker, startdate, enddate):
        """
            Get stock history from xignite
        """
        urlfun = "http://www.xignite.com/xGlobalHistorical.json/"
        urlfun = urlfun + "GetGlobalHistoricalQuotesRange?"
        urlfun = urlfun + "IdentifierType=Symbol"
        urlfun = urlfun + "&Identifier={0}"
        urlfun = urlfun + "&AdjustmentMethod=SplitOnly"
        urlfun = urlfun + "&StartDate={1}"
        urlfun = urlfun + "&EndDate={2}"
        urlfun = urlfun + "&_Token={3}"
        url = str.format(urlfun, ticker, startdate, enddate, self.xigniteToken)
      
      
        resp = u.request.urlopen(url)
        bytearr = resp.read()
        text = bytearr.decode()
        data = json.loads(text)
        if len(data) > 0:
            outcome = data['Outcome']
            if outcome == 'Success':
                quotes = data['GlobalQuotes']
                qdf = pd.DataFrame(quotes)
                tsdata = qdf[['Date', 'Last']]
                dtidx = [datetime.strptime(d, '%m/%d/%Y').date()  \
                    for d in tsdata['Date']]
                tsdata.index = dtidx
                tsdata = tsdata[['Last']]
                return tsdata
            else:
                return []
        else:
            return []

    def get_future_quote(self, ticker, month, year):
        urlfun = "http://www.xignite.com/xFutures.json/GetDelayedFuture?Symbol={0}&Month={1}&Year={2}&_Token={3}"
        url = str.format(urlfun,ticker,month,year,self.xigniteToken)
        resp = u.request.urlopen(url)
        bytearr = resp.read()
        text = bytearr.decode()
       
        data = json.loads(text)
    
        if len(data) > 0:
            outcome = data['Outcome']
            if outcome == 'Success':
                return data;
        else:
            return None
   
        
    def get_future_quote_hist(self, ticker, month, year, dt):
        urlfun = "http://www.xignite.com/xFutures.json/GetHistoricalFuture?Symbol={0}&Month={1}&Year={2}&AsOfDate={3}&_Token={4}"
        url = str.format(urlfun,ticker,month,year,dt,self.xigniteToken)
        resp = u.request.urlopen(url)
        bytearr = resp.read()
        text = bytearr.decode()
           
        data = json.loads(text)
    
        if len(data) > 0:
            outcome = data['Outcome']
        if outcome == 'Success':
            return data;
        else:
            return None
            
    def get_next_future(self, ticker):
        urlfun = "http://www.xignite.com/xFutures.json/GetNextFuture?Symbol={0}&_Token={1}"
        url = str.format(urlfun,ticker,self.xigniteToken)
        resp = u.request.urlopen(url)
        bytearr = resp.read()
        text = bytearr.decode()
           
        data = json.loads(text)
    
        if len(data) > 0:
            outcome = data['Outcome']
        if outcome == 'Success':
            return data;
        else:
            return data['Message']
            
    def get_future_history(self, ticker, sdate,edate):
        urlfun = "http://www.xignite.com/xFutures.json/GetHistoricalSpotRange?Symbol={0}&StartDate={1}&EndDate={2}&_Token={3}"
        url = str.format(urlfun,ticker,sdate,edate,self.xigniteToken)
        resp = u.request.urlopen(url)
        bytearr = resp.read()
        text = bytearr.decode()
       
        data = json.loads(text)
    
        if len(data) > 0:
            outcome = data['Outcome']
            if outcome == 'Success':
                df = pd.DataFrame(data['Quotes'])
                cols = ['Date','Last','PreviousClose','PercentChange','OpenInterest','Volume']    
                df = df[cols]
                return (df)
        else:
            return  None
    



if __name__ == '__main__':
	mkt = MarketData()
	q = mkt.get_future_quote('KC',12,2016)
	print(q)
