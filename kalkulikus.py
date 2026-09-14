from enum import auto, Enum
from collections import defaultdict
from dataclasses import dataclass, field, fields
from typing import Any, Callable, DefaultDict, List, Tuple, Set

# CORE OF THE KALKULIKUS IDEA..
# THE KEY TO THE GREAT UNIVERSE
# OF NUMERIC SYSTEMS 3 6 9 12 ⧝
class NumericSystem(str, Enum):
    BIN = '01'
    TRI = '012'
    QTR = '0123'
    QIN = '01234'
    SEX = '012345'
    SEP = '0123456'
    OCT = '01234567'
    NON = '012345678'
    DEC = '0123456789'
    DOZ = '0123456789AB'
    PTD = '0123456789ABCDE'
    HEX = '0123456789ABCDEF'
    DTG = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
    EHX = '0123456789ABCDEFGHIJKLMNOPQRSTUV'
    MAY = '𝋠𝋡𝋢𝋣𝋤𝋥𝋦𝋧𝋨𝋪𝋫𝋬𝋭𝋮𝋯𝋰𝋱𝋲𝋳'
    TSL = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz⧝'
NumSys = NumericSystem


# NUMERIC SYSTEM SYMBOLS CONTAINER
@dataclass
class Symbols:
    items:      str
    ns_name:    str

    def __post_init__(self):
        Symbols.validate(self.items)
    def __len__(self) -> int:
        return len(self.items)
    def __contains__(self, item: str) -> bool:
        return item in self.items
    def __getitem__(self, index: int) -> str:
        return self.items[index]

    @property
    def base(self) -> int:
        return len(self.items)
    @property
    def min_value(self) -> str:
        return self.items[0]
    @property
    def max_value(self) -> str:
        return self.items[-1]
    @property
    def index_padding(self) -> str:
        return len(str(self.base - 1))

    def index(self, symbol: str) -> int:
        return self.items.index(symbol)

    @staticmethod
    def validate(symbols: str) -> str:
        if len(symbols) < 2:
            raise ValueError('Numeric system symbols must contain at least two items!')
        if len(set(symbols)) < len(symbols):
            raise ValueError(f'Repeating symbol found! All numeric symbols must be unique! {symbols} vs. {set(symbols)}')
        try: numsys_name = NumSys(symbols).name.lower()
        except: numsys_name = f'b_{len(symbols)}'
        return numsys_name
    @staticmethod
    def from_numsys(numsys: NumericSystem) -> 'Symbols':
        if not isinstance(numsys, NumSys): raise TypeError()
        return Symbols(numsys.value, numsys.name.lower())
    @staticmethod
    def from_string(symbols: str) -> 'Symbols':
        if not isinstance(symbols, str): raise TypeError()
        return Symbols(symbols, Symbols.validate(symbols))
    @staticmethod
    def from_items(symbols: List[str]) -> 'Symbols':
        if not isinstance(symbols, list): raise TypeError()
        if not all(s for s in symbols if isinstance(s, str)):
            raise ValueError()
        return Symbols.from_string("".join(s for s in symbols))
    @staticmethod
    def create(obj) -> 'Symbols':
        if not obj: raise ValueError()
        if isinstance(obj, Symbols): return obj
        if isinstance(obj, NumSys): return Symbols.from_numsys(obj)
        if isinstance(obj, list): return Symbols.from_items(obj)
        if isinstance(obj, str): return Symbols.from_string(obj)
        raise TypeError()


# VALUE DATA CONTAINER
@dataclass
class ValueData:
    pure_value      : str
    symbols         : Symbols
    fp_digits       : int = 0
    is_negative     : bool = False

    def __str__(self) -> str:
        return self.value_str

    @property
    def base(self) -> int:
        return self.symbols.base
    @property
    def min_value(self) -> str:
        return self.symbols.min_value
    @property
    def max_value(self) -> str:
        return self.symbols.max_value
    @property
    def is_positive(self) -> bool:
        return not self.is_negative
    @property
    def is_zero(self) -> bool:
        return len(set(list(self.pure_value))) == 1 and self.symbols.min_value in self.pure_value
    @property
    def is_not_zero(self) -> bool:
        return not self.is_zero
    @property
    def is_one(self) -> bool:
        return self.pure_value == self.symbols[1]
    @property
    def is_float(self) -> bool:
        return self.fp_digits > 0
    @property
    def is_lt_zero(self) -> bool:
        return self.is_negative
    @property
    def is_le_zero(self) -> bool:
        return self.is_negative or self.is_zero
    @property
    def is_ge_zero(self) -> bool:
        return not self.is_negative
    @property
    def is_gt_zero(self) -> bool:
        return not (self.is_zero and self.is_negative)
    @property
    def length(self) -> int:
        return len(self.pure_value)
    @property
    def index_padding(self) -> int:
        return self.symbols.index_padding
    @property
    def fp_index(self) -> int:
        return self.length - self.fp_digits if self.is_float else -1
    @property
    def fp_int_part(self) -> str:
        return self.pure_value[:self.fp_index] if self.is_float else self.pure_value
    @property
    def fp_fract_part(self) -> str:
        return self.pure_value[self.fp_index:] if self.is_float else ""
    @property
    def fp_string(self) -> str:
        return f'{self.fp_int_part}.{self.fp_fract_part}' if self.is_float else self.pure_value
    @property
    def value_str(self) -> str:
        return f'{"-" if self.is_negative else ""}{self.fp_string}'

    def get_opposite(self):
        return ValueData(self.pure_value, self.symbols, self.fp_digits, not self.is_negative)
    def normalize(self):
        val = self.pure_value
        while val.startswith(self.min_value) and len(val) > self.fp_digits + 1:
            val = val[1:]
        if self.is_float:
            while val.endswith(self.min_value) and self.fp_digits > 0:
                self.fp_digits -= 1
                val = val[:-1]
        self.pure_value = val
        return self
    def adjust_fp_digits(self, fp_digits: int):
        if fp_digits < 0: return self
        if self.fp_digits == fp_digits: return self
        while self.fp_digits < fp_digits:
            self.pure_value += self.min_value
            self.fp_digits += 1
        while self.fp_digits > fp_digits and self.pure_value.endswith(self.min_value):
            self.pure_value = self.pure_value[:-1]
            self.fp_digits -= 1
        return self

    @staticmethod
    def create_default(symbols) -> 'ValueData':
        symbols = Symbols.create(symbols)
        return ValueData(symbols.min_value, symbols)
    @staticmethod
    def create(val, symbols) -> 'ValueData':
        try:
            if isinstance(val, ValueData): return val
            symbols = Symbols.create(symbols)
            val, fp_digits, is_negative = ValueData.parse(val, symbols)
            return ValueData(val, symbols, fp_digits, is_negative)
        except Exception as ex:
            print(f'Provided input is invalid!\n{ex}')
            return None
    @staticmethod
    def parse(val, symbols) -> Tuple[str, int, bool]:
        symbols = Symbols.create(symbols)
        val = ValueData.validate(val, symbols)
        fp_digits = 0
        is_negative = val.startswith('-')
        val = val[1:] if is_negative else val
        if '.' in val:
            parts = val.split('.')
            left = parts[0]
            right = parts[1]
            if not left or len(left) == 0:
                left = symbols.min_value
            fp_digits = len(right)
            val = f'{left}{right}'
        return val, fp_digits, is_negative
    @staticmethod
    def validate(value, symbols):
        symbols = Symbols.create(symbols)
        val = str(value)
        if not value or len(val) == 0:
            raise ValueError('Value must be a number or a non empty string!')
        if any([v for v in val if v not in f'.-{symbols.items}']):
            raise ValueError('Value contains invalid symbols!')
        if '-' in val and val.rindex('-') > 0:
            raise ValueError('Value has an invalid format! (-)')
        if '.' in val and (val.startswith('.') or val.endswith('.') or val.count('.') > 1):
            raise ValueError('Value has an invalid format! (.)')
        return val
    @staticmethod
    def align_fp_digits(first: 'ValueData', second: 'ValueData'):
        if first.fp_digits < second.fp_digits:
            second.adjust_fp_digits(first.fp_digits)
            first.adjust_fp_digits(second.fp_digits)
        else:
            first.adjust_fp_digits(second.fp_digits)
            second.adjust_fp_digits(first.fp_digits)
        return first, second


