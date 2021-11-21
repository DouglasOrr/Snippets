PORT="${1:-8888}"
docker run --rm -it -v `pwd`:/work -w /work -p "${PORT}:${PORT}" jupyter/scipy-notebook \
       start-notebook.sh --port "${PORT}"
