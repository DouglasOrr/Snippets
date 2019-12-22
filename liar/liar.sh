set -e
./build.sh
docker run --rm -it -v `pwd`:/home/jovyan liar python3 liar.py "$@"
