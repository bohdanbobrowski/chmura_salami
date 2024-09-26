import argparse
import json
import os.path
import sys
from datetime import datetime
from typing import Any

import pandas as pd
import xlsxwriter
from progress.bar import Bar
from pydantic import BaseModel


class Teacher(BaseModel):
    first_name: str
    second_name: str
    role: str = ""

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.second_name}"

    @property
    def name_with_role(self) -> str:
        name_with_role = f"{self.first_name} {self.second_name}"
        if self.role:
            name_with_role += f" ({self.role})"
        return name_with_role

    @property
    def sort_value(self) -> str:
        if self.role.upper() == "PRZEWODNICZĄCY":
            return "000000000"
        return self.name

    def __key(self):
        return self.first_name, self.second_name

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Teacher):
            return self.__key() == other.__key()
        return NotImplemented


class Room(BaseModel):
    name: str
    term: str
    subject: str = ""
    teachers: set[Teacher] = set()

    @property
    def row_title(self) -> str:
        row_title = self.name
        if self.term_start:
            row_title = f"{row_title} {self.term_start.strftime('%H:%M')}"
        return row_title

    @property
    def term_start(self) -> datetime | None:
        if len(self.term) > 8:
            return datetime.strptime(self.term.split(" - ")[0], "%d.%m.%y %H:%M")
        return None

    @property
    def term_end(self) -> datetime | None:
        if len(self.term) > 8:
            return datetime.strptime(
                self.term.split(" ")[0] + " " + self.term.split(" - ")[1],
                "%d.%m.%y %H:%M",
            )
        return None

    def __key(self):
        return self.name, self.term_start

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Teacher):
            return self.__key() == other.__key()
        return NotImplemented


class School(BaseModel):
    name: str
    rooms: set[Room] = set()

    @property
    def short_name(self) -> str:
        comma_index = self.name.find(",")
        if comma_index:
            short_name = self.name[:comma_index]
            if len(short_name) > 31:
                return short_name.rsplit(" ", 1)[0]
            return short_name
        return self.name

    @property
    def file_name(self) -> str:
        file_name = self.short_name
        file_name = file_name.replace(":", "")
        file_name = file_name.replace("/", "")
        file_name = file_name.replace("\\", "")
        file_name = file_name.replace(".", "")
        file_name = file_name.replace(",", "")
        return file_name

    def __key(self):
        return self.name

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Teacher):
            return self.__key() == other.__key()
        return NotImplemented


class TeacherAlreadyAddedError(Exception):
    pass


def not_in_set(in_set, in_element):
    for element in in_set:
        if element.__hash__() == in_element.__hash__():
            return False
    return True


def get_terms(workbook) -> list[str]:
    terms = list()
    for column in workbook:
        if column not in ["Imię", "Nazwisko"]:
            terms.append(column)
    return terms


def parse_field(field) -> dict | None:
    if field.lower() == "nie dotyczy":
        return None
    field_rows = field.strip().split("\n")
    field_parsed = {}
    for f_row in field_rows:
        label_index = f_row.find(":")
        field_parsed[f_row[:label_index].strip()] = f_row[label_index + 1 :].strip()
    if field_parsed:
        return field_parsed
    else:
        return None


def prevent_overwrite(file_name: str) -> str:
    exists = 0
    while os.path.isfile(file_name):
        file_name = file_name.replace(f" ({exists}).xlsx", ".xlsx")
        exists += 1
        file_name = file_name.replace(f".xlsx", f" ({exists}).xlsx")
    return file_name


def export_data_to_one_file(
    schools,
    file_name,
):
    """Pierwsza wersja eksportu - do jednego pliku."""
    print("")
    print(f"Wyeksportowano dane dla {len(schools)} placówek:")
    converted_file_name = file_name.split(".")[:-1]
    converted_file_name.append(" - SALAMI")
    converted_file_name.append(".xlsx")
    converted_file_name = "".join(converted_file_name)

    converted_file_name = prevent_overwrite(converted_file_name)

    with pd.ExcelWriter(converted_file_name) as writer:
        x = 1
        for s in schools:
            print(f"{x}. {s.short_name} ({len(s.short_name)})")
            x += 1
            data = {
                "Sala": [],
                "Termin": [],
                "Przedmiot": [],
                "Nauczyciel": [],
                "Rola": [],
            }
            for r in s.rooms:
                for t in r.teachers:
                    data["Sala"].append(r.name)
                    data["Termin"].append(r.term)
                    data["Przedmiot"].append(r.subject)
                    data["Nauczyciel"].append(t.name)
                    data["Rola"].append(t.role)
            data_frame = pd.DataFrame(data)
            data_frame.to_excel(writer, sheet_name=s.short_name)
    print("")
    print(f'Zapisano plik "{converted_file_name}"')


