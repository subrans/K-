import requests

import munch
import datetime
import fractions

import loguru

# 取得個股日成交資訊（編號、年、月）
def getStockData(resp_type, stockNumber, y, m):
    response=requests.get(f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response={resp_type}&date={y}{m}01&stockNo={stockNumber}')
    
    if response.status_code !=200:
        loguru.logger.error(f'status is not success({response.status_code})')
        return None
    
    stockInfo = None    
    if resp_type == 'json':
        stockInfo = response.json()
    if resp_type == 'csv':
        stockInfo = response.text
    return stockInfo
    
# 轉換 json & csv
def convertData(resp_type, stockInfo):
      
    if resp_type == 'json':
        stock_data = munch.munchify(stockInfo).data
    
    if resp_type == 'csv':
        data = stockInfo.split('\r\n')[2:-6]
        stock_data = list(csv.reader(data))
    
    # stock_data 取得資訊 
    # 日期、開盤價、最高價、最低價、收盤價、成交量
    stock_summary = [
        [data[0], data[3], data[4], data[5], data[6], data[8]]
        for data in stock_data
    ]
    return stock_summary

# 時間格式轉換
def convertDate(date):
    date = [
        int(part)
        for part in date.split('/')
    ]
    date[0] += 1911
    return datetime.date(date[0], date[1], date[2])

def getStockDailySummary(resp_type, stockNumber, y, m):
    result = []
    stockInfo = getStockData(resp_type, stockNumber, y, m)
    
    if stockInfo is None:
        loguru.logger.error('No stock data found')
        return
    
    stock_summary = convertData(resp_type, stockInfo)
    for data in stock_summary:
        result.append(munch.munchify({
            'date': convertDate(data[0]),
            'open':fractions.Fraction(data[1]),
            'high':fractions.Fraction(data[2]),
            'low':fractions.Fraction(data[3]),
            'close': fractions.Fraction(data[4]),
            'turnover': int(data[5].replace(',', ''))
        }))
    return result

if __name__=='__main__':
    result = getStockDailySummary('json', '2308', '2020', '07')
    loguru.logger.add(
        f'{datetime.date.today():%Y%m%d}.log',
        rotation='1 day',
        retention='7 days',
        level='DEBUG'
    )
    loguru.logger.info(result)

