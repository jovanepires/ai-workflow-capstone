#!/usr/bin/env bash

case "$1" in
  webserver)
    exec python run_data_ingestion.py && python wsgi.py
    ;;
  unittests)
    sleep 1
    exec python -m unittest unittests/*.py -vvv
    ;;
  *)
    # The command is something like bash, not an airflow subcommand. Just run it in the right environment.
    exec "$@"
    ;;
esac