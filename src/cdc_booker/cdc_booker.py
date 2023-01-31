import traceback
import time
import json
import random
import datetime

import click
import yaml

from cdc_website import CDCWebsite, Booking_Types
from cdc_android import CDCAndroid
from cdc_notifier import CDCNotifier

from timing_randomizer import sleep_randomish, random_time


@click.command()
@click.option(
    "--telegram",
    is_flag=True,
    help="Enable telegram notifications when slots are available",
)
@click.option(
    "--road_revision",
    is_flag=True,
    help="Book road revision instead of practical class",
)
@click.option(
    "--circuit_revision",
    is_flag=True,
    help="Book circuit revision instead of practical class",
)
@click.option(
    "--scrapper", type=click.Choice(["web", "android"], case_sensitive=False)
)
@click.option("-c", "--configuration", help="Your configuration file")
@click.option("-u", "--username", help="Your CDC learner ID")
@click.option("-p", "--password", "password_", help="Your CDC password")
@click.option("--booking_type", type= click.Choice(["practical", "rr", "btt", "rtt", "pt", "simulator"]) ,help="Booking Type")
def main(
    username,
    password_,
    configuration,
    scrapper,
    circuit_revision,
    road_revision,
    telegram,
    booking_type
):
    config = {}
    if configuration is not None:
        with open(configuration, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

    username = config.get("username", username)
    password = config.get("password", password_)
    circuit_revision = config.get("circuit_revision", circuit_revision)
    road_revision = config.get("road_revision", road_revision)
    telegram = config.get("telegram", telegram)
    refresh_rate = config.get("refresh_rate", 90)
    scrapper = config.get("scrapper", "android")
    booking_type = config.get("booking_type", "simulator")

    if telegram:
        notifier = CDCNotifier(
            token=str(config.get("telegram_token", "")),
            chat_id=str(config.get("telegram_chat_id", "")),
        )
        notifier.send_message(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Vrooom vroom, starting CDC bot"
        )

    if scrapper == "web":
        cdc_website = initialize_web(username=username, password=password)
        get_website_slots(
            cdc_website,
            booking_type,
            refresh_rate=refresh_rate,
            notifier=notifier,
        )

    elif scrapper == "android":
        get_android_slots(
            username=username,
            password=password,
            circuit_revision=circuit_revision,
            road_revision=road_revision,
            refresh_rate=refresh_rate,
            notifier=notifier,
        )


def get_android_slots(
    username, password, circuit_revision, road_revision, refresh_rate, notifier
):
    cdc_android = initialize_android(username=username, password=password)

    while True:
        try:
            cdc_android.open_available_practical_lessons(
                circuit_revision=circuit_revision, road_revision=road_revision
            )
            session_count = cdc_android.get_session_available_count()
            now = datetime.datetime.now()
            print(
                f"{now.strftime('%Y-%m-%d %H:%M:%S')}: Available slots: {session_count}"
            )
            if notifier is not None:
                retries_count = 0
                print(f"session_count: {session_count}")
                if session_count > 0:
                    notifier.send_message(f"Available slots: {session_count}")
                    notifier.send_photo("cdc_screenshot.png")
                    retries_count = 0
                else:
                    print(f"retries: {retries_count}")
                    retries_count += 1
                    if retries_count > 10:
                        notifier.send_message(
                            f"I'm still alive! ({retries_count} since last message)"
                        )
                        retries_count = 0

            # we go back to the class selection
            cdc_android.go_back()

        except Exception:
            traceback.print_exc()

        # in case there are too many exceptions, we restart the emulator session
        if cdc_android.exception_count > 5:
            if notifier is not None:
                notifier.send_message(
                    f"Too many emulator exceptions ({cdc_android.exception_count}) - restarting"
                )
            cdc_android = initialize_android(username=username, password=password)
            continue

        sleep_randomish(refresh_rate)


def initialize_android(username, password):
    cdc_android = CDCAndroid(username=username, password=password)
    cdc_android.login()
    cdc_android.open_lesson_booking()
    return cdc_android


def initialize_web(username, password):
    with CDCWebsite(
        username=username,
        password=password,
        headless=False,
    ) as cdc_website:
        cdc_website.open_home_website()
        cdc_website.login()
    return cdc_website


def get_website_slots(cdc_website, refresh_rate, notifier, booking_type):

    cdc_website.open_booking_overview()
    cdc_website.open_booking(booking_type=booking_type)

    try:
        session_count = cdc_website.get_session_available_count()
        available_sessions = cdc_website.get_available_sessions()
        now = datetime.datetime.now()
        print(f"{now.strftime('%Y-%m-%d %H:%M:%S')}: Available slots: {session_count}")
        print(f"available sessions: {json.dumps(available_sessions, indent = 4)}")

        if (notifier is not None) and session_count > 0:
            notifier.send_message(f"Available slots: {session_count}")
            notifier.send_message(
                f"Available sessions: {json.dumps(available_sessions, indent = 4)}"
            )

    except Exception:
        traceback.print_exc()
    sleep_randomish(refresh_rate)


if __name__ == "__main__":
    main()
