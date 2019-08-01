# Risk Lambda - practice using Google Cloud Functions to simulate Risk attacks


## Option 1 - Google Cloud Function

```bash
$ docker run --rm -it -v `pwd`:/work -w /work -p 7777:7777 google/cloud-sdk:255.0.0

# gcloud auth login
# gcloud config set project risk-lambda-2019
# gcloud functions deploy odds --runtime python37 --trigger-http
# gcloud functions delete odds

# apt install -qy python3-pip
# pip3 install -r requirements.txt
# python3 main.py
```

## Option 2 - Google Cloud Run

TODO

## Option 3 - Local Run

```bash
$ ./fetch_dependencies.sh
$ docker build --rm -t risk_serverless .
$ docker run --rm -it -v `pwd`:/work -w /work -p 7777:7777 risk_serverless python3 main.py
```
