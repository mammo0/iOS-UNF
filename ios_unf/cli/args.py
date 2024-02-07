import logging
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CLIArguments:
    input_dir: Path = field(init=False)
    output_dir: Path = field(init=False)
    to_zip: bool = field(init=False)

    def __post_init__(self) -> None:
        parser: ArgumentParser = ArgumentParser(description="Unpack iOS backups")
        parser.add_argument("-z", "--zip", dest="to_zip", default=False, action="store_true",
                            help="Output to zip")
        parser.add_argument("-o", "--output", dest="output_dir", type=Path, default=Path("."),
                            help="Output directory (default: current directory)")
        parser.add_argument("input_dir", metavar="INPUT_DIR", type=Path, action="store",
                            help="Input directory")

        args: Namespace = parser.parse_args()

        self.input_dir: Path = args.input_dir.resolve(strict=True)
        self.output_dir: Path = args.output_dir.resolve(strict=True)
        self.to_zip: bool = args.to_zip

        logging.info("Input Dir:  %s", str(self.input_dir))
        logging.info("Output Dir: %s", str(self.output_dir))
