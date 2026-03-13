"""
Адресна книга - консольний бот-асистент для управління контактами.

Підтримує зберігання:
- Імен та телефонів (з автоматичним форматуванням у міжнародний формат)
- Email адрес (з валідацією через regex)
- Фізичних адрес
- Днів народження (з нагадуваннями на наступний тиждень)

Дані зберігаються у файл addressbook.pkl за допомогою pickle.
"""
from collections import UserDict
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable, Any, Tuple
import pickle
import re


class Field:
    """Базовий клас для полів запису"""

    def __init__(self, value: Any) -> None:
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Birthday(Field):
    """Клас для зберігання дня народження з валідацією формату DD.MM.YYYY"""

    def __init__(self, value: str) -> None:
        try:
            # Перетворюємо рядок у datetime об'єкт
            birthday = datetime.strptime(value, "%d.%m.%Y")
        except ValueError as exc:
            raise ValueError("Invalid date format. Use DD.MM.YYYY") from exc
        super().__init__(birthday)


class Address(Field):
    """Клас для зберігання адреси"""
    def __init__(self, value: str) -> None:
        if not value or len(value.strip()) == 0:
            raise ValueError("Адреса не може бути порожньою")
        super().__init__(value)


class Email(Field):
    """Клас для зберігання email. Валідація: наявність @ та ."""
    def __init__(self, value: str) -> None:
        pattern = r"[\w.+-]+@[\w-]+\.[\w.]+"
        match = re.search(pattern, value)
        if not match:
            raise ValueError("Неправильний формат email")
        super().__init__(value)


class Name(Field):
    """Клас для зберігання імені контакту. Обов'язкове поле"""

    def __init__(self, value: str) -> None:
        if not value:
            raise ValueError("Ім'я не може бути порожнім")
        super().__init__(value)


class Phone(Field):
    """Клас для зберігання номера телефону. Валідація та форматування номеру"""

    def __init__(self, value: str) -> None:
        # Очищаємо від всіх символів крім цифр
        clean_phone = ''.join(char for char in value if char.isdigit())

        # Перевіряємо формат 10 цифр (0501234567)
        if len(clean_phone) == 10 and clean_phone[0] == '0':
            clean_phone = "+38" + clean_phone
            super().__init__(clean_phone)

        # Перевіряємо формат 12 цифр (380501234567)
        elif len(clean_phone) == 12 and clean_phone.startswith("380"):
            clean_phone = "+" + clean_phone
            super().__init__(clean_phone)

        # Невалідний формат - викидаємо помилку
        else:
            raise ValueError("Неправильний формат телефону")


class Record:
    """Клас для зберігання інформації про контакт"""

    def __init__(self, name: str) -> None:
        self.name = Name(name)
        self.phones: List[Phone] = []
        self.email: Optional[Email] = None
        self.address: Optional[Address] = None
        self.birthday: Optional[Birthday] = None

    def add_email(self, email: str) -> None:
        """Додає email до контакту"""
        email_obj = Email(email)
        self.email = email_obj

    def add_address(self, address: str) -> None:
        """Додає адресу до контакту"""
        address_obj = Address(address)
        self.address = address_obj

    def edit_email(self, new_email: str) -> None:
        """Редагує email контакту"""
        self.email = Email(new_email)

    def edit_address(self, new_address: str) -> None:
        """Редагує адресу контакту"""
        self.address = Address(new_address)

    def add_phone(self, phone: str) -> None:
        """Додає телефон до списку"""
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)

    def add_birthday(self, birthday: str) -> None:
        """Додає день народження до контакту"""
        birthday_obj = Birthday(birthday)
        self.birthday = birthday_obj

    def remove_phone(self, phone: str) -> None:
        """Видаляє телефон зі списку"""
        for found_phone in self.phones:
            if found_phone.value == phone:
                self.phones.remove(found_phone)
                break

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """Редагує телефон (видаляє старий, додає новий)"""
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone: str) -> Optional[Phone]:
        """Знаходить телефон у списку. Повертає об'єкт Phone або None"""
        for found_phone_obj in self.phones:
            if found_phone_obj.value == phone:
                return found_phone_obj
        return None

    def __str__(self) -> str:
        """Повертає рядкове представлення контакту"""
        phones_str = '; '.join(p.value for p in self.phones)
        result = f"Contact name: {self.name.value}, phones: {phones_str}"

        if self.birthday:
            result += f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}"

        if self.email:
            result += f", email: {self.email.value}"

        if self.address:
            result += f", address: {self.address.value}"

        return result


