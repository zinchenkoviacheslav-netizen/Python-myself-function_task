def celsius_to_fahrenheit(value):
    return value * 1.8 + 32

def miles_to_km(value):
    return value * 1.60934

def km_to_miles(value):
    return value / 1.60934

def fahrenheit_to_celsius(value):
    return (value - 32) / 1.8

def convert(value, from_unit, to_unit):
    key = (from_unit, to_unit)
    return round(dict_convert[key](value), 2)


dict_convert = {("km", "miles") : km_to_miles,
("miles", "km") : miles_to_km, ("celsius", "fahrenheit") : celsius_to_fahrenheit,
("fahrenheit", "celsius") : fahrenheit_to_celsius}

print(convert(100, "km", "miles"))       
print(convert(100, "miles", "km"))        
print(convert(0, "celsius", "fahrenheit")) 
print(convert(32, "fahrenheit", "celsius"))