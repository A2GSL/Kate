import requests
import math
import numpy as np
import pandas as pd
import datetime
import os

CLICKHOUSE_HOST = "clickhouse.db.prod.xxxxxxxxxxxxx.com:xxxx"
ETCD_HOST = "etcd.db.prod.xxxxxxxxxxxxx.com:xxxx"
MD_URL = "md.prod.xxxxxxxxxxxxx.com/api/md/pattern/"
MINIO_HOST = "minio.db.prod.xxxxxxxxxxxxx.com:xxxx"

FIELD_NAMES_DAILY = pd.read_csv(
    requests.post(
        "http://" + CLICKHOUSE_HOST,
        data="""
            select
                *
            from stock.daily_bar
            where (Symbol like '00%.SZ' or Symbol like '30%.SZ' or Symbol like '60%.SH')
                and TradingDay = '{}'
            order by TradingDay, Symbol
            limit 5
            format CSVWithNames
            """.format(
            "2020-04-30"
        ),
        auth=("readonly", ""),
        stream=True,
    ).raw,
    na_values=["\\N"],
).columns

FIELD_NAMES_MIN = pd.read_csv(
    requests.post(
        "http://" + CLICKHOUSE_HOST,
        data="""
            select
                *
            from stock.minute_bar
            order by TradingDay, Symbol
            limit 5
            format CSVWithNames
            """,
        auth=("readonly", ""),
        stream=True,
    ).raw
).columns


def get_calendar(host=ETCD_HOST):
    calendar_path = "/v2/keys/stock/calendar.csv"
    da = (
        requests.get("http://" + host + calendar_path)
        .json()["node"]["value"]
        .split("\r\n")
    )
    da = sorted(list(set([item.split(",")[0] for item in da[1:-1]])))
    return da


CALENDAR = get_calendar()


def get_symbols(
    date=None,
    form=("00%.SZ", "30%.SZ", "60%.SH"),
    etcd_host=ETCD_HOST,
    clickhouse_host=CLICKHOUSE_HOST,
):
    if date is None:
        calendar = get_calendar(etcd_host)
        date = calendar[calendar.index(datetime.date.today().strftime("%Y-%m-%d")) - 1]

    form_str = " or ".join(["Symbol like '" + item + "'" for item in form])
    sql_str = """
        select distinct
            Symbol
        from stock.symbol_date
        where TradingDay = '{}' and
            {} 
        format CSVWithNames
        """.format(
        date, form_str
    )

    da = pd.read_csv(
        requests.post(
            "http://" + clickhouse_host,
            data=sql_str,
            auth=("readonly", ""),
            stream=True,
        ).raw,
        na_values=["\\N"],
    )

    return sorted(list(da["Symbol"]))


def get_fields(
    date_start="",
    date_end="2020-12-31",
    fields=["TradingDay", "Symbol", "ClosePrice", "Volume"],
):
    return pd.read_csv(
        requests.post(
            "http://" + CLICKHOUSE_HOST,
            data="""
            select 
                {}
            from stock.daily_bar
            where (Symbol like '00%.SZ' or Symbol like '30%.SZ' or Symbol like '60%.SH')
                and TradingDay between '{}' and '{}'
            order by TradingDay, Symbol
            format CSVWithNames
            """.format(
                ",".join(fields), date_start, date_end
            ),
            auth=("readonly", ""),
            stream=True,
        ).raw,
        na_values=["\\N"],
    )


def get_minute(date_start="2020-04-30", date_end="", symbols="all"):
    if not date_end:
        date_end = date_start
    if symbols == "all":
        cond = "(Symbol like '00%.SZ' or Symbol like '30%.SZ' or Symbol like '60%.SH')"
    elif isinstance(symbols, list):
        cond = (
            "Symbol IN {}".format(tuple(symbols))
            if len(symbols) > 1
            else "Symbol = '{}'".format(symbols[0])
        )
    else:
        cond = "Symbol = '{}'".format(symbols)
    return pd.read_csv(
        requests.post(
            "http://" + CLICKHOUSE_HOST,
            data="""
            select
                *
            from stock.minute_bar
            where TradingDay between '{}' and '{}' 
                and (Time between '{}' and '{}')
                and ({})
            order by TradingDay, Time
            format CSVWithNames
            """.format(
                date_start, date_end, "09:20:00", "15:00:00", cond
            ),
            auth=("readonly", ""),
            stream=True,
        ).raw
    )


def get_panel(
    date_start="", date_end="2020-12-31", field="ClosePrice", minute_level=False
):
    if minute_level:
        if date_start != date_end and date_start:
            raise ValueError("For minute-level data, only oneday is allowed")
        df = get_minute(date_end, date_end)
        return df.set_index(["Time", "Symbol"])[field].unstack()
    df = get_fields(date_start, date_end, ["TradingDay", "Symbol"] + [field])
    return df.set_index(["TradingDay", "Symbol"])[field].unstack()


def fetch(date, field="Price"):
    field = field.lower()
    cachePath = os.path.join("/mnt/data", "data_cache", field)
    filename = "{}-{}.pkl".format(date, field)
    if filename not in os.listdir(cachePath):
        if field == "price":
            df = get_panel(date_end=date, field="Price", minute_level=True)
        elif field == "volume":
            df = get_panel(date_end=date, field="Volume", minute_level=True)
        elif field == "tradingstatus":
            df = get_panel(date, date, field="TradeStatus", minute_level=False)
        else:
            df = get_panel(date_end=date, field="Price", minute_level=True).iloc[-1, :]
        df.to_pickle(os.path.join(cachePath, filename))
    else:
        df = pd.read_pickle(os.path.join(cachePath, filename))
    return df
