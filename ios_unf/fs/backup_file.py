import plistlib
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path
from time import struct_time
from zipfile import ZipInfo

from ios_unf.cclgroupltd import ccl_bplist
from ios_unf.const.domains import DOMAIN_TRANSLATION


@dataclass
class BackupFile:
    file_id: str
    domain: str
    relative_path: str
    file_meta: bytes
    is_dir: bool

    def translated_path(self) -> Path:
        domain: str
        package_name: str
        try:
            domain, package_name = self.domain.split("-", 1)
        except ValueError:
            domain = self.domain
            package_name = ""

        domain_subdir: Path
        if domain in DOMAIN_TRANSLATION:
            domain_subdir = DOMAIN_TRANSLATION[domain] / package_name
        else:
            domain_subdir = Path(domain) / package_name

        true_path: Path = domain_subdir / self.relative_path

        # normalize path and convert it back to Path(); did not found a better way
        return true_path.resolve()

    def get_mod_time(self) -> struct_time:
        """
        Reads file_meta plist and returns modified date
        :return:
        """
        file_meta_plist: dict
        if self.file_meta[:2] == b'bp':
            file_meta_plist = ccl_bplist.load(BytesIO(self.file_meta))
            raw_date_time: float = file_meta_plist['$objects'][1]['LastModified']
            converted_time: datetime = datetime.fromtimestamp(raw_date_time)
            return converted_time.timetuple()

        file_meta_plist = plistlib.loads(self.file_meta)
        return file_meta_plist['modified'].timetuple()

    def get_size(self) -> int:
        """
        Reads file_meta plist and returns reported file size
        :return:
        """
        file_meta_plist: dict
        if self.file_meta[:2] == b'bp':
            file_meta_plist = ccl_bplist.load(BytesIO(self.file_meta))
            return file_meta_plist['$objects'][1]['Size']

        file_meta_plist = plistlib.loads(self.file_meta)
        return file_meta_plist['size']

    def get_zipinfo(self) -> ZipInfo:
        """
        Generates and returns a zipinfo object. Used for zipfile output.
        :return:
        """
        zipinfo: ZipInfo = ZipInfo()
        zipinfo.filename = str(self.translated_path())
        zipinfo.date_time = self.get_mod_time()[0:6]
        zipinfo.file_size = self.get_size()

        return zipinfo
