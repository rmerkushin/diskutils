import sys
import io
import unittest
from unittest.mock import patch
from diskutils import Device, Partition, WindowsDiskUtils, LinuxDiskUtils, pretty_print


class TestDiskUtils(unittest.TestCase):

    def test_convert_size(self):
        disk_utils = WindowsDiskUtils()
        size = disk_utils._convert_size('445834592256')
        self.assertEqual(size, '415.22 GB')

    def test_pretty_print(self):
        items = [
            Partition(name='sda1', size='976.0 MB'),
            Partition(name='sda2', size='1.91 GB')
        ]
        expected = 'ST500DM002-1BD14:\n├──sda1 976.0 MB\n└──sda2 1.91 GB \n'
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        pretty_print(items, 'ST500DM002-1BD14')
        sys.stdout = sys.__stdout__
        self.assertEqual(capturedOutput.getvalue(), expected)


class TestWindowsDiskUtils(unittest.TestCase):

    disk_utils = WindowsDiskUtils()

    @patch('subprocess.run')
    def test_get_devices(self, m):
        m.return_value.stdout = """
        Node,Index,Model,Name,Size
        PROMETHEUS,1,WDC WD10EFRX-68FYTN0,PHYSICALDRIVE1,1000202273280
        PROMETHEUS,0,INTEL SSDSC2BW240A4,PHYSICALDRIVE0,240054796800
        """
        expected = [
            Device(index='0', name='INTEL SSDSC2BW240A4', alias='PHYSICALDRIVE0', size='223.57 GB'),
            Device(index='1', name='WDC WD10EFRX-68FYTN0', alias='PHYSICALDRIVE1', size='931.51 GB')
        ]
        devices = self.disk_utils.get_devices()
        self.assertEqual(devices, expected)

    @patch('subprocess.run')
    def test_get_device_partitions(self, m):
        m.return_value.stdout = """
        Node,Index,Name,Size
        PROMETHEUS,0,Disk #0  Partition #0,471859200
        PROMETHEUS,1,Disk #0  Partition #1,104857600
        PROMETHEUS,2,Disk #0  Partition #2,239462252544
        """
        device = Device(index='0', name='INTEL SSDSC2BW240A4', alias='PHYSICALDRIVE0', size='223.57 GB')
        expected = [
            Partition(name='Partition #0', size='450.0 MB'),
            Partition(name='Partition #1', size='100.0 MB'),
            Partition(name='Partition #2', size='223.02 GB')
        ]
        partitions = self.disk_utils.get_device_partitions(device)
        self.assertEqual(partitions, expected)


class TestLinuxDiskUtils(unittest.TestCase):

    disk_utils = LinuxDiskUtils()

    @patch('subprocess.run')
    def test_get_devices(self, m):
        m.return_value.stdout = """
        {
            "blockdevices": [
                {"model": "ST500DM002-1BD14", "name": "sda", "size": "500107862016"}
            ]
        }
        """
        expected = [
            Device(index='0', name='ST500DM002-1BD14', alias='sda', size='465.76 GB')
        ]
        devices = self.disk_utils.get_devices()
        self.assertEqual(devices, expected)

    @patch('subprocess.run')
    def test_get_device_partitions(self, m):
        m.return_value.stdout = """
        {
            "blockdevices": [
                {"name": "sda", "size": "500107862016",
                    "children": [
                        {"name": "sda1", "size": "1023410176"},
                        {"name": "sda2", "size": "2047868928"},
                        {"name": "sda3", "size": "51199868928"},
                        {"name": "sda4", "size": "445834592256"}
                    ]
                }
            ]
        }
        """
        device = Device(index='0', name='ST500DM002-1BD14', alias='sda', size='465.76 GB')
        expected = [
            Partition(name='sda1', size='976.0 MB'),
            Partition(name='sda2', size='1.91 GB'),
            Partition(name='sda3', size='47.68 GB'),
            Partition(name='sda4', size='415.22 GB')
        ]
        partitions = self.disk_utils.get_device_partitions(device)
        self.assertEqual(partitions, expected)


if __name__ == '__main__':
    unittest.main()
