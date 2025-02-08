"""
Keep a record of all occurrences of a specific event during the day.

Create a plot with all occurrences with the date on the x-axis and
the hour of the day on the y-axis. The top x-axis represents the total
number of occurrences that day.

The script is meant to run in the background. It checks for a FileModifiedEvent for
the file holding the metrics data.

This is a generic script that reads from a YAML file with the following structure:

    watch_path: <folder that contains the file(s) to watch>

    data:
        <YYYY-MM-DD>: ['HH:MM', 'HH:MM', ...]
        <YYYY-MM-DD>: ['HH:MM', 'HH:MM', ...]

The YAML file path shall be passed as an argument.

Usage:

    $ nohup python scatter/metrics/generic/occurrences.py <YAML path> &

    If you want to log the output, add the following:

    $ nohup python scatter/metrics/generic/occurrences.py <YAML path> 1> ~/occurrences.log 2>&1 &

"""

from pathlib import Path
import time
import datetime
import sys
import rich
import queue

from watchdog.events import FileSystemEvent
from watchdog.events import FileSystemEventHandler
from watchdog.events import FileModifiedEvent
from watchdog.observers import Observer

import pandas as pd
from ruamel import yaml

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FixedLocator, FixedFormatter, MultipleLocator, MaxNLocator

HERE = Path(__file__).parent
YAML_PATH = HERE / "occurrences.yaml"

# The following variables will be overwritten with entries from the YAML file.

WATCH_PATH = HERE
PNG_PATH = HERE
PNG_FILE = "occurrences.png"

FIG_TITLE = "Event occurrences during the day"
TOP_AXIS_LABEL = "Occurrences in the day"


def set_fig_title(data: dict):
    global FIG_TITLE

    FIG_TITLE = data.get("title", FIG_TITLE)


def set_top_axis_label(data: dict):
    global TOP_AXIS_LABEL

    TOP_AXIS_LABEL = data.get("top_axis_label", TOP_AXIS_LABEL)


def set_watch_path(data: dict):
    global WATCH_PATH

    watch_path = data.get("watch_path", "__here__")

    if watch_path == "__here__":
        WATCH_PATH = YAML_PATH.parent
    else:
        WATCH_PATH = Path(watch_path)


def set_png_path(data: dict):
    global PNG_PATH

    png_path = data.get("png_path", "__here__")

    if png_path == "__here__":
        PNG_PATH = YAML_PATH.parent
    else:
        PNG_PATH = Path(png_path)


def set_png_file(data: dict):
    global PNG_FILE

    PNG_FILE = data.get("png_file", PNG_FILE)


def set_global_variables(data: dict):
    set_watch_path(data)
    set_png_path(data)
    set_png_file(data)
    set_fig_title(data)
    set_top_axis_label(data)

    # rich.print({
    #     'YAML_PATH': YAML_PATH,
    #     'WATCH_PATH': WATCH_PATH,
    #     'PNG_PATH': PNG_PATH,
    #     'PNG_FILE': PNG_FILE,
    #     'FIG_TITLE': FIG_TITLE,
    # })


def read_data():
    with open(YAML_PATH) as fd:
        yaml_file = yaml.YAML(typ="safe")
        data = yaml_file.load(fd)

    set_global_variables(data)

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(
        [
            (date, time)
            for date, times_list in data["data"].items()
            for time in times_list
        ],
        columns=["date", "time"],
    )

    return df


