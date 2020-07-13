import datetime

import loguru
import sqlalchemy
import sqlalchemy.ext.automap
import sqlalchemy.orm
import sqlalchemy.schema

def main():
    username = 'root'     # 資料庫帳號
    password = 'root'     # 資料庫密碼
    host = 'localhost'    # 資料庫位址
    port = '3307'         # 資料庫埠號
    database = 'stocks'   # 資料庫名稱
    # 建立連線引擎
    engine = sqlalchemy.create_engine(
        f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
    )
    # 取得資料庫元資料
    metadata = sqlalchemy.schema.MetaData(engine)
    # 產生自動對應參照
    automap = sqlalchemy.ext.automap.automap_base()
    automap.prepare(engine, reflect=True)
    # 準備 ORM 連線
    session = sqlalchemy.orm.Session(engine)

    # 載入 stocks 資料表資訊
    sqlalchemy.Table('stock_index', metadata, autoload=True)
    # 取出對應 stocks 資料表的類別
    Stock = automap.classes['stock_index']

    try:
        # 執行原生 SQL 命令清空資料庫
        session.execute('TRUNCATE TABLE stocks')
        # 送出執行命令
        session.commit()
    except Exception as e:
        # 發生例外錯誤，還原交易
        session.rollback()
        loguru.logger.error('清空資料失敗')

    # 進入交易模式
    try:
        # 建立第一筆資料
        stock = Stock()
        stock.code = '2344'
        stock.name = '華邦電'
        session.add(stock)

        # 建立第二筆資料
        stock = Stock()
        stock.code = '2308'
        stock.name = '台達電'
        session.add(stock)

        # 建立第三筆資料
        stock = Stock()
        stock.code = '2454'
        stock.name = '聯發科'
        session.add(stock)


        # 寫入資料庫
        session.commit()

    # 發生例外錯誤，還原交易    
    except Exception as e:
        session.rollback()
        loguru.logger.error('新增資料失敗')
        loguru.logger.error(e)

    # 關閉連線
    session.close()

if __name__ == '__main__':
    loguru.logger.add(
        f'{datetime.date.today():%Y%m%d}.log',
        rotation='1 day',
        retention='7 days',
        level='DEBUG'
    )
    main()