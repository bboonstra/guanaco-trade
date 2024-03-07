from datetime import datetime, timedelta

import pytz


class MarketClock:
    def __init__(self):
        pass

    @staticmethod
    def market_open():
        # Get the current time in UTC
        now = datetime.now(pytz.timezone('UTC'))

        # Define the market open hours in UTC
        market_open_start = now.replace(hour=14, minute=30, second=0, microsecond=0)
        market_open_end = now.replace(hour=21, minute=0, second=0, microsecond=0)

        # Check if it's a weekday and within market hours
        return (market_open_start <= now <= market_open_end) and now.weekday() < 5

    @staticmethod
    def seconds_to_next_market_open():
        # Get the current time in UTC
        now = datetime.now(pytz.timezone('UTC'))
        # Check if it's a weekend
        if now.weekday() >= 5:  # 5 and 6 are Saturday and Sunday
            # Calculate the next market open time on the next weekday
            days_ahead = (7 - now.weekday()) + 1  # Number of days until the next weekday
            next_market_open = now + timedelta(days=days_ahead)
            next_market_open = next_market_open.replace(hour=14, minute=30, second=0, microsecond=0)
        else:
            # It's a weekday, calculate the next market open time for today or tomorrow
            if now.hour < 14 or (now.hour == 14 and now.minute < 30):
                # If it's before 8:30, the next market open is today at 14:30
                next_market_open = now.replace(hour=14, minute=30, second=0, microsecond=0)
            else:
                # If it's after 14:30, the next market open is tomorrow at 14:30
                next_market_open = now + timedelta(days=1)
                next_market_open = next_market_open.replace(hour=14, minute=30, second=0, microsecond=0)

        # Calculate the time difference in seconds
        time_difference = next_market_open - now
        time_remaining = time_difference.total_seconds()

        return time_remaining