# TWO-STATE LEVER
@dataclass
class Lever:
    engaged_value       : str
    disengaged_value    : str = ''
    _current_state      : bool = False
    _default_state      : bool = False

    def __post_init__(self):
        if not self.engaged_value or self.engaged_value == self.disengaged_value:
            raise ValueError("Values must be distinct and non-empty.")
        object.__setattr__(self, '_engaged_val', self.engaged_value)
        delattr(self, 'engaged_value')
        object.__setattr__(self, '_disengaged_val', self.disengaged_value)
        delattr(self, 'disengaged_value')

    @property
    def is_engaged(self) -> bool:
        return self._current_state
    @property
    def value(self) -> str:
        return self._engaged_val if self._current_state else self._disengaged_val

    def engage(self):
        if not self.is_engaged:
            self._current_state = True
    def disengage(self):
        if self.is_engaged:
            self._current_state = False
    def set_state(self, state: bool):
        if state: self.engage()
        else: self.disengage()
    def current_as_default(self):
        self._default_state = self._current_state
    def restore_default(self):
        self._current_state = self._default_state
    def clear(self):
        self.disengage()
    def clear_default(self):
        self._default_state = False
    def reset(self):
        self.clear()
        self.clear_default()


# STRETCHABLE RING WITH SHIFTABLE SYMBOLS
@dataclass
class Ring:
    symbols         : str|Symbols
    _scale          : int         = 1
    _band          : List[str]   = field(default_factory=list)

    def __post_init__(self):
        object.__setattr__(self, '_symbols', Symbols.create(self.symbols))
        delattr(self, 'symbols')
        self._band = list(self._symbols.items)
    def __str__(self):
        return self.items_str

    @property
    def scale(self) -> int:
        return self._scale
    @property
    def value(self) -> str:
        return self._band[0]
    @property
    def is_min(self) -> bool:
        return self._band[0] == self._symbols.min_value
    @property
    def is_max(self) -> bool:
        return self._band[1] == self._symbols.min_value
    @property
    def items_str(self) -> str:
        return "".join(self._band)

    def shift_up(self) -> bool:
        self._band.append(self._band.pop(0))
        return self.is_min
    def shift_down(self) -> bool:
        self._band.insert(0, self._band.pop())
        return self.is_max
    def stretch_up(self):
        self._scale += 1
        self._update()
    def stretch_down(self):
        if self._scale > 1:
            self._scale -= 1
            self._update()
    def apply_symbols(self, symbols: str|Symbols):
        symbols = Symbols.create(symbols)
        if symbols == self._symbols: return
        self._symbols = symbols
        self._update()
    def reset(self):
        if self._scale == 1:
            while not self.is_min:
                self.shift_down()
        else:
            while self._scale > 1:
                self.stretch_down()

    def _update(self):
        stretch_gap = " " * (self._scale - 1)
        self._band = list("".join([f'{s}{stretch_gap}' for s in self._symbols.items]))


