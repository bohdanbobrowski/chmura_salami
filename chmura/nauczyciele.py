import argparse

import pandas as pd
from progress.bar import Bar
from pydantic import BaseModel
from pydantic_core import ValidationError


class Teacher(BaseModel):
    first_name: str | None
    second_name: str | None
    subject: str | None
    chmura: bool = False


def teachers_list(input_file_name: str, output_file_name: str):
    workbook = pd.read_excel(input_file_name, sheet_name="tabelka dla IT")
    workbook.head()
    print("")
    output = {}
    bar = Bar("Konwersja pliku xlsx:", max=len(workbook))
    cnt = 0
    for row in range(0, len(workbook)):
        bar.next()
        if row > 0:
            try:
                location = workbook["Lokalizacja"].iloc[row]
                teacher = Teacher(
                    first_name=workbook["Imię"].iloc[row],
                    second_name=workbook["Nazwisko"].iloc[row],
                    subject=workbook["Przedmiot"].iloc[row],
                    chmura=bool(workbook["Nasz"].iloc[row].lower() == "tak"),
                )
                # print(teacher.model_dump())
                cnt += 1
                if location not in output:
                    output[location] = list()
                output[location].append(teacher)
            except ValidationError:
                pass
    print("")
    print(f"Wczytano {cnt} nauczycieli.")
    with pd.ExcelWriter(output_file_name) as writer:
        for location, teachers in output.items():
            print(f"{location}: {len(teachers)}")
            data = {
                "Imię": [],
                "Nazwisko": [],
                "Nasz": [],
                "Przedmiot": [],
            }
            for t in teachers:
                data["Imię"].append(t.first_name)
                data["Nazwisko"].append(t.second_name)
                data["Nasz"].append("TAK" if t.chmura else "NIE")
                data["Przedmiot"].append(t.subject)
            data_frame = pd.DataFrame(data)
            data_frame.to_excel(writer, sheet_name=location)
    print("")
    print(f'Zapisano plik "{output_file_name}"')


def main():
    parser = argparse.ArgumentParser(
        prog="chmura_nauczyciele", description="Chmura Nauczyciele"
    )
    parser.add_argument("input", type=str, help="Nazwa pliku wejścia")
    parser.add_argument("output", type=str, help="Nazwa pliku wyjścia")
    args = parser.parse_args()
    teachers_list(args.input, args.output)


if __name__ == "__main__":
    main()
