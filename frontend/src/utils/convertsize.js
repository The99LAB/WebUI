class Unit {
  constructor(name, symbol, conversionFactor, isDecimal = false) {
    this.name = name
    this.symbol = symbol
    this.conversionFactor = conversionFactor
    this.isDecimal = isDecimal
  }
}

const SizeUnit = {
  B: new Unit('Byte', 'B', 1, false),
  KB: new Unit('Kilobyte', 'KB', 10 ** 3, true),
  KiB: new Unit('Kibibyte', 'KiB', 2 ** 10, false),
  MB: new Unit('Megabyte', 'MB', 10 ** 6, true),
  MiB: new Unit('Mebibyte', 'MiB', 2 ** 20, false),
  GB: new Unit('Gigabyte', 'GB', 10 ** 9, true),
  GiB: new Unit('Gibibyte', 'GiB', 2 ** 30, false),
  TB: new Unit('Terabyte', 'TB', 10 ** 12, true),
  TiB: new Unit('Tebibyte', 'TiB', 2 ** 40, false),
  PB: new Unit('Petabyte', 'PB', 10 ** 15, true),
  PiB: new Unit('Pebibyte', 'PiB', 2 ** 50, false),
}

const ConvertSizeUnitMode = {
  INT: 'int',
  INT_STR: 'int_str',
  INT_STR_SPACE: 'int_str_space',
  INT_STR_TUPLE: 'int_str_tuple',
  INT_TUPLE_UNIT: 'int_tuple_unit',
  FLOAT: 'float',
  FLOAT_STR: 'float_str',
  FLOAT_STR_SPACE: 'float_str_space',
  FLOAT_STR_TUPLE: 'float_str_tuple',
  FLOAT_TUPLE_UNIT: 'float_tuple_unit',
}

function getConversionFactors(useDecimalUnits = null) {
  const factors = {
    B: SizeUnit.B.conversionFactor,
    KB: SizeUnit.KB.conversionFactor,
    KiB: SizeUnit.KiB.conversionFactor,
    MB: SizeUnit.MB.conversionFactor,
    MiB: SizeUnit.MiB.conversionFactor,
    GB: SizeUnit.GB.conversionFactor,
    GiB: SizeUnit.GiB.conversionFactor,
    TB: SizeUnit.TB.conversionFactor,
    TiB: SizeUnit.TiB.conversionFactor,
    PB: SizeUnit.PB.conversionFactor,
    PiB: SizeUnit.PiB.conversionFactor,
  }

  if (useDecimalUnits === true) {
    return Object.fromEntries(
      Object.entries(factors).filter(([unit]) => !SizeUnit[unit].symbol.includes('iB')),
    )
  } else if (useDecimalUnits === false) {
    return Object.fromEntries(
      Object.entries(factors).filter(
        ([unit]) => SizeUnit[unit].symbol.includes('iB') || unit === 'B',
      ),
    )
  } else {
    return factors
  }
}

function fromString(unitStr) {
  for (const unit of Object.values(SizeUnit)) {
    if (unit.symbol === unitStr) {
      return unit
    }
  }
  throw new Error(`No matching unit found for symbol: ${unitStr}`)
}

export function convertsize(
  size,
  from_unit,
  to_unit = null,
  mode = ConvertSizeUnitMode.FLOAT,
  roundState = true,
  roundTo = 2,
  useDecimalUnits = false,
) {
  if (!Object.values(ConvertSizeUnitMode).includes(mode)) {
    throw new Error(`Invalid mode ${mode} specified for convertsize()`)
  }

  if (typeof from_unit === 'string') {
    from_unit = fromString(from_unit)
  }

  if (to_unit != null && typeof to_unit === 'string') {
    to_unit = fromString(to_unit)
  }
  let sizeInBytes = size * from_unit.conversionFactor
  if (to_unit === null) {
    for (const [unit, factor] of Object.entries(getConversionFactors(useDecimalUnits)).reverse()) {
      if (sizeInBytes >= factor) {
        to_unit = SizeUnit[unit]
        break
      }
    }
  }
  if (to_unit === null) {
    to_unit = SizeUnit.B
  }

  let convertedSize = sizeInBytes / to_unit.conversionFactor

  if (roundState) {
    convertedSize = parseFloat(convertedSize.toFixed(roundTo))
  }

  switch (mode) {
    case ConvertSizeUnitMode.INT:
      return Math.floor(convertedSize)
    case ConvertSizeUnitMode.INT_STR:
      return `${Math.floor(convertedSize)}${to_unit.symbol}`
    case ConvertSizeUnitMode.INT_STR_SPACE:
      return `${Math.floor(convertedSize)} ${to_unit.symbol}`
    case ConvertSizeUnitMode.INT_STR_TUPLE:
      return [Math.floor(convertedSize), to_unit.symbol]
    case ConvertSizeUnitMode.INT_TUPLE_UNIT:
      return [Math.floor(convertedSize), to_unit]
    case ConvertSizeUnitMode.FLOAT:
      return convertedSize
    case ConvertSizeUnitMode.FLOAT_STR:
      return `${convertedSize}${to_unit.symbol}`
    case ConvertSizeUnitMode.FLOAT_STR_SPACE:
      return `${convertedSize} ${to_unit.symbol}`
    case ConvertSizeUnitMode.FLOAT_STR_TUPLE:
      return [convertedSize, to_unit.symbol]
    case ConvertSizeUnitMode.FLOAT_TUPLE_UNIT:
      return [convertedSize, to_unit]
    default:
      throw new Error(`Invalid mode ${mode} specified for convertsize()`)
  }
}
