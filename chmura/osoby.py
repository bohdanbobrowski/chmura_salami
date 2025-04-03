import argparse

import pandas as pd


def chmura_osoby(file_name: str):
    workbook = pd.read_excel(file_name)
    workbook.head()


def main():
    parser = argparse.ArgumentParser(prog="chmura_osoby", description="Chmura Osoby")
    parser.add_argument("file_name", type=str, help="Nazwa pliku")
    args = parser.parse_args()
    chmura_osoby(args.file_name)


if __name__ == "__main__":
    main()