# SCROLLABLE & ATTACHABLE GEAR WITH STRETCHABLE RING
@dataclass
class Gear:
    symbols           : str
    auto_size         : bool        = True
    init_index        : int         = 0
    _reminder         : int         = 0
    _last_symbol      : str         = None
    _symbol_ring      : Ring        = None
    _attached_gear    : 'Gear'      = None

    def __post_init__(self):
        object.__setattr__(self, '_symbols', Symbols.create(self.symbols))
        delattr(self, 'symbols')
        object.__setattr__(self, '_auto_size', self.auto_size)
        delattr(self, 'auto_size')
        self._symbol_ring = Ring(self._symbols)
        self._last_symbol = self._symbols.min_value
        for _ in range(self.init_index):
            self.scroll_up()
        delattr(self, 'init_index')

    def __eq__(self, other) -> bool:
        if not isinstance(other, Gear): return False
        return self.get_ring_str() == other.get_ring_str()
    def __str__(self) -> str:
        return self.get_value()

    @property
    def value(self) -> str:
        return self._symbol_ring.value
    @property
    def index(self) -> int:
        if self.value in self._symbols:
            return self._symbols.index(self.value)
        else:
            return self._symbols.index(self._last_symbol)
    @property
    def symbol(self) -> str:
        return self._symbols[self.index]
    @property
    def reminder(self) -> str:
        return self._reminder
    @property
    def is_min(self) -> bool:
        return self._symbol_ring.is_min
    @property
    def is_max(self) -> bool:
        return self._symbol_ring.is_max
    @property
    def has_attached_gear(self) -> bool:
        return self._attached_gear != None
    @property
    def is_last(self) -> bool:
        return not self.has_attached_gear

    # SCROLLING
    def scroll_up(self) -> bool:
        self._symbol_ring.shift_up()
        if self._symbol_ring.scale == 1:
            self._last_symbol = self.value
        else:
            if self.value in self._symbols:
                self._last_symbol = self.value
                self._reminder = 0
            else:
                self._reminder += 1
        if self.is_min:
            if self.is_last and self._auto_size:
                self.attach()
            if self.has_attached_gear:
                self._attached_gear.scroll_up()
        return self.is_min
    def scroll_down(self):
        self._symbol_ring.shift_down()
        if self._symbol_ring.scale == 1:
            self._last_symbol = self.value
        else:
            if self._reminder > 0:
                self._reminder -=1
            else:
                self._reminder = self._symbol_ring.scale - 1
                if self.index == 0:
                    self._last_symbol = self._symbols[-1]
                else:
                    self._last_symbol = self._symbols[self.index - 1]
        if self.has_attached_gear:
            if self.is_max:
                self._attached_gear.scroll_down()
            if self._auto_size and self._attached_gear.is_last and self._attached_gear.is_min:
                self._attached_gear = None
        return self.is_max
    def scroll_to_start(self):
        while not self.is_min:
            self.scroll_down()
        if self._auto_size:
            self._attached_gear = None
        elif self.has_attached_gear:
            self._attached_gear.scroll_to_start()
    def scroll_to_index(self, index: int):
        if index < 0 or index >= len(self._symbols):
            raise ValueError()
        while self.index < index:
            self.scroll_up()
        while self.index > index:
            self.scroll_down()
    def scroll_to_indices(self, indices: List[int]):
        if not indices: return
        self.scroll_to_index(indices.pop())
        if not indices:
            if self._auto_size:
                self._attached_gear = None
            elif self.has_attached_gear:
                self._attached_gear.scroll_to_start()
            return
        if self.is_last:
            if not self._auto_size:
                return
            self.attach()
        self._attached_gear.scroll_to_indices(indices)

    # STRETCHING
    def stretch_up(self):
        self._clear_symbol_and_reminder()
        self._symbol_ring.stretch_up()
        if self.has_attached_gear:
            self._attached_gear.stretch_up()
    def stretch_down(self):
        self._clear_symbol_and_reminder()
        self._symbol_ring.stretch_down()
        if self.has_attached_gear:
            self._attached_gear.stretch_down()
    def stretch_reset(self):
        self._clear_symbol_and_reminder()
        self._symbol_ring.reset()
        if self.has_attached_gear:
            self._attached_gear.stretch_reset()

    # ATTACHING
    def attach(self, gear: 'Gear' = None):
        if self.has_attached_gear:
            self._attached_gear.attach(gear)
        else:
            if not gear: gear = Gear(self._symbols)
            gear._auto_size = self._auto_size
            while gear._symbol_ring.scale < self._symbol_ring.scale:
                gear.stretch_up()
            self._attached_gear = gear
    def detach_left(self):
        return self._delete_gear(self.get_last_gear())
    def detach(self):
        gear = self._attached_gear
        self._attached_gear = None
        return gear, self

    def apply_symbols(self, symbols: str):
        symbols = Symbols.create(symbols)
        if symbols == self._symbols: return
        self._symbols = symbols
        self._clear_symbol_and_reminder()
        self._symbol_ring.apply_symbols(symbols)
        if self.has_attached_gear:
            self._attached_gear.apply_symbols(symbols)

    def check_if_min(self) -> bool:
        return self.is_min and (self.is_last or self._attached_gear.check_if_min())
    def check_if_max(self) -> bool:
        return self.is_max and (self.is_last or self._attached_gear.check_if_max())
    def get_value(self) -> str:
        return f'{self._attached_gear.get_value() if self.has_attached_gear else ""}{self.value}'
    def get_symbols(self) -> Symbols:
        return self._symbols
    def get_indices(self) -> str:
        indices = [] if self.is_last else self._attached_gear.get_indices()
        indices.append(self.index)
        return indices
    def get_length(self, length: int = 0) -> int:
        return self._attached_gear.get_length(length + 1) if self.has_attached_gear else length + 1
    def get_last_gear(self):
        return self._attached_gear.get_last_gear() if self.has_attached_gear else self
    def get_gear_at_index(self, index: int):
        length = self.get_length()
        if index >= length: return None
        return self._return_when_zero_or_decrement(length - 1 - index)
    def get_ring_str(self) -> str:
        ring_str = self._symbol_ring.items_str
        if self.has_attached_gear:
            ring_str = f'{self._attached_gear.get_ring_str()}{ring_str}'
        return ring_str

    def _clear_symbol_and_reminder(self):
        self._reminder = 0
        self._last_symbol = self._symbols.min_value
    def _return_when_zero_or_decrement(self, val: int):
        return self if val == 0 else self._attached_gear._return_when_zero_or_decrement(val - 1)
    def _delete_gear(self, gear):
        if self._attached_gear == gear:
            self._attached_gear = None
            return gear
        elif self.has_attached_gear:
            return self._attached_gear._delete_gear(gear)
        else:
            return self


