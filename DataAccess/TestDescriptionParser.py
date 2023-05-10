from Models.Test import Test
from Utils.ReverseReader import ReverseReader
import logging
import re


class TestDescriptionParser:
    def __init__(self) -> None:
        self._version = 1

    def parse(self, test: Test, fullPath: str) -> str:
        try:
            if test.is_dimm_error():
                return self.extract_error_description(fullPath)
            elif test.is_chk_serialuart_error():
                return self.extract_chk_serialuart_description(fullPath)
            else:
                return ""
        except Exception as e:
            logging.error(str(e))
            return ""

    def extract_error_description(self, fullPath: str):
        with open(fullPath, "r") as fp:
            dims: "list[str]" = []
            voltageError = None
            for l_no, line in enumerate(fp):
                if voltageError == None and self.search(
                    ".*Voltage SYS.*Deasserted.*", line
                ):
                    voltageError = line[31:].strip()
                    continue

                if self.search("Occur Memory Error at", line):
                    dims.append(self.extract_dim(line))
                    continue

            description = ""
            description = self.append(description, voltageError)

            if len(dims) > 0:
                description = self.append(
                    description, "Occur Memory Error at: " + ", ".join(list(set(dims)))
                )

            return description

    def extract_chk_serialuart_description(self, fullPath: str):
        for line in ReverseReader().reverse_readline(fullPath):
            if self.search(".*UART.*TTYUSB.*Fail.*", line):
                return line.strip()
        return ""

    def append(self, txt1, txt2):
        if txt1 == None and txt2 == None:
            return ""
        elif txt1 != None and txt2 == None:
            return txt1
        elif txt1 != None and txt2 != None:
            return txt2
        elif txt1 != None and txt2 != None:
            return txt1 + "\n" + txt2

    def search(self, pattern: str, string: str) -> bool:
        return re.search(pattern, string, re.IGNORECASE) != None

    def extract_dim(self, line: str) -> str:
        match = re.search("CPU\d+_DIMM\d+_C\d+", line)
        if match:
            return match.group(0).strip()
        return ""
