# mode: 
#  str: returns a string with the size and unit concatenated together
#  str_space: returns a string with the size and unit separated by a space
#  tuple: returns a tuple with the size and unit
#  int: returns an integer with the size
#  float: returns a float with the size
#  default: same as float

from .storage_manager_exception import StorageManagerException

def convertSizeUnit(size: int, from_unit, to_unit=None, mode="float", round_state=True, round_to=2):
    sizeUnit = {
        "B": 0,
        "KB": 1,
        "MB": 2,
        "GB": 3,
        "TB": 4,
    }

    if from_unit == to_unit:
        return size

    # if to_unit is not specified, find the largest unit that size can be converted to
    if to_unit == None:
        for unit in sizeUnit:
            # If we convert size to the current unit, and the result is greater than or equal to 1.0, then we have found the largest unit
            if size / (1024 ** (sizeUnit[unit] - sizeUnit[from_unit])) >= 1.0:
                to_unit = unit
            else: # if the result is less than 1.0, then we have found the largest unit, so break
                break

    if to_unit == None:
        to_unit = from_unit
  
    # find the difference between the two units
    difference = sizeUnit[from_unit] - sizeUnit[to_unit]
    if difference > 0:
        # if difference is positive, then size is being converted to a smaller unit
        # so divide the size by 1024^difference
        new_size = size * (1024 ** difference)
    else:
        # if difference is negative, then size is being converted to a larger unit
        # so multiply the size by 1024^difference
        new_size = size / (1024 ** abs(difference))

    if round_state:
        if round_to == None:
            new_size = int(new_size)
        else:
            new_size = round(new_size, round_to)
 
    if mode == "str":
        return str(new_size) + to_unit
    elif mode == "str_space":
        return str(new_size) + " " + to_unit
    elif mode == "tuple":
        return (new_size, to_unit)
    elif mode == "int":
        return int(new_size)
    elif mode == "float":
        return new_size
    else:
        raise StorageManagerException(f"Invalid mode {mode} specified for convertSizeUnit()")