# GEARS-BASED COUNTER
@dataclass
class Klicznik:
    ns_symbols      : str
    gears_count     : int = 1
    gears_auto_size : bool = True

    def __post_init__(self):
        if not self.ns_symbols: raise ValueError()
        object.__setattr__(self, '_symbols',  Symbols.create(self.ns_symbols))
        delattr(self, 'ns_symbols')
        if self.gears_count < 0: self.gears_count = 0
        object.__setattr__(self, '_auto_size', self.gears_auto_size)
        delattr(self, 'gears_auto_size')
        gear = None
        default_gear = None
        for x in range(self.gears_count):
            if x == 0:
                gear = Gear(self._symbols, self._auto_size)
                default_gear = Gear(self._symbols, self._auto_size)
                continue
            gear.attach()
            default_gear.attach()
        object.__setattr__(self, '_gear', gear)
        object.__setattr__(self, '_default_gear', default_gear)
        delattr(self, 'gears_count')
    def __str__(self):
        return self.gear_str

    @property
    def has_gear(self) -> bool:
        return self.length > 0
    @property
    def has_default(self) -> bool:
        return self._default_gear != None
    @property
    def length(self) -> int:
        return self._gear.get_length() if self._gear else 0
    @property
    def is_zero(self) -> bool:
        return self._gear.check_if_min() if self._gear else True
    @property
    def is_one(self) -> bool:
        if self.is_zero or not self._gear: return False
        self.tick_down()
        test = self._gear.check_if_min()
        self.tick_up()
        return test
    @property
    def is_not_zero(self) -> bool:
        return not self.is_zero
    @property
    def is_max(self) -> bool:
        return self._gear.check_if_max() if self._gear else True
    @property
    def symbols(self) -> Symbols:
        return self._symbols
    @property
    def value(self) -> str:
        return self._gear.get_value() if self._gear else ""
    @property
    def indices(self) -> List[int]:
        return self._gear.get_indices() if self._gear else []
    @property
    def gear_str(self) -> str:
        return self.get_gear_str()

    def set(self, indices: List[int], set_as_default: bool = False):
        if not indices or len(indices) == 0:
            print(f'Set indices must be a non empty list!')
        if any(i for i in indices if not isinstance(i, int)):
            print(f'Set indices elements must be integers!')
        if any(i for i in indices if i >= self._symbols.base):
            print(f'Set indices element out of symbols range!')
        self._ensure_gear()
        self._gear.scroll_to_indices(list(indices))
        if set_as_default:
            self._ensure_default()
            self._default_gear.scroll_to_indices(list(indices))
        return self
    def set_value(self, value: str, set_as_default: bool = False):
        return self.set([self._symbols.index(v) for v in value], set_as_default)
    def reset(self, symbols = None):
        symbols = Symbols.create(symbols) if symbols else self._symbols
        self._ensure_gear()
        self._gear.stretch_reset()
        self.clear()
        self.trim_left()
        if symbols != self._symbols:
            self._symbols = symbols
            self._gear.apply_symbols(symbols)
        self.current_as_default()
        return self
    def clear(self):
        if self.has_gear:
            self._gear.scroll_to_start()
        return self

    def apply_symbols(self, symbols: str, set_as_default: bool = False):
        symbols = Symbols.create(symbols)
        if symbols == self._symbols: return
        self._symbols = symbols
        if self.has_gear:
            self._gear.apply_symbols(symbols)
        if set_as_default and self.has_default:
            self._default_gear.apply_symbols(symbols)
        return self
    def apply(self, symbols: str, value: str, set_as_default: bool = False):
        self.apply_symbols(symbols, set_as_default)
        return self.set_value(value, set_as_default)
    def apply_data(self, data: ValueData, set_as_default: bool = False):
        return self.apply(data.symbols, data.pure_value, set_as_default)

    def current_as_default(self):
        self._ensure_default()
        self._default_gear.apply_symbols(self._symbols)
        self._default_gear.scroll_to_indices(self._gear.get_indices())
    def clear_default(self):
        if self._default_gear:
            self._default_gear.scroll_to_start()
        return self
    def restore_default(self):
        if not self.has_default: return
        self.apply_symbols(self._default_gear.get_symbols())
        self._ensure_gear()
        self._gear.scroll_to_indices(self._default_gear.get_indices())
        return self

    def peek_left(self):
        if self.has_gear:
            return self._gear.get_last_gear()
    def peek_right(self):
        if self.has_gear:
            return self._gear
    def peek_at(self, index: int):
        if self.has_gear:
            return self._gear.get_gear_at_index(index)
    def prepend(self, symbol_index: int = 0):
        gear = Gear(self._symbols, self._auto_size, symbol_index)
        if self.has_gear:
            self._gear.attach(gear)
        else:
            self._gear = gear
    def append(self, symbol_index: int = 0):
        gear = Gear(self._symbols, self._auto_size, symbol_index)
        if self.has_gear:
            gear.attach(self._gear)
        self._gear = gear
    def pop_left(self):
        if self.has_gear:
            return self._gear.detach_left()
    def pop_right(self):
        if not self.has_gear: return
        self._gear, right = self._gear.detach()
        return right
    def empty(self):
        if not self.has_gear: return
        self._gear = None
    def trim_left(self, min_length: int = 1):
        while self.length > min_length:
            if not self.peek_left().is_min:
                break
            self.pop_left()
    def align_gears(self, other: 'Klicznik'):
        while self.length < other.length:
            self.append()
        while self.length > other.length:
            self.pop_right()

    def stretch_up(self):
        if self.has_gear:
            self._gear.stretch_up()
    def stretch_down(self):
        if self.has_gear:
            self._gear.stretch_down()
    def stretch_reset(self):
        if self.has_gear:
            self._gear.stretch_reset()

    def tick_up(self):
        self._ensure_gear()
        self._gear.scroll_up()
    def tick_down(self):
        if self.has_gear:
            self._gear.scroll_down()
    def count_to_zero(self) -> int:
        if self.is_zero: return 0
        to_zero = 0
        temp = Gear(self._symbols)
        temp.scroll_to_indices(self.indices)
        while not temp.is_min:
            temp.scroll_down()
            to_zero += 1
        return to_zero

    def _ensure_gear(self):
        if not self.has_gear:
            self._gear = Gear(self._symbols, self._auto_size)
    def _ensure_default(self):
        if not self.has_default:
            self._default_gear = Gear(self._symbols, self._auto_size)


