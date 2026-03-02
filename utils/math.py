from config import config

def get_daily_cost(total_devices: int) -> float:
    """Твоя математика списаний"""
    if total_devices == 0:
        return 0.0
    elif total_devices <= 3:
        return config.one_day_price / 30.0
    else:
        return (config.one_day_price + (total_devices - 3) * config.additional_device_price) / 30.0