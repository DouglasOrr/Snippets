set -e
./build.sh

NAME="${USER}-liar-notebook"
docker rm -f "${NAME}" || true
docker run --name "${NAME}" -d \
       -p 8888:8888 -v `pwd`:/home/jovyan/work -w /home/jovyan/work \
       -e PYTHONPATH=/home/jovyan/work -e JUPYTER_ENABLE_LAB=yes \
       liar
sleep 8
docker logs "${NAME}"
