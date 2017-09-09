"""
Log NVIDIA GPU memory and utilization stats to statsd.
"""
import argparse
import re
import subprocess


def log_mem_and_util(hostname):
    pattern = re.compile(r'\|\s+\d+%.*\|\s+(\d+)MiB.*\s+(\d+)%.*')
    result = subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    lines = result.split('\n')
    gpu_id = 0
    for line in lines:
        match = pattern.match(line)
        if match:
            memory_mib = match.group(1)
            utilization = match.group(2)
            prefix = '{hn}.gpu.{id}.'.format(hn=hostname, id=gpu_id)
            for t in [('memory_usage_mib', memory_mib), ('utilization_pct', utilization)]:
                p1 = subprocess.Popen(['echo', '{p}{stat}:{val}|g'.format(p=prefix, stat=t[0], val=t[1])], stdout=subprocess.PIPE)
                p2 = subprocess.run(['nc', '-u', '-w0', '127.0.0.1', '8125'], stdin=p1.stdout)
            gpu_id += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser('GPU statsd logger')
    parser.add_argument('hostname', help='name of the machine')
    args = parser.parse_args()
    log_mem_and_util(args.hostname)
