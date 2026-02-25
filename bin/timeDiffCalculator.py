#!/usr/bin/env python3


import csv
import os
import sys
from datetime import datetime

TIME_FORMAT = "%H:%M"


def parse_line(line):
    start_str, end_str = line.strip().split(" - ")
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
        print("Usage: python time_diff.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = generate_output_filename(input_file)

    total_minutes_sum = 0
    rows = []

    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            start_str, end_str, start, end = parse_line(line)
            diff_minutes = compute_diff_minutes(start, end)
            formatted = format_hours_minutes(diff_minutes)

            total_minutes_sum += diff_minutes

            rows.append([
                f"{start_str} - {end_str}",
                diff_minutes,
                formatted
            ])

    total_formatted = format_hours_minutes(total_minutes_sum)

    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Original", "Minutes", "Hours_Minutes"])

        for row in rows:
            writer.writerow(row)

        writer.writerow([])
        writer.writerow(["TOTAL", total_minutes_sum, total_formatted])

    print(f"Output written to: {output_file}")


if __name__ == "__main__":
    main()