# OPERATIONS ENUM
class Operation(str, Enum):
    # FUNCTIONALS
    SET = '≫'
    RST = '✗' #'⟳'
    CLR = '◯' #⊘
    MEM = '⤽'
    MRC = '⥅' #↺ ⤻
    MCL = 'ℂ'
    # RELATIONALS
    EQ  = '⩵'
    NE  = '≠'
    LT  = '<'
    LE  = '≤'
    GE  = '≥'
    GT  = '>'
    CMP = 'ᰄ'
    # ESSENTIALS
    INC = '↗'
    DCR = '↘'
    EQL = '='
    NEG = '±'
    NRM = '✓'
    # ARITHMETICALS
    ADD = '+'
    SUB = '-'
    MUL = '×'
    DIV = '÷'
    # MORPHINGS
    RBS = '⇆'
    # LOGICALS
    OR  = '∨'
    NOR = '⊽'
    XOR = '⊻'
    AND = '∧'
    NDN = '⊼'
    NOT = '¬'
    def get_opposite(self) -> 'Operation':
        if self == Operation.INC: return Operation.DEC
        if self == Operation.DEC: return Operation.INC
        if self == Operation.ADD: return Operation.SUB
        if self == Operation.SUB: return Operation.ADD
        if self == Operation.MUL: return Operation.DIV
        if self == Operation.DIV: return Operation.MUL
        return self


