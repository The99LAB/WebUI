# mode: 
#  str: returns a string with the size and unit concatenated together
#  str_space: returns a string with the size and unit separated by a space
#  tuple: returns a tuple with the size and unit
#  int: returns an integer with the size
#  float: returns a float with the size
#  default: same as float

from .storage_manager_exception import StorageManagerException

class Unit:
    def __init__(self, name, symbol, conversion_factor, is_decimal=False):
        self.name = name
        self.symbol = symbol
        self.conversion_factor = conversion_factor
        self.is_decimal = is_decimal

class SizeUnit:
    B = Unit("Byte", "B", 1, is_decimal=False)
    KB = Unit("Kilobyte", "KB", 10**3, is_decimal=True)
    KiB = Unit("Kibibyte", "KiB", 2**10, is_decimal=False)
    MB = Unit("Megabyte", "MB", 10**6, is_decimal=True)
    MiB = Unit("Mebibyte", "MiB", 2**20, is_decimal=False)
    GB = Unit("Gigabyte", "GB", 10**9, is_decimal=True)
    GiB = Unit("Gibibyte", "GiB", 2**30, is_decimal=False)
    TB = Unit("Terabyte", "TB", 10**12, is_decimal=True)
    TiB = Unit("Tebibyte", "TiB", 2**40, is_decimal=False)
    PB = Unit("Petabyte", "PB", 10**15, is_decimal=True)
    PiB = Unit("Pebibyte", "PiB", 2**50, is_decimal=False)

    @property
    def conversion_factors(self):
        return {
            SizeUnit.B: SizeUnit.B.conversion_factor,
            SizeUnit.KB: SizeUnit.KB.conversion_factor,
            SizeUnit.KiB: SizeUnit.KiB.conversion_factor,
            SizeUnit.MB: SizeUnit.MB.conversion_factor,
            SizeUnit.MiB: SizeUnit.MiB.conversion_factor,
            SizeUnit.GB: SizeUnit.GB.conversion_factor,
            SizeUnit.GiB: SizeUnit.GiB.conversion_factor,
            SizeUnit.TB: SizeUnit.TB.conversion_factor,
            SizeUnit.TiB: SizeUnit.TiB.conversion_factor,
            SizeUnit.PB: SizeUnit.PB.conversion_factor,
            SizeUnit.PiB: SizeUnit.PiB.conversion_factor
        }

    def get_conversion_factors(self, use_decimal_units=None):
        if use_decimal_units == True:
            return {unit: unit.conversion_factor for unit in self.conversion_factors if "iB" not in unit.symbol}
        elif use_decimal_units == False:
            return {unit: unit.conversion_factor for unit in self.conversion_factors if "iB" in unit.symbol or unit == SizeUnit.B}
        else:
            return self.conversion_factors
        
    @classmethod
    def from_string(cls, unit_str):
        for unit in cls.__dict__.values():
            if isinstance(unit, Unit) and unit.symbol == unit_str:
                return unit
        raise ValueError(f"No matching unit found for symbol: {unit_str}")

class ConvertSizeUnitMode:
    """ STR = "str"
    STR_SPACE = "str_space"
    TUPLE = "tuple"
    TUPLE_UNIT = "tuple_unit"
    INT = "int"
    FLOAT = "float" """
    INT = "int" # returns an integer: "1"
    INT_STR = "int_str" # returns a string with the size and unit(symbol) concatenated together: "1B"
    INT_STR_SPACE = "int_str_space" # returns a string with the size and unit(symbol) separated by a space: "1 B"
    INT_STR_TUPLE = "int_str_tuple" # returns a tuple with the size and unit(symbol): (1, "B")
    INT_TUPLE_UNIT = "int_tuple_unit"  # returns a tuple with the size and unit: (1, SizeUnit.B)
    FLOAT = "float" # returns a float: 1.0
    FLOAT_STR = "float_str" # returns a string with the size and unit(symbol) concatenated together: "1.0B"
    FLOAT_STR_SPACE = "float_str_space" # returns a string with the size and unit(symbol) separated by a space: "1.0 B"
    FLOAT_STR_TUPLE = "float_str_tuple" # returns a tuple with the size and unit(symbol): (1.0, "B")
    FLOAT_TUPLE_UNIT = "float_str_tuple_unit" # returns a tuple with the size and unit: (1.0, SizeUnit.B)
    
       
def convertSizeUnit(size: int, from_unit, to_unit=None, mode=ConvertSizeUnitMode.FLOAT, round_state=True, round_to=2, use_decimal_units=False):
    print(f"Size: {size}")
    # Perform input validation
    # Check if mode is valid
    if mode not in ConvertSizeUnitMode.__dict__.values():
        raise StorageManagerException(f"Invalid mode {mode} specified for convertSizeUnit()")

    # Check if from_unit is a valid unit
    if not isinstance(from_unit, Unit):
        # Convert the unit string to a SizeUnit object
        try:
            from_unit = SizeUnit.from_string(from_unit)
        except ValueError:
            raise StorageManagerException(f"Invalid from_unit {from_unit} specified for convertSizeUnit()")

    print(f"From unit: {from_unit.name} {from_unit.symbol}")

    # Check if to_unit is a valid unit
    if to_unit and not isinstance(to_unit, Unit):
        # Convert the unit string to a SizeUnit object
        try:
            to_unit = SizeUnit.from_string(to_unit)
        except ValueError:
            raise StorageManagerException(f"Invalid to_unit {to_unit} specified for convertSizeUnit()")

    if to_unit:
        print(f"To unit: {to_unit.name} {to_unit.symbol}")


    # Convert size to bytes
    size_in_bytes = size * from_unit.conversion_factor

    # If to_unit is not specified, find the largest unit that size can be converted to
    if not to_unit:
        for unit, factor in reversed(SizeUnit().get_conversion_factors(use_decimal_units=use_decimal_units).items()):
            if size_in_bytes >= factor:
                to_unit = unit
                break
    
    if not to_unit:
        to_unit = SizeUnit.B

    # Convert bytes to the target unit
    converted_size = size_in_bytes / to_unit.conversion_factor

    print(f"Converted size: {converted_size} {to_unit.symbol}")

    # Round the result if required
    if round_state:
        converted_size = round(converted_size, round_to)

    # Return the result based on the mode
    if mode == ConvertSizeUnitMode.INT:
        return int(converted_size)
    elif mode == ConvertSizeUnitMode.INT_STR:
        return f"{int(converted_size)}{to_unit.symbol}"
    elif mode == ConvertSizeUnitMode.INT_STR_SPACE:
        return f"{int(converted_size)} {to_unit.symbol}"
    elif mode == ConvertSizeUnitMode.INT_STR_TUPLE:
        return (int(converted_size), to_unit.symbol)
    elif mode == ConvertSizeUnitMode.INT_TUPLE_UNIT:
        return (int(converted_size), to_unit)
    elif mode == ConvertSizeUnitMode.FLOAT:
        return float(converted_size)
    elif mode == ConvertSizeUnitMode.FLOAT_STR:
        return f"{converted_size}{to_unit.symbol}"
    elif mode == ConvertSizeUnitMode.FLOAT_STR_SPACE:
        return f"{converted_size} {to_unit.symbol}"
    elif mode == ConvertSizeUnitMode.FLOAT_STR_TUPLE:
        return (converted_size, to_unit.symbol)
    elif mode == ConvertSizeUnitMode.FLOAT_TUPLE_UNIT:
        return (converted_size, to_unit)        
