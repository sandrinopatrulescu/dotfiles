#!/usr/bin/env python3


import csv
import os
import sys
from collections import defaultdict
from datetime import datetime

TIME_FORMAT = "%H:%M"


def parse_time_range(time_range):
    start_str, end_str = time_range.strip().split(" - ")
    start = datetime.strptime(start_str, TIME_FORMAT)
    end = datetime.strptime(end_str, TIME_FORMAT)
    return start_str, end_str, start, end


def compute_diff_minutes(start, end):
    delta = end - start
    return int(delta.total_seconds() // 60)


def format_hours_minutes(total_minutes):
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}h{minutes:02d}m"


def generate_output_filename(input_file):
    base_name = os.path.basename(input_file)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}.{timestamp}.csv"


def main():
    if len(sys.argv) != 2:
        print("Usage: python time_diff.py <input_csv>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = generate_output_filename(input_file)

    total_minutes_sum = 0
    task_totals = defaultdict(int)
    task_earliest = {}
    rows = []

    with open(input_file, "r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 2:
                continue

            time_range = row[0].strip()
            task_name = row[1].strip()

            start_str, end_str, start, end = parse_time_range(time_range)
            diff_minutes = compute_diff_minutes(start, end)
            formatted = format_hours_minutes(diff_minutes)

            total_minutes_sum += diff_minutes
            task_totals[task_name] += diff_minutes

            # Track earliest start per task
            if task_name not in task_earliest or start < task_earliest[task_name]:
                task_earliest[task_name] = start

            rows.append([
                f"{start_str} - {end_str}",
                task_name,
                diff_minutes,
                formatted
            ])

    total_formatted = format_hours_minutes(total_minutes_sum)

    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Main table
        writer.writerow(["Original", "Task", "Minutes", "Hours_Minutes"])

        # Detail rows
        for row in rows:
            writer.writerow(row)

        # Overall total
        writer.writerow([])
        writer.writerow(["TOTAL", "", total_minutes_sum, total_formatted])

        # Blank line before per-task
        writer.writerow([])

        # Per-task table sorted by earliest time
        sorted_tasks = sorted(task_totals.keys(), key=lambda t: task_earliest[t])
        pad_width = len(str(len(sorted_tasks)))

        for idx, task in enumerate(sorted_tasks, start=1):
            minutes = task_totals[task]
            entry_number = str(idx).zfill(pad_width)

            writer.writerow([
                entry_number,
                "<intentionally left blank>",
                minutes,
                format_hours_minutes(minutes),
                task
            ])

    print(f"Output written to: {output_file}")


if __name__ == "__main__":
    main()
