#!/bin/bash

set -eu

run_linters() {
    set +e

    echo "Running flake8 ..."
    flake8_output=$(flake8 --config .flake8 --statistics src/)
    if [ $? -ne 0 ]; then echo "$flake8_output"; else echo "  Success!"; fi

    echo "Running mypy ..."
    mypy_output=$(mypy --config-file .mypy.ini src/)
    if [ $? -ne 0 ]; then echo "$mypy_output"; else echo "  Success!"; fi

    echo "Running pylint ..."
    pylint_output=$(pylint --rcfile .pylintrc src/)
    if [ $? -ne 0 ]; then echo "$pylint_output"; else echo "  Success!"; fi

}

run_unit_tests() {
    pytest tests/unit
}

run_help() {
    cat <<EOF
usage:
    ./dev.sh <command>

commands:
    lint                runs linters
    unit                runs unit tests
    help                shows this help
EOF
}

if [ $# -ne 1 ]; then
    echo -e "No arguments were supplied\n"
    run_help
    exit 1
fi

command="$1"
shift

case "$command" in
lint)
    run_linters
    ;;
unit)
    run_unit_tests
    ;;
help)
    run_help
    ;;
*)
    echo -e "Invalid command: $command\n"
    run_help
    ;;
esac