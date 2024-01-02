#!/bin/bash

# Check if app env variables are set
if [ -n "${BARCODES}" ]; then
    args+=("$BARCODES")
fi

if [ -n "${ORDERS}" ]; then
    args+=("$ORDERS")
fi

if [ -n "${APP_FILE_PATH}" ]; then
    args+=("--file_path" "$APP_FILE_PATH")
fi

if [ -n "${TOP_N}" ]; then
    args+=("--top_n" "$TOP_N")
fi

if [[ -v APP_DEBUG ]]; then
    args+=("--debug")
fi


# Call main.py with or without additional arguments
if [ ${#args[@]} -gt 0 ]; then
    python ./src/main.py "${args[@]}"
else
    python ./src/main.py "$@"
fi