# COUNTERS-BASED CALCULATING MACHINE
@dataclass
class Kalkulikus:
    ns_symbols          : str           = None
    init_value          : str           = None
    _neg_lever          : Lever         = None
    _main_counter       : Klicznik      = None
    _input_counter      : Klicznik      = None
    _result_counter     : Klicznik      = None
    _support_counter    : Klicznik      = None
    _fp_digits_counter  : Klicznik      = None
    _result_neg_lever   : Lever         = None
    _input_neg_lever    : Lever         = None
    _memory_lever       : Lever         = None

    def __post_init__(self):
        if not self.ns_symbols: self.ns_symbols = NumericSystem.DEC
        symbols = Symbols.create(self.ns_symbols)
        delattr(self, 'ns_symbols')
        self._neg_lever         = Lever('-')
        self._main_counter      = Klicznik(symbols)
        self._input_counter     = Klicznik(self.symbols)
        self._result_counter    = Klicznik(self.symbols)
        self._support_counter   = Klicznik(self.symbols)
        self._fp_digits_counter = Klicznik(NumericSystem.DEC)
        self._result_neg_lever  = Lever('-')
        self._input_neg_lever   = Lever('-')
        self._memory_lever      = Lever('✓')
        if not self.init_value: self.init_value = symbols.min_value
        self.set(ValueData.create(self.init_value, self.symbols))
        delattr(self, 'init_value')

    @property
    def is_negative(self) -> bool:
        return self._neg_lever.is_engaged
    @property
    def is_positive(self) -> bool:
        return not self.is_negative
    @property
    def is_float(self) -> bool:
        return not self._fp_digits_counter.is_zero
    @property
    def length(self) -> int:
        return self._main_counter.length
    @property
    def symbols(self) -> Symbols:
        return self._main_counter._symbols
    @property
    def fp_digits(self) -> int:
        return self._fp_digits_counter.count_to_zero()
    @property
    def value_data(self) -> ValueData:
        return ValueData(self._main_counter.value, self.symbols, self.fp_digits, self.is_negative)

    # PRINTING
    def show_info(self, prfx: str = '', info: str = ''):
        print(f'{prfx[:2].rjust(2)} {info}')
    def show_value(self, prfx: str = '', force: bool = False):
        nsn = self.symbols.ns_name
        value_str = self.value_data.value_str
        counter_str = self.get_counter_str()
        print(f'{prfx[:2].rjust(2)} {nsn} {value_str.ljust(36 - len(nsn))}{counter_str.rjust(45)}')
    def get_counter_str(self):
        if self.length == 0: return ""
        padding = self.symbols.index_padding
        indices = [f"[{str(i).rjust(padding, '0')}]" for i in self._main_counter.indices]
        gear_str = '[-]' if self.is_negative else ''
        if self.fp_digits > 0:
            fp_idx = self.length - self.fp_digits
            gear_str += f'{"".join(indices[:fp_idx])}.{"".join(indices[fp_idx:])}'
        else:
            gear_str += "".join(indices)
        return gear_str

    # FUNCTIONAL:
    def set(self, val: str|int|float|ValueData, silent: bool = False):
        if not self._setup_input(val, self.symbols): return
        self.clear(True)
        self._transfer_to_main(self._input_counter, self._input_neg_lever)
        if not silent: self.show_value(f'{Operation.SET.value}{Operation.SET.value}', True)
    def reset(self, silent: bool = False):
        self.clear(True)
        self.mem_clr(True)
        if not silent: self.show_value(Operation.RST.value)
    def clear(self, silent: bool = False):
        self._neg_lever.clear()
        self._main_counter.clear()
        self._fp_digits_counter.clear()
        if not silent: self.show_value(Operation.CLR.value)
    def mem_set(self, silent: bool = False):
        self._neg_lever.current_as_default()
        self._main_counter.current_as_default()
        self._fp_digits_counter.current_as_default()
        self._memory_lever.engage()
        if not silent: self.show_info(Operation.MEM, self.value_data.value_str)
    def mem_clear(self, silent: bool = False):
        self._neg_lever.clear_default()
        self._main_counter.clear_default()
        self._fp_digits_counter.clear_default()
        self._memory_lever.disengage()
        if not silent: self.show_info(Operation.MCL.value)
    def mem_recall(self, silent: bool = False):
        if not self._memory_lever.is_engaged:
            if not silent: self.show_info(Operation.MRC, 'mempty')
            return
        self._neg_lever.restore_default()
        self._main_counter.restore_default()
        self._fp_digits_counter.restore_default()
        if not silent: self.show_info(Operation.MRC, self.value_data.value_str)
        self.result(silent)

    # RELATIONAL:
    def eq(self, val: str, symbols: str = None) -> bool:
        return self.compare(val, symbols) == 0
    def ne(self, val: str, symbols: str = None) -> bool:
        return self.compare(val, symbols) != 0
    def lt(self, val: str, symbols: str = None) -> bool:
        return self.compare(val, symbols) < 0
    def le(self, val: str, symbols: str = None) -> bool:
        return self.compare(val, symbols) <= 0
    def gt(self, val: str, symbols: str = None) -> bool:
        return self.compare(val, symbols) > 0
    def ge(self, val: str, symbols: str = None) -> bool:
        return self.compare(val, symbols) >= 0
    def compare(self, val: str|int|float|ValueData, symbols: str|Symbols = None) -> int:
        if not self._setup_input(val, symbols): return
        if self._input_neg_lever.is_engaged and self.is_positive: return 1
        if self.is_negative and not self._input_neg_lever.is_engaged: return -1
        if self._input_counter.is_zero and self._main_counter.is_zero: return 0
        if self._main_counter.is_zero: return -1
        if self._input_counter.is_zero: return 1
        self._support_counter.apply_data(self.value_data)
        while True:
            self._input_counter.tick_down()
            self._support_counter.tick_down()
            if self._input_counter.is_zero and self._support_counter.is_zero:
                return 0
            if self._input_counter.is_zero: return 1
            if self._support_counter.is_zero: return -1

    # MORPHING:
    def rebase(self, symbols, silent: bool = False):
        symbols = Symbols.create(symbols)
        if symbols == self.symbols: return
        self._setup_input(self.value_data)
        if not silent: self.show_info(Operation.RBS, f'{self.symbols.ns_name}->{symbols.ns_name}')
        try: self._main_counter.apply_symbols(symbols)
        except Exception as ex:
            print(f'Rebase failed!\n{ex}')
            return
        self.clear(True)
        self._transfer_to_main(self._input_counter, self._input_neg_lever)
        self.result(silent)

    # ESSENTIAL
    def increment(self, silent: bool = False):
        if not silent: self.show_info(Operation.INC, f'+{self.symbols[1]}')
        self._tick_up()
        self.result(silent)
    def decrement(self, silent: bool = False):
        if not silent: self.show_info(Operation.DCR, f'-{self.symbols[1]}')
        self._tick_down()
        self.result(silent)
    def negate(self, silent: bool = False):
        if not silent: self.show_info(Operation.NEG, 'negate')
        if self.is_negative: self._neg_lever.disengage()
        else: self._neg_lever.engage()
        self.result(silent)
    def result(self, silent: bool = False):
        if not silent: self.show_value(Operation.EQL)

    # ARITHMETICAL:
    def add(self, val: str|int|float|ValueData, symbols: str|Symbols = None, silent: bool = False):
        if not self._setup_input(val, symbols): return
        if not silent: self.show_info(Operation.ADD, f'{self._input_counter.symbols.ns_name} {val}')
        tick_func = self._tick_up
        if self._input_neg_lever.is_engaged:
            tick_func = self._tick_down
            self._input_neg_lever.disengage()
        self._transfer_to_main(self._input_counter, None, tick_func)
        self.result(silent)
    def sub(self, val: str|int|float|ValueData, symbols: str|Symbols = None, silent: bool = False):
        if not self._setup_input(val, symbols): return
        if not silent: self.show_info(Operation.SUB, f'{self._input_counter.symbols.ns_name} {val}')
        tick_func = self._tick_down
        if self._input_neg_lever.is_engaged:
            tick_func = self._tick_up
            self._input_neg_lever.disengage()
        self._transfer_to_main(self._input_counter, None, tick_func)
        self.result(silent)
    def mul(self, val: str|int|float|ValueData, symbols: str|Symbols = None, silent: bool = False):
        if not self._setup_input(val, symbols): return
        if not silent: self.show_info(Operation.MUL, f'{self._input_counter.symbols.ns_name} {val}')
        self._result_neg_lever.set_state(self.is_negative != self._input_neg_lever.is_engaged)
        if self._main_counter.is_zero or self._input_counter.is_zero:
            self.clear(True)
            return self.result(silent)
        if self._main_counter.is_one:
            self.clear(True)
            self._transfer_to_main(self._input_counter, self._result_neg_lever)
            return self.result(silent)
        if self._input_counter.is_one:
            self._transfer_to_main(None, self._result_neg_lever)
            return self.result(silent)
        if self.is_negative: self.negate(True)
        self._input_counter.current_as_default()
        self._result_counter.empty()
        for i in range(1, self._main_counter.length + 1):
            state_idx = self._main_counter.length - i
            for s in range(self.symbols.base):
                if self._main_counter.peek_at(state_idx).index == s:
                    self._result_counter.prepend(self._support_counter.pop_right().index)
                    break
                self._input_counter.restore_default()
                while not self._input_counter.is_zero:
                    self._input_counter.tick_down()
                    self._support_counter.tick_up()
        while self._support_counter.length > 0:
            self._result_counter.prepend(self._support_counter.pop_right().index)
        self.clear(True)
        self._transfer_to_main(self._result_counter, self._result_neg_lever)
        self.result(silent)
    def div(self, val: str|int|float|ValueData, symbols: str|Symbols = None, silent: bool = False):
        equal_dividend_and_divisor = self.eq(val, symbols)
        if not equal_dividend_and_divisor:
            self.negate(True)
            equal_dividend_and_divisor = self.eq(val, symbols)
            self.negate(True)
        if not self._setup_input(val, symbols): return
        if not silent: self.show_info(Operation.DIV, f'{self._input_counter.symbols.ns_name} {val}')
        self._result_neg_lever.set_state(self.is_negative != self._input_neg_lever.is_engaged)
        if self._input_counter.is_zero:
            print('Attempted to divide by zero!')
            return self.result(silent)
        if self._main_counter.is_zero:
            return self.result(silent)
        if equal_dividend_and_divisor:
            self.clear(True)
            self.increment(True)
            self._transfer_to_main(None, self._result_neg_lever)
            return self.result(silent)
        if self._input_counter.is_one:
            self._transfer_to_main(None, self._result_neg_lever)
            return self.result(silent)
        if self.is_negative: self.negate(True)
        while True:
            self._input_counter.tick_down()
            if self._input_counter.is_zero: break
            self._support_counter.stretch_up()
        reminder = 0
        for i in range(self._main_counter.length):
            idx = self._main_counter.peek_at(i).index + reminder
            reminder = 0
            self._support_counter.clear()
            for _ in range(idx):
                self._support_counter.tick_up()
            self._result_counter.append(self.symbols.index(self._support_counter.peek_right().symbol))
            reminder = self._support_counter.peek_right().reminder * self.symbols.base
        self.clear(True)
        self._transfer_to_main(self._result_counter)
        if self._result_neg_lever.is_engaged: self.negate(True)
        self.result(silent)
    def mul_old(self, val: str|int|float|ValueData, symbols: str|Symbols = None, silent: bool = False):
        try: val_data = ValueData.create(val, symbols if symbols else self.symbols)
        except Exception as ex:
            print(f'Operation {Operation.MUL} has been aborted due to invalid input!\n{ex}')
            return
        if not silent: self.show_info(Operation.MUL, f'{val_data.symbols.ns_name} {val_data.value_str}')
        self_data = self.value_data
        self._result_neg_lever.clear()
        if self_data.is_negative != val_data.is_negative:
            self._result_neg_lever.engage()
        if self.is_negative: self.negate(True)
        if self_data.is_zero or val_data.is_zero:
            self.clear(True)
            return self.result(silent)
        if self_data.is_one:
            if self_data.is_negative:
                val_data = val_data.get_opposite()
            self.set(val_data, True)
            return self.result(silent)
        if val_data.is_one:
            if self._result_neg_lever.is_engaged:
                self.negate(True)
            return self.result(silent)
        self._reset_counters()
        self._input_counter.apply_data(val_data, True)
        self._result_counter.pop_right()
        for i in range(1, self._main_counter.length + 1):
            state_idx = self._main_counter.length - i
            for s in range(self.symbols.base):
                if self._main_counter.peek_at(state_idx).index == s:
                    self._result_counter.prepend(self._support_counter.pop_right().index)
                    break
                self._input_counter.restore_default()
                while not self._input_counter.is_zero:
                    self._input_counter.tick_down()
                    self._support_counter.tick_up()
        while self._support_counter.length > 0 and self._support_counter.peek_right().index > 0:
            self._result_counter.prepend(self._support_counter.pop_right().index)
        self.clear(True)
        self._transfer_to_main(self._result_counter)
        if self._result_neg_lever.is_engaged: self.negate(True)
        self.result(silent)
    def div_old(self, val: str|int|float|ValueData, symbols: str|Symbols = None, silent: bool = False):
        try: val_data = ValueData.create(val, symbols if symbols else self.symbols)
        except Exception as ex:
            print(f'Operation {Operation.DIV} has been aborted due to invalid input!\n{ex}')
            return
        if not silent: self.show_info(Operation.DIV, f'{val_data.symbols.ns_name} {val_data.value_str}')
        if val_data.is_zero:
            print('Attempted to divide by zero!')
            return self.result(silent)
        self_data = self.value_data
        self._result_neg_lever.clear()
        if self_data.is_negative != val_data.is_negative:
            self._result_neg_lever.engage()
        if self.is_negative: self.negate(True)
        if self_data.is_zero: return self.result(silent)
        if val_data.is_one:
            if self._result_neg_lever.is_engaged:
                self.negate(True)
            return self.result(silent)
        if val_data.pure_value == self_data.pure_value:
            self.clear(True)
            self.increment(True)
            if self._result_neg_lever.is_engaged:
                self.negate(True)
            return self.result(silent)
        self._reset_counters()
        self._input_counter.apply_data(val_data)
        while True:
            self._input_counter.tick_down()
            if self._input_counter.is_zero: break
            self._support_counter.stretch_up()
        reminder = 0
        for i in range(self._main_counter.length):
            idx = self._main_counter.peek_at(i).index + reminder
            reminder = 0
            self._support_counter.clear()
            for _ in range(idx):
                self._support_counter.tick_up()
            self._result_counter.append(self.symbols.index(self._support_counter.peek_right().symbol))
            reminder = self._support_counter.peek_right().reminder * self.symbols.base
        self.clear(True)
        self._transfer_to_main(self._result_counter)
        if self._result_neg_lever.is_engaged: self.negate(True)
        self.result(silent)

    # INTERNAL:
    def _tick_up(self, force: bool = False):
        if self.is_negative and not force: return self._tick_down(True)
        self._main_counter.tick_up()
    def _tick_down(self, force: bool = False):
        if self._main_counter.is_zero and self.is_positive: self.negate(True)
        if self.is_negative and not force: return self._tick_up(True)
        self._main_counter.tick_down()
        if self._main_counter.is_zero and self.is_negative: self.negate(True)
    def _setup_input(self, val: str|int|float|ValueData, symbols: str|Symbols = None) -> bool:
        self._reset_counters()
        try:
            val_data = ValueData.create(val, symbols if symbols else self.symbols)
            self._input_counter.apply_data(val_data)
            self._input_neg_lever.set_state(val_data.is_negative)
            return True
        except Exception as ex:
            print(f'Failed to setup input counter.\n{ex}')
            return False
    def _transfer_to_main(self, source_counter: Klicznik = None, source_lever: Lever = None, op_func: Callable = None):
        if source_counter:
            if not op_func: op_func = self._tick_up
            while source_counter.is_not_zero:
                source_counter.tick_down()
                op_func.__call__()
        if source_lever:
            self._neg_lever.set_state(source_lever.is_engaged)
    def _reset_counters(self):
        self._input_neg_lever.reset()
        self._result_neg_lever.reset()
        self._input_counter.reset(self.symbols)
        self._result_counter.reset(self.symbols)
        self._support_counter.reset(self.symbols)


