"""
iOS Backup UNF
UNFunk iOS backups into something sensible
Assumes presence of manifest.db, and uses the files present in 'Files' table to determine path.
Also an example of dataclasses, F-strings, logging and argparse, whew
"""

import logging
import sys
from pathlib import Path

from ios_unf.cli.args import CLIArguments
from ios_unf.fs.manifest import ManifestDB


def run() -> None:
    cli_args: CLIArguments = CLIArguments()

    logging.info("-------------------")
    logging.info("iOS Backup UnFunker")
    logging.info("By Greybeard")
    logging.info("and mammo0")
    logging.info("-------------------")

    manifest_path: Path | None = next(cli_args.input_dir.glob('[Mm]anifest.db'), None)

    if (manifest_path is None or
            not manifest_path.exists()):
        logging.critical("Cannot find manifest.db at: %s", str(manifest_path))
        logging.info("Exiting..")
        sys.exit(1)

    try:
        manifest_file: ManifestDB = ManifestDB(file_path=manifest_path)
    except RuntimeError:
        logging.critical("Can't open manifest.db file.")
        logging.info("Exiting..")
        sys.exit(1)

    if cli_args.to_zip:
        logging.info("Exporting to zip file..")
        logging.info("Beginning File Conversion..")
        manifest_file.process_into_zip(input_root=cli_args.input_dir,
                                       output_root=cli_args.output_dir)
    else:
        logging.info("Exporting to filesystem..")
        logging.info("Beginning File Conversion..")
        manifest_file.process_file_list(input_root=cli_args.input_dir,
                                        output_root=cli_args.output_dir)

    logging.info("Complete. Exiting..")


if __name__ == '__main__':
    run()
