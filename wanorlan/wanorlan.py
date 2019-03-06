import time
import datetime
import subprocess
import json
import sys
import re


PING_RTT_REGEX = re.compile('rtt.+=\s*([\d.]+)')


def get_status(ip, timeout):
    t0 = time.time()
    error = subprocess.call(['ping', '-c', '1', '-W', str(timeout), ip],
                            stdout=sys.stderr.fileno(),
                            stderr=sys.stderr.fileno())
    delay = time.time() - t0
    return None if error else delay


def log_status(hosts, timeout):
    now = datetime.datetime.now().isoformat(timespec='seconds')
    processes = []
    for host in hosts:
        processes.append(subprocess.Popen(
            ['ping', '-qnc', '1', '-W', str(timeout), host],
            stdout=subprocess.PIPE))
    results = dict(time=now)
    for host, process in zip(hosts, processes):
        if process.wait():
            results[host] = None
        else:
            last_line = list(process.stdout)[-1].strip().decode('utf8')
            results[host] = float(PING_RTT_REGEX.match(last_line).group(1))
    return results


TIMEOUT = 2
INTERVAL = 15
HOSTS = ['localhost', '192.168.1.1', '1.1.1.1', '8.8.8.8', 'www.google.co.uk']

if __name__ == '__main__':
    t0 = time.time()
    while True:
        time.sleep(max(0, t0 + INTERVAL - time.time()))
        t0 = time.time()
        print(json.dumps(log_status(HOSTS, timeout=TIMEOUT)), flush=True)