def _prepare_data(data):
    """Sort columns by name and make'em equal."""
    sorted_columns = sorted(data.keys())
    max_rows = 0
    for column in sorted_columns:
        if len(data[column]) > max_rows:
            max_rows = len(data[column])
    output_data = {}
    for column in sorted_columns:
        column_data = []
        for r in range(0, max_rows):
            try:
                if isinstance(data[column][r], Teacher):
                    column_data.append(data[column][r].name_with_role)
                else:
                    column_data.append(data[column][r])
            except IndexError:
                column_data.append("")
        output_data[column] = column_data
    return output_data


def export_data(
    schools,
    file_name,
):
    """Poprawiony eksport danych do wielu plików - jeden plik na placówkę"""
    print("")
    print(f"Wyeksportowano dane dla {len(schools)} placówek:")
    x = 1
    for s in schools:
        converted_file_name = file_name.split(".")[:-1]
        converted_file_name.append(f" - {s.file_name} - SALAMI")
        converted_file_name.append(".xlsx")
        converted_file_name = "".join(converted_file_name)
        converted_file_name = prevent_overwrite(converted_file_name)
        school_sheets = {}
        for r in s.rooms:
            term_date = r.term_start.strftime("%m.%d")
            if term_date not in school_sheets.keys():
                school_sheets[term_date] = {}
            if r.row_title not in school_sheets[term_date]:
                school_sheets[term_date][r.row_title] = []
                for t in r.teachers:
                    school_sheets[term_date][r.row_title].append(t)
                school_sheets[term_date][r.row_title] = [r.subject] + sorted(
                    school_sheets[term_date][r.row_title], key=lambda x: x.sort_value
                )
        if school_sheets:
            school_sheets_names_sorted = sorted(school_sheets.keys())
            with pd.ExcelWriter(converted_file_name, engine="xlsxwriter") as writer:
                for sheet_name in school_sheets_names_sorted:
                    sheet_data = _prepare_data(school_sheets[sheet_name])
                    data_frame = pd.DataFrame.from_dict(sheet_data, orient="columns")
                    data_frame.to_excel(writer, sheet_name=sheet_name, startrow=4)
                    # Szerokość kolumn w excelu:
                    for column_name in sheet_data.keys():
                        col_idx = data_frame.columns.get_loc(column_name)
                        writer.sheets[sheet_name].set_column(
                            col_idx + 1, col_idx + 1, 30
                        )
            print(f"{x}. {s.short_name} ({len(s.short_name)})")
            print(f'Zapisano plik "{converted_file_name}"')

        else:
            print(school_sheets)
        x += 1
    print("")


def chmura_salami(file_name: str, sheet_name: str = "Sheet1", one_file: bool = False):
    workbook = pd.read_excel(file_name, sheet_name=sheet_name)
    workbook.head()
    schools = set()
    print("")
    bar = Bar("Konwersja pliku xlsx:", max=len(workbook))
    for row in range(0, len(workbook)):
        bar.next()
        for term in get_terms(workbook):
            teacher = Teacher(
                first_name=workbook["Imię"].iloc[row],
                second_name=workbook["Nazwisko"].iloc[row],
            )
            field = str(workbook[term].iloc[row])
            field_parsed = parse_field(field)
            if field_parsed:
                teacher.role = field_parsed.get("Rola", "")
                f_school = School(
                    name=field_parsed.get("Placówka"),
                )
                f_room = Room(
                    name=field_parsed.get("Sala"),
                    term=term,
                    subject=field_parsed.get("Egzamin", ""),
                )
                if not_in_set(schools, f_school):
                    f_room.teachers.add(teacher)
                    f_school.rooms.add(f_room)
                    schools.add(f_school)
                else:
                    for a_school in schools:
                        if a_school.name == field_parsed.get("Placówka"):
                            if not_in_set(a_school.rooms, f_room):
                                f_room.teachers.add(teacher)
                                a_school.rooms.add(f_room)
                            else:
                                for a_room in a_school.rooms:
                                    if (
                                        a_room.name == field_parsed.get("Sala")
                                        and a_room.term == term
                                    ):
                                        if not_in_set(a_room.teachers, teacher):
                                            a_room.teachers.add(teacher)
                                        else:
                                            raise TeacherAlreadyAddedError(
                                                "Nauczyciel już został dodany!"
                                            )
    bar.finish()
    if one_file:
        export_data_to_one_file(schools, file_name)
    else:
        export_data(schools, file_name)


def main():
    parser = argparse.ArgumentParser(prog="chmura_salami", description="Chmura Salami")
    parser.add_argument("file_name", type=str, help="Nazwa pliku")
    parser.add_argument(
        "-s",
        "--sheet",
        type=str,
        required=False,
        default="Sheet1",
        help='Nazwa arkusza (domyślnie "Sheet1")',
    )
    parser.add_argument(
        "-o",
        "--one-file",
        action="store_true",
        help='Eksport do jednego, "płaskiego" pliku',
    )
    args = parser.parse_args()
    chmura_salami(args.file_name, args.sheet, args.one_file)


if __name__ == "__main__":
    main()