@dataclass
class SomeClass:
    some_prop       : int = 12
    some_str_prop   : str = '144'
    def __post_init__(self):
        for field in fields(self):
            print(field.name)
            print(field.type)
            print(field.default)
            print(field.default_factory)
            print(field.metadata)

            value = getattr(self, field.name)
            #print(f'{field.name} = {value}')
            object.__setattr__(self, f'_{field.name}', value)
            delattr(self, field.name)
    @property
    def some_property(self) -> int:
        return self._some_prop
    @property
    def some_str_property(self) -> str:
        return self._some_str_prop

def test2():
    #some_obj = SomeClass()
    #print(some_obj.some_property)
    #print(some_obj.some_str_property)

    #print(isinstance(Lever.is_engaged, property)) # True
    #lever = Lever('+')
    #print(isinstance(lever.is_engaged, property)) # False
    #return
    #return
    print()
    '''
    print(f"0 -> {ValueData.create('0', NumSys.DEC.value)}")
    print(f"100 -> {ValueData.create('100', NumSys.DEC.value)}")
    print(f"010 -> {ValueData.create('010', NumSys.DEC.value)}")
    print(f"00100 -> {ValueData.create('00100', NumSys.DEC.value)}")
    print(f"1.00 -> {ValueData.create('1.00', NumSys.DEC.value)}")
    print(f"1.01 -> {ValueData.create('1.01', NumSys.DEC.value)}")
    print(f"1.11 -> {ValueData.create('1.11', NumSys.DEC.value)}")
    print(f"1.100 -> {ValueData.create('1.100', NumSys.DEC.value)}")
    print(f"000.0110 -> {ValueData.create('000.0110', NumSys.DEC.value)}")
    print(f"010.0110 -> {ValueData.create('010.0110', NumSys.DEC.value)}")
    print()
    cd1 = ValueData.create('010.0110', NumSys.DEC.value)
    cd2 = ValueData.create('1.11', NumSys.DEC.value)
    print(cd1)
    print(cd2)
    ValueData.align_fp_digits(cd1, cd2)
    print(cd1)
    print(cd2)
    cd = ValueData.create('010.011000', NumSys.DEC.value)
    print(cd)
    cd.pure_value = f'00{cd.pure_value}'
    print(cd)
    cd.clean_zeros()
    print(cd)
    #return


    calc = Kalkulikus(NumericSystem.DEC.value, '0.1')
    calc.add('0.02')
    calc.mul('0.4')
    calc.div('0.12')
    calc.mul('4')
    calc.div('2')
    #calc.negate()
    calc.mul('1.5')
    calc.add('-3.5')
    calc.add('8.1')
    calc.div('1.5')
    calc.mul('2.000')
    calc.set('12')
    calc.mul('12')


    return
    calc = Kalkulikus(NumericSystem.DEC.value, '5')
    calc.add('0.5')
    calc.sub('2.255')
    calc.add('0.05')
    calc.increment()
    calc.increment()
    calc.increment()
    calc.norm()
    calc.increment()
    calc.increment()
    calc.norm()
    calc.sub(6)
    calc.memory()
    calc.add(12)
    calc.recall()
    '''
    #return
    print()

    #calc = Kalkulikus()
    #calc.set(855)
    #calc.mul('C', NumericSystem.HEX)
    #calc.set(85)
    #calc.mul('C', NumericSystem.HEX)

    #return

    #calc = Kalkulikus(NumericSystem.HEX.value, '54BD')
    #calc = Kalkulikus(NumericSystem.HEX.value, '1E60')
    #calc = Kalkulikus(NumericSystem.HEX.value, '1B3A')
    calc = Kalkulikus()
    calc.rebase(NumericSystem.HEX)
    calc.set('1B3A')
    calc.mul(-6)
    calc.mem_set()
    calc.div(-6)
    calc.rebase(NumericSystem.DEC)
    calc.add(12)
    calc.mem_recall()
    calc.rebase(NumericSystem.OCT)
    calc.negate()
    calc.div(66)
    calc.rebase(NumericSystem.BIN)
    calc.add(69, NumericSystem.DOZ)
    calc.rebase(NumericSystem.DEC)
    calc.mul('C', NumericSystem.HEX)
    return
    calc.rebase(NumericSystem.MAY)
    calc.rebase(NumericSystem.TSL)
    calc.rebase(NumericSystem.DEC)
    #print(calc.diff(ValueData.create('453', NumericSystem.DEC)))
    #print(calc.diff(ValueData.create('853', NumericSystem.DEC)))
    #print(calc.diff_old(ValueData.create('453', NumericSystem.DEC)))
    #calc.mul('3')
    #calc.add('3')
    #calc.sub(4, NumericSystem.DEC.value )
