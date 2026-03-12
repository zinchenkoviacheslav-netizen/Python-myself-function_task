import re


def validate_and_format_phone(text):
    clean_phone = ''.join(char for char in text if char.isdigit())
    if len(clean_phone) == 10 and clean_phone[0] == '0':
        clean_phone = "+38" + clean_phone
        return clean_phone
    elif len(clean_phone) == 12 and clean_phone.startswith("380"):
        clean_phone = "+" + clean_phone
        return clean_phone
    else:
        clean_phone = None
        return clean_phone


def is_valid_email(text):
    pattern = r"[\w.+-]+@[\w-]+\.[\w.]+"
    match = re.search(pattern, text)
    if match:
        mailto = match.group()
        return mailto
    else:
        return "Invalid email"


print(is_valid_email("   sdjcnGHJdsjdndj@asd.vb   "))
print(is_valid_email("sdjcnsjdndj"))
print(validate_and_format_phone("0501234567"))  # +380501234567 ✅
print(validate_and_format_phone("050-123-45-67"))  # +380501234567 ✅
print(validate_and_format_phone("+38 050 666 66 67"))  # +380501234567 ✅
print(validate_and_format_phone("380501234567"))  # +380501234567 ✅
print(validate_and_format_phone("80501234567"))  # Invalid phone ✅
print(validate_and_format_phone("1380501234567"))  # Invalid phone ✅
print(validate_and_format_phone("123"))  # Invalid phone ✅