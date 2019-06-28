#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the date formatter of the TransmartCopyWriter.
"""
from datetime import datetime, timezone, date
from dateutil.tz import gettz
from transmart_loader.copy_writer import format_date, microseconds


def test_date_serialization():
    assert format_date(
        date(2019, 6, 28)) == '2019-06-28'
    assert format_date(
        datetime(2019, 6, 28, 13, 2, 58,
                 tzinfo=timezone.utc)) == '2019-06-28 13:02:58'
    assert format_date(
        datetime(2019, 6, 28, 13, 2, 58, 12345,
                 tzinfo=timezone.utc)) == '2019-06-28 13:02:58.012345'
    assert format_date(
        datetime(2019, 6, 28, 13, 2, 58,
                 tzinfo=gettz('Europe/Amsterdam')
                 )) == '2019-06-28 11:02:58'
    assert format_date(datetime.fromtimestamp(
        microseconds(date(2019, 6, 28))/1000,
        timezone.utc)) == '2019-06-28 00:00:00'
    assert format_date(datetime.fromtimestamp(
        microseconds(datetime(2019, 6, 28, 13, 2, 58))/1000,
        timezone.utc)) == '2019-06-28 13:02:58'