#    calc.recall()
#    calc.div2('6')
    #calc.recall()
    #calc.div_working_counter('6')
    #calc.rebase(NumericSystem.DEC.value)
    #calc.mul(3)
    #calc.memory()
    #calc.sub('369E')
    #calc.neg()
    return
    calc.add('1100', NumericSystem.BIN.value)
    calc.add(144, NumericSystem.DEC.value)
    #calc.rebase(NumericSystem.OCT.value)
    #calc.rebase(NumericSystem.BIN.value)
    calc.add(69, NumericSystem.DOZ.value)
    calc.undo()
    calc.rebase(NumericSystem.DEC.value)
    calc.increment()
    calc.increment()
    calc.decrement()
    calc.add('A', NumericSystem.HEX.value)
    calc.mul(3, NumericSystem.DEC.value)
    calc.recall()
    print()

def test():
    calc = Kalkulikus()
    calc.set(6969)
    calc.rebase(NumSys.HEX)
    calc.increment()
    calc.mul(-6)
    calc.add(3)
    calc.sub(3)
    calc.sub(-3)
    calc.add(-3)
    calc.div(-6)
    calc.add(3)
    calc.sub(3)
    calc.sub(-3)
    calc.add(-3)
    calc.decrement()

def test3():
    calc = Kalkulikus()



def run_tests():
    print('run_tests')
    #test2()
    test2()
    #print('⩵ ≥⩾ ≤⩽')


if __name__ == '__main__':
    print('Hello Kalkulikus!')
    run_tests()