class AddressBook(UserDict[str, Record]):
    """Клас для зберігання та управління записами"""

    def add_record(self, record: Record) -> None:
        """Додає запис до адресної книги"""
        self.data[record.name.value] = record

    def find(self, name: str) -> Optional[Record]:
        """Знаходить запис за ім'ям. Повертає Record або None"""
        return self.data.get(name)

    def delete(self, name: str) -> None:
        """Видаляє запис за ім'ям"""
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self) -> List[Dict[str, str]]:
        """Повертає список користувачів, яких потрібно привітати на наступному тижні"""
        today = datetime.today().date()
        upcoming_birthdays: List[Dict[str, str]] = []

        for record in self.data.values():
            # Пропускаємо контакти без дня народження
            if not record.birthday:
                continue

            # Отримуємо дату народження
            birthday = record.birthday.value.date()
            # Переносимо день народження на поточний рік
            birthday_this_year = birthday.replace(year=today.year)

            # Якщо день народження вже минув цього року, беремо наступний рік
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            # Рахуємо кількість днів до дня народження
            delta_days = (birthday_this_year - today).days

            # Перевіряємо чи день народження протягом наступних 7 днів
            if 0 <= delta_days <= 7:
                weekday = birthday_this_year.weekday()

                # Якщо день народження випадає на суботу, переносимо на понеділок
                if weekday == 5:
                    congratulation_date = birthday_this_year + timedelta(days=2)
                # Якщо на неділю, також переносимо на понеділок
                elif weekday == 6:
                    congratulation_date = birthday_this_year + timedelta(days=1)
                else:
                    congratulation_date = birthday_this_year

                # Додаємо до списку
                upcoming_birthdays.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime("%d.%m.%Y")
                })

        return upcoming_birthdays


# Функції для роботи з ботом

def parse_input(user_input: str) -> Tuple[str, ...]:
    """Розбирає введення користувача на команду та аргументи"""
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return (cmd, *args)


def input_error(func: Callable[..., str]) -> Callable[..., str]:
    """Декоратор для обробки помилок введення"""

    def inner(*args: Any, **kwargs: Any) -> str:
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Not enough arguments."

    return inner


@input_error
def add_contact(args: List[str], book: AddressBook) -> str:
    """Додає новий контакт або оновлює існуючий"""
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    if phone:
        record.add_phone(phone)

    return message


@input_error
def change_contact(args: List[str], book: AddressBook) -> str:
    """Змінює телефон існуючого контакту"""
    name, old_phone, new_phone = args
    record = book.find(name)

    if record is None:
        return "Contact not found."

    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args: List[str], book: AddressBook) -> str:
    """Показує телефони вказаного контакту"""
    name, *_ = args
    record = book.find(name)

    if record is None:
        return "Contact not found."

    phones = "; ".join(phone.value for phone in record.phones)
    return f"{name}: {phones}"


@input_error
def show_all(_: List[str], book: AddressBook) -> str:
    """Показує всі контакти в адресній книзі"""
    if not book.data:
        return "No contacts found."

    result = []
    for record in book.data.values():
        result.append(str(record))

    return "\n".join(result)


@input_error
def add_birthday(args: List[str], book: AddressBook) -> str:
    """Додає день народження до контакту"""
    name, birthday = args
    record = book.find(name)

    if record is None:
        return "Contact not found."

    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args: List[str], book: AddressBook) -> str:
    """Показує день народження вказаного контакту"""
    name, *_ = args
    record = book.find(name)

    if record is None:
        return "Contact not found."

    if not record.birthday:
        return "Birthday not found."

    return record.birthday.value.strftime("%d.%m.%Y")


@input_error
def add_email(args: List[str], book: AddressBook) -> str:
    """Додає email до контакту"""
    name, email = args
    record = book.find(name)

    if record is None:
        return "Contact not found."

    record.add_email(email)
    return "Email added."


@input_error
def add_address(args: List[str], book: AddressBook) -> str:
    """Додає адресу до контакту (вся решта рядка - це адреса)"""
    if len(args) < 2:
        return "Not enough arguments."

    name = args[0]
    address = ' '.join(args[1:])  # З'єднуємо всі слова після імені
    record = book.find(name)

    if record is None:
        return "Contact not found."

    record.add_address(address)
    return "Address added."


@input_error
def show_email(args: List[str], book: AddressBook) -> str:
    """Показує email вказаного контакту"""
    name, *_ = args
    record = book.find(name)

    if record is None:
        return "Contact not found."

    if not record.email:
        return "Email not found."

    return record.email.value


@input_error
def show_address(args: List[str], book: AddressBook) -> str:
    """Показує адресу вказаного контакту"""
    name, *_ = args
    record = book.find(name)

    if record is None:
        return "Contact not found."

    if not record.address:
        return "Address not found."

    return record.address.value


@input_error
def birthdays(_: List[str], book: AddressBook) -> str:
    """Показує дні народження на наступному тижні"""
    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "No upcoming birthdays."

    result = []
    for user in upcoming:
        name = user["name"]
        date = user["congratulation_date"]
        line = f"{name}: {date}"
        result.append(line)

    return "\n".join(result)


def save_data(book: AddressBook, filename: str = "addressbook.pkl") -> None:
    """Зберігає адресну книгу у файл"""
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename: str = "addressbook.pkl") -> AddressBook:
    """Завантажує адресну книгу з файлу"""
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повертаємо нову книгу, якщо файл не знайдено


def main() -> None:
    """Головна функція програми - запускає бота-асистента"""
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break

        if command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "add-email":
            print(add_email(args, book))

        elif command == "add-address":
            print(add_address(args, book))

        elif command == "show-email":
            print(show_email(args, book))

        elif command == "show-address":
            print(show_address(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
