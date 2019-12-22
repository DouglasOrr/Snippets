set -e
./build.sh
docker run --rm -it -v `pwd`:/home/jovyan liar pytest liar.py "$@"
docker run --rm -it -v `pwd`:/home/jovyan liar flake8 liar.py
