# !/usr/bin/env python3
# -*- coding: utf-8 -*-

#Выполнить индивидуальное задание лабораторной работы 4.5, использовав классы данных, а
#также загрузку и сохранение данных в формат XML.

import argparse
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class Person:
    surname: str
    name: str
    zodiac: str
    birthday: list


@dataclass
class People:
    people: List[dict] = field(default_factory=list)

    def add(self, surname: str, name: str, zodiac: str, birthday: str):
        self.people.append(Person(surname, name, zodiac, birthday.split(".")))

        self.people.sort(
            key=lambda x: datetime.strptime(".".join(x.birthday), "%d.%m.%Y")
        )

    def __str__(self):
        table = []
        line = "+-{}-+-{}-+-{}-+-{}-+-{}-+".format(
            "-" * 4, "-" * 30, "-" * 30, "-" * 20, "-" * 20
        )
        table.append(line)
        table.append(
            "| {:^4} | {:^30} | {:^30} | {:^20} | {:^20} |".format(
                "№", "Фамилия", "Имя", "Знак зодиака", "Дата рождения"
            )
        )
        table.append(line)

        for idx, person in enumerate(self.people, 1):
            print(
                "| {:>4} | {:<30} | {:<30} | {:<20} | {:>20} |".format(
                    idx,
                    person.get("surname", ""),
                    person.get("name", ""),
                    person.get("zodiac", ""),
                    ".".join(person.get("birthday", "")),
                )
            )
        table.append(line)
        return "\n".join(table)

    def select(self, surname: str):
        result = People()
        for i in self.people:
            if i.surname == surname:
                result.add(i)
        return result

    def load(self, filename: str):
        with open(filename, "r", encoding="utf8") as fin:
            xml = fin.read()

        parser = ET.XMLParser(encoding="utf8")
        tree = ET.fromstring(xml, parser=parser)

        self.people = []
        for person_element in tree:
            surname, name, zodiac, birthday = None, None, None, None

            for element in person_element:
                match element.tag:
                    case "surname":
                        surname = element.text
                    case "name":
                        name = element.text
                    case "zodiac":
                        zodiac = element.text
                    case "birthday":
                        birthday = element.text

                if (
                    surname is not None
                    and name is not None
                    and zodiac is not None
                    and birthday is not None
                ):
                    self.people.append(
                        Person(surname, name, zodiac, birthday.split("."))
                    )

    def save(self, filename: str):
        root = ET.Element("people")
        for person in self.people:
            person_element = ET.Element("person")

            surname_element = ET.SubElement(person_element, "surname")
            surname_element.text = person.surname

            name_element = ET.SubElement(person_element, "name")
            name_element.text = person.name

            zodiac_element = ET.SubElement(person_element, "zodiac")
            zodiac_element.text = person.zodiac

            birthday_element = ET.SubElement(person_element, "birthday")
            birthday_element.text = ".".join(person.birthday)

            root.append(person_element)

        tree = ET.ElementTree(root)
        with open(filename, "wb") as fout:
            tree.write(fout, encoding="utf8", xml_declaration=True)


def main(command_line=None):
    """
    Главная функция программы.
    """
    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "filename", action="store", help="The data file name"
    )

    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("people")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    subparsers = parser.add_subparsers(dest="command")

    # Создать субпарсер для добавления человека.
    add = subparsers.add_parser(
        "add", parents=[file_parser], help="Add a new person"
    )
    add.add_argument(
        "-s",
        "--surname",
        action="store",
        required=True,
        help="The person's surname",
    )
    add.add_argument(
        "-n", "--name", action="store", required=True, help="The person's name"
    )
    add.add_argument(
        "-z", "--zodiac", action="store", help="The person's zodiac"
    )
    add.add_argument(
        "-b",
        "--birthday",
        action="store",
        required=True,
        help="The person's birthday",
    )

    # Создать субпарсер для отображения всех людей.
    _ = subparsers.add_parser(
        "display", parents=[file_parser], help="Display people"
    )

    # Создать субпарсер для выбора людей по фамилии.
    select = subparsers.add_parser(
        "select", parents=[file_parser], help="Select people by surname"
    )
    select.add_argument(
        "-s",
        "--surname",
        action="store",
        type=str,
        required=True,
        help="The required surname",
    )

    # Выполнить разбор аргументов командной строки.
    args = parser.parse_args(command_line)

    people = People()

    # Домашний каталог
    home_path = Path.home() / args.filename

    is_dirty = False
    if home_path.exists():
        people.load(home_path)

    match args.command:
        case "add":
            people.add(args.surname, args.name, args.zodiac, args.birthday)
            is_dirty = True

        case "select":
            selected = people.select(args.surname, people)
            if selected.people:
                print(selected)
            else:
                print("Люди с заданной фамилией не найдены")

        case "display":
            print(people)

    if is_dirty:
        people.save(home_path)


if __name__ == "__main__":
    main()
