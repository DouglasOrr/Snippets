import datetime
import re
import sys


def read_date(line):
    if line == '🇺🇸':
        return '2019-07-04'
    m = re.search('^\d{1,2} \w+', line)
    if not m:
        raise ValueError('No date at start of line')
    d = datetime.datetime.strptime(m.group(0), '%d %B')
    return datetime.date(2019, d.month, d.day).strftime('%Y-%m-%d')


class Monitor:
    def __init__(self, volume_path, sick_path):
        self._date = None
        self._max_volume = None
        self._volume_f = open(volume_path, 'w')
        self._volume_f.write('date,volume\n')
        self._sick_f = open(sick_path, 'w')
        self._sick_f.write('date,time\n')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._flush_volume()
        self._volume_f.close()
        self._sick_f.close()

    def _flush_volume(self):
        if self._date:
            if self._max_volume:
                self._volume_f.write(f'{self._date},{self._max_volume}\n')
            else:
                raise ValueError(f'No volume for {self._date}')
        self._date = None

    def set_date(self, date):
        self._flush_volume()
        self._date = date
        self._max_volume = None

    def update_volume(self, volume):
        self._max_volume = volume

    def add_sick(self, time):
        self._sick_f.write(f'{self._date},{time or ""}\n')


def convert(data_dir):
    with open(f'{data_dir}/milks_and_sicks.txt', encoding='utf-8-sig') as f, \
         Monitor(f'{data_dir}/volume.csv', f'{data_dir}/sick.csv') as monitor:
        for line in f:
            line = line.strip()
            if line:
                try:
                    monitor.set_date(read_date(line))
                except ValueError:
                    matched = False
                    m = re.search(r'\[(\d{1,4})(\.\d)?\]', line)
                    if m:
                        monitor.update_volume(int(m.group(1)))
                        matched = True
                    m = re.search(r'([0-9]{4})?.*\b([sS]icks?|[vV]om(|med|s))\b', line)
                    if m:
                        monitor.add_sick(m.group(1))
                        matched = True
                    if not matched:
                        sys.stderr.write(f'! {line}\n')
