import time
import random
import datetime


def sleep_randomish(refresh_rate, variance=0.2):
    # We add/substract randomly 20% (default) from target refresh rate
    # in order to try to prevent patttern recognition
    random_variance = random_time(refresh_rate, variance)
    next_refresh = refresh_rate + random_variance
    print(f"Sleeping for {next_refresh}s...")
    time.sleep(next_refresh)


def random_time(seconds=1, variance=0.2):
    varianace_seconds = int(seconds * variance)
    generated_time = random.randint(1, varianace_seconds)
    return generated_time
