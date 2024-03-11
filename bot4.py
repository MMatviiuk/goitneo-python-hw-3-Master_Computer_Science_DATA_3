from collections import UserDict
from datetime import datetime, timedelta
import json


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def validate(self):
        if not self.value.isalpha():
            raise ValueError("Name should contain only letters.")


class Phone(Field):
    def validate(self):
        if len(self.value) != 10 or not self.value.isdigit():
            raise ValueError("Phone number must be 10 digits and contain only digits.")


class Birthday(Field):
    def validate(self):
        try:
            datetime.strptime(self.value, "%d/%m/%Y")
        except ValueError:
            raise ValueError("Invalid birthday format. Please use DD/MM/YYYY.")


class Record:
    def __init__(self, name, phones=None, birthday=None):
        self.name = Name(name)
        self.name.validate()
        self.phones = []
        if phones:
            for phone in phones:
                self.add_phone(phone)
        self.birthday = None
        if birthday:
            self.add_birthday(birthday)

    def add_phone(self, phone):
        phone_obj = Phone(phone)
        phone_obj.validate()
        self.phones.append(phone_obj)

    def remove_phone(self, phone):
        ph = self.find_phone(phone)
        if ph:
            self.phones.remove(ph)

    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone):
        for ph in self.phones:
            if ph.value == phone:
                return ph

    def add_birthday(self, birthday):
        birthday_obj = Birthday(birthday)
        birthday_obj.validate()
        self.birthday = birthday_obj

    def show_birthday(self):
        return self.birthday.value if self.birthday else "No birthday set"

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {', '.join(str(phone) for phone in self.phones)}, Birthday: {self.show_birthday()}"


class AddressBook(UserDict):
    def __init__(self, filename="address_book.json"):
        self.filename = filename
        self.data = self.load()

    def load(self):
        try:
            with open(self.filename, "r") as f:
                return {
                    k: Record(v["name"], v["phones"], v["birthday"])
                    for k, v in json.load(f).items()
                }
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, default=lambda o: o.__dict__, indent=4)

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        name = name.title()
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def show_all(self):
        if self.data:
            for record in self.data.values():
                print(record)
        else:
            print("No contacts found.")

    def get_birthdays_per_week(self):
        today = datetime.today()
        next_week = today + timedelta(days=7)
        birthdays = []
        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d/%m/%Y")
                if today <= birthday_date <= next_week:
                    birthdays.append((record.name.value, record.birthday.value))
        return birthdays


def main():
    book = AddressBook()

    commands = {
        "add": "Add a new contact",
        "change": "Change contact's phone number",
        "find": "Find a contact",
        "all": "Show all contacts",
        "birthdays": "Show birthdays for the next week",
        "exit": "Close the program",
    }

    while True:
        print("Commands:")
        for idx, (command, description) in enumerate(commands.items(), start=1):
            print(f"{idx} - {description}")
        try:
            choice = int(input("Enter a command number: ").strip())
            if choice < 1 or choice > len(commands):
                print("Invalid command number. Please choose a number from the list.")
                continue
        except ValueError:
            print("Invalid format. Please enter a number.")
            continue

        command = list(commands.keys())[choice - 1]

        if command == "add":
            name = input("Enter the name of the new contact: ").strip()
            phones = input("Enter the phone number(s) separated by commas: ").strip().split(",")
            birthday = input("Enter the birthday of the new contact (DD/MM/YYYY): ").strip()
            try:
                record = Record(name, phones, birthday)
                book.add_record(record)
                book.save()
            except ValueError as e:
                print(e)
        elif command == "change":
            name = input("Enter the name of the contact: ").strip()
            record = book.find(name)
            if record:
                old_phone = input("Enter the old phone number: ").strip()
                new_phone = input("Enter the new phone number: ").strip()
                try:
                    record.edit_phone(old_phone, new_phone)
                    book.save()
                except ValueError as e:
                    print(e)
            else:
                print("Contact not found.")
        elif command == "find":
            name = input("Enter the name of the contact: ").strip()
            record = book.find(name)
            if record:
                print(f"Contact found: {record}")
            else:
                print("Contact not found.")
        elif command == "all":
            book.show_all()
        elif command == "birthdays":
            birthdays = book.get_birthdays_per_week()
            if birthdays:
                for name, birthday in birthdays:
                    print(f"Name: {name}, Birthday: {birthday}")
            else:
                print("No birthdays in the next week.")
        elif command == "exit":
            print("Closing the program...")
            break
        else:
            print("Invalid command. Please try again.")


if __name__ == "__main__":
    main()
