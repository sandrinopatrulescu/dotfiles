#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 || ! -f "$1" ]]; then
    echo "Usage: $0 <file> <duration-seconds> [parallel-jobs]"
    exit 1
fi

file="$1"
duration="$2"
jobs="${3:-2}"

if [[ ! "$duration" =~ ^[0-9]+([.][0-9]+)?$ ]] ||
   ! awk -v d="$duration" 'BEGIN { exit !(d > 0) }'; then
    echo "Error: duration must be a positive number."
    exit 1
fi

if [[ ! "$jobs" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: parallel-jobs must be a positive integer."
    exit 1
fi

# Resolve input path
file=$(realpath -- "$file")

# Extract filename and extension
base=$(basename -- "$file")

if [[ "$base" != *.* || "$base" == .* ]]; then
    echo "Error: input filename must have an extension."
    exit 1
fi

ext="${base##*.}"
name="${base%.*}"

# Output directory: current working directory
outdir=$(pwd -P)

# Get video duration
total=$(ffprobe -v error \
    -show_entries format=duration \
    -of default=noprint_wrappers=1:nokey=1 \
    "$file")

if [[ ! "$total" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
    echo "Error: could not determine video duration."
    exit 1
fi

echo "Input:    $file"
echo "Duration: $total seconds"
echo "Segments: $duration seconds"
echo "Parallel: $jobs jobs"
echo "Output:   $outdir"
echo

# Create temporary directory
tmpdir=$(mktemp -d "${TMPDIR:-/tmp}/split-video.$(date +%Y-%m-%d_%H-%M-%S).XXXXXX")

trap 'printf "\nLogs: %s\n" "$tmpdir"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# Generate segment information
starts=()
lengths=()
parts=()

while read -r start segment_length part; do
    starts+=("$start")
    lengths+=("$segment_length")
    parts+=("$part")
done < <(
    awk -v total="$total" -v duration="$duration" '
        BEGIN {
            for (start = 0; start < total; start += duration) {
                segment_length = duration

                if (start + segment_length > total)
                    segment_length = total - start

                printf "%.6f %.6f %02d\n", start, segment_length, ++part
            }
        }
    '
)

count=${#parts[@]}
if (( count == 0 )); then
    echo "Error: no segments generated."
    exit 1
fi

# Check for existing output files
for part in "${parts[@]}"; do
    output="$outdir/$name.part-$part.$ext"

    if [[ -e "$output" ]]; then
        echo "Error: output already exists: $output"
        exit 1
    fi
done

echo "Generated $count segments."
echo

# Process segments in parallel batches
for ((i = 0; i < count; i += jobs)); do
    pids=()
    pid_parts=()

    batch_end=$((i + jobs))
    (( batch_end > count )) && batch_end=$count

    for ((j = i; j < batch_end; j++)); do
        part="${parts[j]}"
        start="${starts[j]}"
        length="${lengths[j]}"

        output="$name.part-$part.$ext"
        tmpoutput="$outdir/$output"
        logfile="$tmpdir/$part.log"

        echo "Starting part $part: ${start}s + ${length}s"

        ffmpeg -hide_banner -y \
            -ss "$start" \
            -i "$file" \
            -t "$length" \
            -map 0 \
            "$tmpoutput" \
            > "$logfile" 2>&1 &

        pids+=("$!")
        pid_parts+=("$part")
    done

    # Wait for all processes in this batch
    failed=0

    for ((j = 0; j < ${#pids[@]}; j++)); do
        if ! wait "${pids[j]}"; then
            echo "ERROR: part ${pid_parts[j]} failed."
            cat "$tmpdir/${pid_parts[j]}.log"
            failed=1
        fi
    done

    if (( failed )); then
        echo "Splitting failed."
        exit 1
    fi
done

echo
echo "All segments processed successfully."
echo "Created $count segments in: $outdir"