def create_plot(timestamp):
    try:
        df = read_data()
    except yaml.scanner.ScannerError:
        rich.print(f"[red]ERROR: Error while scanning {YAML_PATH}[/]")
        return

    # Convert date and time columns to datetime
    df["date"] = pd.to_datetime(df["date"])
    df["time"] = pd.to_datetime(df["time"], format="%H:%M").dt.time

    # Convert datetime objects to numerical values
    df["date_numeric"] = mdates.date2num(df["date"])

    # Convert time to a numeric format (minutes since midnight)
    df["time_numeric"] = df["time"].apply(lambda x: x.hour * 60 + x.minute) / 60.0

    # Plot occurrences
    # fig, ax1 = plt.subplots(figsize=(10, 6))
    fig, (ax3, ax1) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 4]}, sharex=True, figsize=(10, 8))

    fig.suptitle(FIG_TITLE, fontsize=16)

    # FixedFomatter shall be used with FixedLocator, the locations shall be in the units of the axis, i.e. numeric datetime.
    fixed_locations = mdates.date2num(df["date"].unique())
    fixed_labels = df["date"].astype(str).unique().tolist()

    # Calculate total occurrences per day
    occurrences_per_day = df["date"].value_counts().sort_index()

    ax3.plot(
        fixed_locations, occurrences_per_day, color="blue", alpha=0.4, linestyle='-', marker='.', markersize=7, label="Counts"
    )

    ax3.set_ylabel("Aantal")
    ax3.set_ylim(0, 20)

    y_ticks = [0, 5, 10, 15, 20]
    y_tick_labels = ['0', '5', '10', '15', '20']

    ax3.yaxis.set_major_locator(FixedLocator(y_ticks))
    ax3.yaxis.set_major_formatter(FixedFormatter(y_tick_labels))

    ax3.yaxis.set_minor_locator(FixedLocator(range(20)))

    # Remove ticks from the bottom x-axis
    ax3.tick_params(axis='x', which='both', bottom=False, top=False, length=0, labelbottom=False)

    ax3.grid(True)


    ax1.scatter(df["date_numeric"], df["time_numeric"], color="blue")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Time (hour)")
    ax1.grid(True)
    # ax1.yaxis.grid(which='minor', color='whitesmoke', linestyle='-', linewidth=1)

    # Define the ticks on the bottom x-axis

    # 1. Set fixed x-axis ticks each day (this gets very crowded with many days)

    # ax1.xaxis.set_major_locator(FixedLocator(fixed_locations))
    # ax1.xaxis.set_major_formatter(FixedFormatter(fixed_labels))

    # 2. Use AutoDateLocator and ConciseDateFormatter for the x-axis with a maximum of 20 ticks

    locator = mdates.AutoDateLocator(minticks=5, maxticks=20)
    formatter = mdates.ConciseDateFormatter(locator)
    ax1.xaxis.set_major_locator(locator)
    ax1.xaxis.set_major_formatter(formatter)

    # Add darker background for the 'night' part (e.g., from 22:00 to 08:00)
    night_start = 22  # 22:00 in the evening
    night_end = 8  # 08:00 in the morning

    ax1.axhspan(
        night_start, 24, facecolor="gray", alpha=0.3
    )  # Night from 18:00 to midnight
    ax1.axhspan(
        0, night_end, facecolor="gray", alpha=0.3
    )  # Night from midnight to 06:00

    # Set y-axis limits from 0 to 24 hours
    ax1.set_ylim(0, 24)

    # Set fixed y-axis ticks at [0, 8, 12, 18, 22, 24] hours
    y_ticks = [0, 4, 8, 12, 16, 20, 24]
    y_tick_labels = ["0", "4", "8", "12", "16", "20", "24"]
    # plt.yticks(y_ticks, y_tick_labels)

    ax1.yaxis.set_major_locator(FixedLocator(y_ticks))
    ax1.yaxis.set_major_formatter(FixedFormatter(y_tick_labels))

    ax1.yaxis.set_minor_locator(FixedLocator(range(24)))

    # Add a second x-axis at the top with the occurrence per day as major ticks
    ax2 = ax3.twiny()
    ax2.set_xlim(ax3.get_xlim())
    ax2.set_xticks(fixed_locations)
    ax2.set_xticklabels(occurrences_per_day.values)

    # Set font size for the major ticks
    ax2.tick_params(axis="x", which="major", labelsize=10)

    # An alternative way to set the fontsize for each major tick label individually.
    #
    # for tick in ax2.xaxis.get_major_ticks():
    #     # specify integer or one of preset strings, e.g. small, x-small, ...
    #     tick.label2.set_fontsize(10)
    #     # tick.label2.set_fontsize("small")
    #     tick.label2.set_rotation("horizontal")

    ax2.set_xlabel(TOP_AXIS_LABEL)

    plt.tight_layout(rect=[0, 0, 1, 1])

    rich.print(f"{timestamp} Creating occurrences plot at {PNG_PATH / PNG_FILE}")
    plt.savefig(PNG_PATH / PNG_FILE)

    plt.close()


class MyEventHandler(FileSystemEventHandler):
    def __init__(self, trigger: queue.Queue):
        self.last_occurrence = time.time()
        self.trigger = trigger
        self.watch_file = YAML_PATH.name

    def on_any_event(self, event: FileSystemEvent) -> None:
        if isinstance(event, FileModifiedEvent):
            # rich.print(f"{event.src_path = }, {self.watch_file = }")
            if event.src_path.endswith(self.watch_file):
                if time.time() - self.last_occurrence > 5.0:
                    self.last_occurrence = time.time()
                    # rich.print(datetime.datetime.fromtimestamp(self.last_occurrence), event)
                    self.trigger.put(
                        (
                            datetime.datetime.fromtimestamp(self.last_occurrence),
                            event.src_path,
                        )
                    )


def main():
    global YAML_PATH

    YAML_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else YAML_PATH

    # First time run, create the plot

    create_plot(datetime.datetime.now())

    trigger_queue = queue.Queue()

    event_handler = MyEventHandler(trigger=trigger_queue)
    observer = Observer()
    observer.schedule(event_handler, WATCH_PATH, recursive=False)
    observer.start()

    try:
        while True:
            try:
                timestamp, src_path = trigger_queue.get(timeout=1)
                create_plot(timestamp)
            except queue.Empty:
                pass
            except KeyboardInterrupt:
                rich.print("Caught a KeyboardInterrupt: Terminating..")
                break
            except Exception as exc:
                rich.print(f"[red]Caught exception: {exc.__class__.__name__}, {exc}[/]")
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
