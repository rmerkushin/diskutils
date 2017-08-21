import abc
import csv
import json
import math
import argparse
import platform
import subprocess
from typing import List, Union
from collections import namedtuple

Device = namedtuple('Device', ('index', 'name', 'alias', 'size'))
Partition = namedtuple('Partition', ('name', 'size'))


def pretty_print(items: List[Union[Device, Partition]], title: str) -> None:
    """
    Выводит на печать отформатированный список элементов
    """
    row_format = '{0:{1}} {2:{3}}'
    i_length = len(items)
    m_name = len(max(i.name for i in items))
    m_size = len(max(i.size for i in items))
    print(f'{title}:')
    for idx, item in enumerate(items, 0):
        row = row_format.format(item.name, m_name, item.size, m_size)
        if idx < i_length - 1:
            print(f'├──{row}')
        else:
            print(f'└──{row}')


class DiskUtils(abc.ABC):

    def _convert_size(self, size: str) -> str:
        """
        Конвертирет размер в байтах в человекочитаемый формат
        """
        i_size = int(size)
        if i_size == 0:
            return '0B'
        size_name = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
        i = int(math.floor(math.log(i_size, 1024)))
        p = math.pow(1024, i)
        s = round(i_size / p, 2)
        return f'{s} {size_name[i]}'

    @abc.abstractmethod
    def get_devices(self) -> List[Device]:
        """
        Возвращает список HDD и их размеров
        """

    @abc.abstractmethod
    def get_device_partitions(self, device: Device) -> List[Partition]:
        """
        Возвращает список разделов и их размеры для указанного HDD
        """


class WindowsDiskUtils(DiskUtils):

    def get_devices(self) -> List[Device]:
        cmd = 'wmic diskdrive get Index,Name,Model,Size /translate:nocomma /format:csv'
        result = subprocess.run(cmd.split(), stdout=subprocess.PIPE, check=True, encoding='cp866')
        devices = csv.DictReader(result.stdout.strip().splitlines())
        s_devices = sorted(devices, key=lambda k: k['Index'])
        return [Device(d['Index'], d['Model'], d['Name'], self._convert_size(d['Size'])) for d in s_devices]

    def get_device_partitions(self, device: Device) -> List[Partition]:
        cmd = f'wmic partition where DiskIndex={device.index} get Index,Name,Size /translate:nocomma /format:csv'
        result = subprocess.run(cmd.split(), stdout=subprocess.PIPE, check=True, encoding='cp866')
        partitions = csv.DictReader(result.stdout.strip().splitlines())
        return [Partition(p['Name'].split('  ')[-1], self._convert_size(p['Size'])) for p in partitions]


class LinuxDiskUtils(DiskUtils):

    def get_devices(self) -> List[Device]:
        cmd = 'lsblk --nodeps --bytes --json --output=MODEL,NAME,SIZE'
        result = subprocess.run(cmd.split(), stdout=subprocess.PIPE, check=True, encoding='utf_8')
        devices = json.loads(result.stdout.strip())['blockdevices']
        s_devices = sorted(devices, key=lambda k: k['model'])
        return [Device(str(i), d['model'], d['name'], self._convert_size(d['size'])) for i, d in enumerate(s_devices, 0)]

    def get_device_partitions(self, device: Device) -> List[Partition]:
        cmd = f'lsblk --bytes --json --output=NAME,SIZE /dev/{device.alias}'
        result = subprocess.run(cmd.split(), stdout=subprocess.PIPE, check=True, encoding='utf_8')
        partitions = json.loads(result.stdout.strip())['blockdevices'][0]['children']
        return [Partition(p['name'], self._convert_size(p['size'])) for p in partitions]


def main():
    p = platform.system()
    if p == 'Windows':
        disk_utils = WindowsDiskUtils()
    elif p == 'Linux':
        disk_utils = LinuxDiskUtils()
    else:
        raise NotImplementedError(f'Платформа {p} не поддерживается!')
    devices = disk_utils.get_devices()
    parser = argparse.ArgumentParser('diskutils')
    parser.add_argument('index', choices=range(len(devices)), nargs='?', type=int, help='Индекс диска в системе')
    args = parser.parse_args()
    if args.index is None:
        pretty_print(devices, 'Devices')
    else:
        device = devices[args.index]
        partitions = disk_utils.get_device_partitions(device)
        pretty_print(partitions, device.name)


if __name__ == '__main__':
    main()
