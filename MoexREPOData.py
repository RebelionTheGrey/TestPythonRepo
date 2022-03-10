import requests

import apimoex
import pandas as pd
import datetime

import numpy as np
import warnings
import riskfolio as rp


from apimoex import get_market_history
from datetime import date
import matplotlib.pyplot as plt


def GetMoexSecuritySectionInfo(indexes):

    request = ('https://iss.moex.com/iss/securities.json?q=MOEX')
    arguments = {'securities.columns': ()}

    with requests.Session() as session:
        response = apimoex.ISSClient(session, request, arguments)
        rawSecuritiesData = response.get()

        securitiesDataFrame = pd.DataFrame(rawSecuritiesData['securities'])

    return securitiesDataFrame[securitiesDataFrame['secid'].isin(indexes)][['secid']] if indexes != None else securitiesDataFrame[securitiesDataFrame['secid']]

def GetSecurityInfo(security, cols):

    request = "https://iss.moex.com/iss/securities/{0}.json".format(security)
    arguments = {'securities.columns': ()}

    with requests.Session() as session:

        response = apimoex.ISSClient(session, request, arguments)

        rawSecurityInfo = response.get()
        securityInfo = pd.DataFrame(rawSecurityInfo['boards'])

    return securityInfo[cols] if cols != None else securityInfo

def GetEODHistoricalData(security, engine, market, dateFrom, dateTo):

    with requests.Session() as session:

        securityHistoricalData = get_market_history(session = session, security = security, market = market,
                                                    engine = engine, start = dateFrom, end = dateTo, columns = None)

        return pd.DataFrame(securityHistoricalData)

if __name__ == '__main__':

    indexes = ['MCFTR', 'RGBITR', 'RUCBITR']
    securityColumns = ['engine', 'market']

    securityHistoryDict = {}
    EODCloseHistoryDict = {}

    securitiesId = GetMoexSecuritySectionInfo(indexes)

    for index, security in securitiesId.iterrows():

        currentSecurity = security['secid']
        securityInfo = GetSecurityInfo(currentSecurity, securityColumns)

        market = securityInfo.loc[0, 'market']
        engine = securityInfo.loc[0, 'engine']

        historicalData = GetEODHistoricalData(currentSecurity, engine,
                                              market, date(2010, 1, 1), date(2021, 12, 31))

        securityHistoryDict[currentSecurity] = historicalData[['TRADEDATE', 'SHORTNAME', 'CLOSE', 'OPEN', 'HIGH', 'LOW', 'VALUE']]

        EODCloseHistoryDict[currentSecurity] = historicalData[['TRADEDATE', 'CLOSE']]
        EODCloseHistoryDict[currentSecurity].columns = ['Date', currentSecurity]
        EODCloseHistoryDict[currentSecurity] = EODCloseHistoryDict[currentSecurity].set_index('Date')

    mergedData = pd.concat([security for security in EODCloseHistoryDict.values()], 1).dropna()




    pd.options.display.float_format = '{:.4%}'.format
    totalReturns = mergedData.pct_change().dropna()
