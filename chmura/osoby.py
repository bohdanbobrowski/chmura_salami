import argparse

import pandas as pd


def validate_teacher_name(teacher_name: str):
    teacher_name = teacher_name.split(" ")
    rank = None
    if len(teacher_name) > 3:
        rank = teacher_name[3]
    return teacher_name[0], f"{teacher_name[1]} {teacher_name[2]}", rank


def chmura_osoby(file_name: str, output_file_name: str | None):
    xl = pd.ExcelFile(file_name)
    output = {}
    for exam_date in xl.sheet_names:
        workbook = pd.read_excel(file_name, sheet_name=exam_date)
        workbook.head()
        subject_name = workbook.columns[0]
        columns = workbook.columns[2:]
        for column in columns:
            room_name = str(workbook[column].iloc[3])
            if room_name != "nan":
                for row in range(4, len(workbook)):
                    role = "przewodniczący"
                    if row > 4:
                        role = "członek"
                    teacher_name = str(workbook[column].iloc[row]).strip()
                    if teacher_name != "nan":
                        job, teacher_name, rank = validate_teacher_name(teacher_name)
                        if teacher_name not in output:
                            output[teacher_name] = []
                        output[teacher_name].append(
                            [
                                exam_date,
                                room_name,
                                subject_name,
                                role,
                                job,
                                rank,
                            ]
                        )

    sorted_names = list(output.keys())
    sorted_names.sort()

    data = {
        "Imię i nazwisko": [],
        "Termin": [],
        "Sala": [],
        "Przedmiot": [],
        "Rola": [],
        "Kontrakt": [],
        "Ranga": [],
    }
    for teacher_name in sorted_names:
        print(teacher_name)
        for teacher_data in output[teacher_name]:
            data["Imię i nazwisko"].append(teacher_name)
            data["Termin"].append(teacher_data[0])
            data["Sala"].append(teacher_data[1])
            data["Przedmiot"].append(teacher_data[2])
            data["Rola"].append(teacher_data[3])
            data["Kontrakt"].append(teacher_data[4])
            data["Ranga"].append(teacher_data[5])
            print(
                f"({teacher_data[0]}) - ",
                teacher_data[1],
                teacher_data[2],
                teacher_data[3],
                teacher_data[4],
                teacher_data[5],
            )

    if output_file_name:
        with pd.ExcelWriter(output_file_name) as writer:
            data_frame = pd.DataFrame(data)
            data_frame.to_excel(writer, "Chmura osoby")


def main():
    parser = argparse.ArgumentParser(prog="chmura_osoby", description="Chmura Osoby")
    parser.add_argument("file_name", type=str, help="Nazwa pliku")
    parser.add_argument(
        "-o",
        "--output",
        help="Nazwa pliku eksportu",
    )
    args = parser.parse_args()
    chmura_osoby(args.file_name, args.output)


if __name__ == "__main__":
    main()
