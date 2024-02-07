import logging
import shutil
import sqlite3
from pathlib import Path
from sqlite3 import Connection, Cursor
from typing import Final
from zipfile import ZipFile, ZipInfo

from ios_unf.fs.backup_file import BackupFile


#TODO: Add option to input a zipfile
class ManifestDB:
    ZIP_FILE_NAME: Final[str] = "UNF_Backup.zip"

    def __init__(self, file_path: Path) -> None:
        """
        Open the manifest.db file and create the BackupFile objects.
        They can be processed later.

        Args:
            file_path (Path): Path to the manifest.db file

        Raises:
            RuntimeError: If the manifest.db file is not a valid sqlite database.
        """
        manifest_db_connection: Connection = sqlite3.connect(str(file_path))
        db_cursor: Cursor = manifest_db_connection.cursor()

        logging.debug("Connected to manifest.db")
        sql_query: str = "select fileID, domain, relativePath, file, flags from Files"
        logging.debug("Connected OK. Running SQL..")
        try:
            db_cursor.execute(sql_query)
        except sqlite3.DatabaseError as e:
            logging.critical("manifest.db is not a sqlite database; possibly encrypted.")
            raise RuntimeError from e

        self.__file_list: dict[str, BackupFile] = {}
        file_info: tuple[str, str, str, bytes, int]
        for file_info in db_cursor.fetchall():
            is_dir: bool = file_info[4] == 2

            backup_file = BackupFile(file_id=file_info[0],
                                     domain=file_info[1],
                                     relative_path=file_info[2],
                                     file_meta=file_info[3],
                                     is_dir=is_dir)
            self.__file_list[backup_file.file_id] = backup_file

        logging.debug("SQL complete. %d entries found and objects added.", len(self.__file_list))

        manifest_db_connection.close()

        logging.info("%d entries found in manifest.db", len(self.__file_list))

    def process_file_list(self, input_root: Path, output_root: Path) -> None:
        """
        For each file, reads the file content then writes to a new file in the right "path".
        v1: use domain as top level folder.

        Args:
            input_root (Path): Input directory
            output_root (Path): Output directory
        """
        backup_file: BackupFile
        for backup_file in self.__file_list.values():
            # logging.debug(f"{backup_id}: {backup_file.relative_path}")
            if backup_file.is_dir:
                self.__create_directory(backup_file, output_root)
            else:
                self.__create_file(backup_file, input_root, output_root)


    def process_into_zip(self, input_root: Path, output_root: Path) -> None:
        """
        Creates a zip file in the root of output_root and writes all data into it.

        Args:
            input_root (Path): Input directory
            output_root (Path): Output directory
        """
        output_path: Path = output_root / ManifestDB.ZIP_FILE_NAME

        new_zip: ZipFile
        with ZipFile(output_path, "w") as new_zip:
            backup_file: BackupFile
            for backup_file in self.__file_list.values():
                if not backup_file.is_dir:
                    zinfo: ZipInfo = backup_file.get_zipinfo()

                    data = self.__get_file_data(backup_file, input_root)
                    if data is None:
                        logging.warning("Unable to find data: %s (%s)",
                                        backup_file.file_id,
                                        backup_file.relative_path)
                        continue

                    new_zip.writestr(zinfo, data)

    def __create_directory(self, backup_file: BackupFile, output_root: Path) -> None:
        """
        Creates a directory

        Args:
            backup_file (BackupFile): BackupFile object
            output_root (Path): Output directory root
        """
        full_output_path: Path = self.__get_output_path(backup_file, output_root)
        # logging.debug(f"{full_output_path}")
        full_output_path.mkdir(parents=True, exist_ok=True)


    def __create_file(self, backup_file: BackupFile, input_root: Path, output_root: Path) -> None:
        """
        Creates a file in our output folder, copied from our input folder.

        Args:
            backup_file (BackupFile): BackupFile object
            input_root (Path): Input directory root
            output_root (Path): Output directory root
        """
        input_path: Path | None = self.__get_input_path(backup_file, input_root)
        if input_path is None:
            logging.warning("Missing file: %s (%s)",
                            backup_file.file_id,
                            backup_file.relative_path)
            return

        output_path: Path = self.__get_output_path(backup_file, output_root)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copyfile(input_path, output_path)

    def __get_input_path(self, backup_file: BackupFile, input_root: Path) -> Path | None:
        """
        Gets our input path.

        Args:
            backup_file (BackupFile): BackupFile object
            input_root (Path): Input directory root

        Returns:
            Path | None: The actual file path. Or None if the file was not found.
        """
        # Case where backup files are in the same folder as manifest.db
        full_input_path: Path = input_root / backup_file.file_id
        if full_input_path.exists():
            return full_input_path

        # Case where backup files exist in subdirectories
        sub_folder_name: str = backup_file.file_id[:2]
        full_input_path = input_root / sub_folder_name / backup_file.file_id
        if full_input_path.exists():
            return full_input_path

        # Otherwise we have no file!
        return None


    def __get_output_path(self, backup_file: BackupFile, output_root: Path) -> Path:
        """
        Generates for us a full path for our data

        Args:
            backup_file (BackupFile): BackupFile object
            output_root (Path): Output directory root

        Returns:
            Path: The full path
        """
        return output_root / backup_file.translated_path()


    def __get_file_data(self, backup_file: BackupFile, input_root: Path) -> bytes | None:
        """
        Returns file data

        Args:
            backup_file (BackupFile): BackupFile object
            input_root (Path): Input directory root

        Returns:
            bytes | None: File data. Or None if the file was not found.
        """
        input_path: Path | None = self.__get_input_path(backup_file, input_root)
        if input_path is None:
            logging.warning("Missing file: %s (%s)",
                            backup_file.file_id,
                            backup_file.relative_path)
            return None

        file_data: bytes
        with open(input_path, 'rb') as f:
            file_data = f.read()

        return file_data
