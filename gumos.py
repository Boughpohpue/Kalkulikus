from dataclasses import dataclass
from typing import List
from boughtils.terminals.console import console

@dataclass
class Value:
    value: str
    symbols: str = '0123456789'
    def __post_init__(self):
        if not self.symbols or len(self.symbols) < 2 or len(set(self.symbols)) < len(self.symbols) :
            raise ValueError('Invalid symbols!')
        self.value = str(self.value).upper()
        if any(v for v in list(self.value) if v not in self.symbols):
            raise ValueError('Invalid value!')
    def __str__(self) -> str:
        return f'{self.value} ({self.value_integer})'
    @property
    def base(self) -> int:
        return len(self.symbols)
    @property
    def symbols_elements(self) -> List[str]:
        return list(self.symbols)
    @property
    def length(self) -> int:
        return len(self.value)
    @property
    def value_symbols(self) -> List[str]:
        return list(self.value)
    @property
    def value_reversed(self) -> str:
        return self.value[::-1]
    @property
    def value_integer(self) -> int:
        int_value = 0
        _value = self.value_reversed
        for i in range(self.length):
            _symbols = self.symbols_elements
            _current = 0
            while any(_symbols) and _symbols.pop(0) != _value[i]:
                _current += 1
            int_value += _current * self.base ** i
        return int_value


@dataclass
class GumosConfig:
    gap_char: str = '-'
    mark_char: str = 'x'
    start_char: str = '|'
    space_char: str = ' '
    div_precision: int = 3
    @property
    def chars(self) -> str:
        return f'{self.gap_char}{self.mark_char}{self.start_char}{self.space_char}'


class Gumoś:
    @staticmethod
    def get_ruler(scale: Value, config: GumosConfig = GumosConfig()) -> str:
        gap = config.gap_char * (scale.value_integer - 1)
        return "".join([f'{s}{gap}' for s in scale.symbols_elements])
    @staticmethod
    def get_ruler_line(scale: Value, config: GumosConfig = GumosConfig()) -> str:
        available_width = console.get_terminal_width()
        ruler = Gumoś.get_ruler(scale, config)
        return (ruler * (int(available_width / len(ruler)) + 1))[:available_width]
    @staticmethod
    def get_ruler_lines(ruler_line: str, skip_leading_zeros: bool = True, config: GumosConfig = GumosConfig()) -> List[str]:
        bases = Gumoś.get_ruler_symbols(ruler_line, config)
        base_line = str(ruler_line)
        base_lines = []

        while True:
            _bases = list(bases)
            _ruler_line = list(base_line)
            current_base_handled = False
            base_line = ''
            while _ruler_line:
                if _ruler_line[0] in config.chars:
                    base_line += config.space_char
                elif _ruler_line[0] == bases[0]:
                    if not base_lines:
                        base_line += _bases[0]
                        _bases.append(_bases.pop(0))
                    elif current_base_handled:
                        _bases.append(_bases.pop(0))
                        base_line += _bases[0]
                        current_base_handled = False
                    else:
                        base_line += _bases[0]
                        current_base_handled = True
                elif not base_lines:
                    base_line += config.space_char
                else:
                    base_line += _bases[0]
                _ruler_line.pop(0)
            unique_symbols = set([s for s in base_line if s not in config.chars])
            if len(unique_symbols) == 1 and list(unique_symbols)[0] == bases[0]: break
            base_lines.append(base_line)
            if len(unique_symbols) < len(bases): break

        if skip_leading_zeros:
            for i in range(len(base_lines)):
                base_line = list(base_lines[i])
                new_line = ''
                while any(base_line):
                    if base_line[0] not in [config.space_char, ruler_line[0]]:
                        new_line += "".join(base_line)
                        break
                    new_line += config.space_char
                    base_line.pop(0)
                base_lines[i] = new_line

        base_lines.insert(0, ruler_line)

        return reversed(base_lines)
    @staticmethod
    def get_ruler_lines_for_scale(scale: Value, skip_leading_zeros: bool = True, config: GumosConfig = GumosConfig()) -> List[str]:
        return Gumoś.get_ruler_lines(Gumoś.get_ruler_line(scale, config), skip_leading_zeros, config)
    @staticmethod
    def get_ruler_base_line(ruler_line: str, config: GumosConfig = GumosConfig()) -> str:
        bases = []
        base_definer = ''
        ruler_base_line = ''
        while ruler_line:
            if ruler_line[0] in config.chars:
                ruler_base_line += config.space_char
            elif not base_definer:
                base_definer = ruler_line[0]
                ruler_base_line += config.space_char
            elif ruler_line[0] == base_definer:
                if base_definer not in bases:
                    bases.append(base_definer)
                bases.append(bases.pop(0))
                ruler_base_line += bases[-1]
            elif ruler_line[0] not in bases:
                bases.append(ruler_line[0])
                ruler_base_line += config.space_char
            else:
                ruler_base_line += config.space_char
            ruler_line = ruler_line[1:]
        return ruler_base_line
    @staticmethod
    def get_lines_with_marked_value_elements(value: Value, ruler_line: str, config: GumosConfig = GumosConfig()) -> List[str]:
        value_lines = []
        value_elements = list(value.value)
        start_idx = ruler_line.index(value.symbols[0])
        for i in range(len(value_elements)):
            element_idx = ruler_line.index(value_elements[i])
            if element_idx == start_idx:
                line = f"{config.mark_char}"
            else:
                line = f"{config.start_char}{config.gap_char * (element_idx - start_idx - 1)}{config.mark_char}"
            value_lines.append(line)
        return value_lines
    @staticmethod
    def get_ruler_base(ruler_line: str, config: GumosConfig = GumosConfig()) -> int:
        return len(set([c for c in list(ruler_line) if c not in config.chars]))
    @staticmethod
    def get_ruler_symbols(ruler_line: str, config: GumosConfig = GumosConfig()) -> List[str]:
        _ruler = [c for c in list(ruler_line) if c not in config.chars]
        _symbols = []
        while True:
            _symbols.append(_ruler.pop(0))
            if len(_ruler) == 0:
                break
            if len(_symbols) > 1 and _symbols[0] == _symbols[-1]:
                _symbols.pop()
                break
        return _symbols
    @staticmethod
    def get_ruler_scale(ruler_line: str, config: GumosConfig = GumosConfig()) -> int:
        scale = 1
        _ruler_line_elements = list(ruler_line)
        _ruler_line_elements.pop(0)
        while _ruler_line_elements.pop(0) == config.gap_char:
            scale += 1
        return scale


class GumosOps:
    @staticmethod
    def multiply(value: Value, multiplier: Value, silent: bool = False, config: GumosConfig = GumosConfig()) -> str:
        value_ruler = Gumoś.get_ruler(multiplier, config)
        value_lines = Gumoś.get_lines_with_marked_value_elements(value, value_ruler, config)
        multiplier_ruler = Gumoś.get_ruler(Value(1, value.symbols), config)
        multiplier_ruler = multiplier_ruler * (int(len(value_ruler) / len(multiplier_ruler)))
        result_values = GumosOps._get_values_from_marked_lines_mul(reversed(value_lines), multiplier_ruler, config)
        result = "".join(reversed(result_values))
        if not silent:
            print(f'\nMultiplication: {value.value} × {multiplier.value}\n')
            print(value_ruler)
            print("\n".join(value_lines))
            print(multiplier_ruler)
            print(f'\n{value.value} × {multiplier.value} = {result}\n')
        return result
    @staticmethod
    def _get_value_from_marked_line_mul(marked_value_line: str, ruler_line: str, config: GumosConfig = GumosConfig()) -> str:
        _rbase = list(Gumoś.get_ruler_base_line(ruler_line, config))
        _value = list(marked_value_line)
        _ruler = list(ruler_line)
        _symbol = ''
        _rmindr = ''
        while True:
            _symbol = _ruler.pop(0)
            if _rbase.pop(0) not in config.chars:
                _rmindr += config.gap_char
            if _value.pop(0) == config.mark_char:
                break
            _ruler.append(_symbol)
        return _symbol, _rmindr
    @staticmethod
    def _get_values_from_marked_lines_mul(marked_value_lines: List[str], ruler_line: str, config: GumosConfig = GumosConfig()) -> List[str]:
        _values = []
        _rmindr = ''
        for line in marked_value_lines:
            _line = GumosOps._apply_reminder_to_value_line(_rmindr, line, config)
            _symbol, _rmindr = GumosOps._get_value_from_marked_line_mul(_line, ruler_line, config)
            _values.append(_symbol)
        if _rmindr:
            _values.append(GumosOps._get_reminder_value_mul(_rmindr, ruler_line, config))
        return _values
    @staticmethod
    def _get_reminder_value_mul(reminder: str, ruler_line: str, config: GumosConfig = GumosConfig()) -> str:
        _symbols = Gumoś.get_ruler_symbols(ruler_line, config)
        _ruler = list(ruler_line)
        _rmindr = list(reminder)
        _loop_items = []
        _rem_val = ''
        while _rmindr:
            ruler_pop = _ruler.pop(0)
            if ruler_pop in _loop_items:
                _symbols.append(_symbols.pop(0))
                _loop_items = []
            _loop_items.append(ruler_pop)
            _rmindr.pop(0)
        if _ruler[0] in _loop_items: _symbols.append(_symbols.pop(0))
        return f'{_symbols[0] if _symbols[0] != ruler_line[0] else ""}{_ruler[0]}'

    @staticmethod
    def divide(value: Value, divisor: Value, silent: bool = False, config: GumosConfig = GumosConfig()) -> str:
        divisor_ruler = Gumoś.get_ruler(divisor, config)
        value_ruler = Gumoś.get_ruler(Value(1, value.symbols), config)
        value_lines = Gumoś.get_lines_with_marked_value_elements(value, value_ruler, config)
        result_values = GumosOps._get_values_from_marked_lines_div(value_lines, divisor_ruler, config)
        while len(result_values) > 1 and result_values[0] == value.symbols[0] and not result_values[1].startswith('.'):
            result_values.pop(0)
        result = "".join(result_values)
        if not silent:
            print(f'\nDivision: {value.value} ÷ {divisor.value}\n')
            print(value_ruler)
            print("\n".join(value_lines))
            print(divisor_ruler)
            print(f'\n{value.value} ÷ {divisor.value} = {result}\n')
        return result
    @staticmethod
    def _get_value_from_marked_line_div(marked_value_line: str, ruler_line: str, config: GumosConfig = GumosConfig()) -> str:
        _value = list(marked_value_line)
        _ruler = list(ruler_line)
        _symbol = ''
        _rmindr = ''
        while True:
            _rmindr += _ruler.pop(0)
            if _rmindr[-1] != config.gap_char:
                _symbol = _rmindr[-1]
                _rmindr = ''
            if _value.pop(0) == config.mark_char:
                break
        return _symbol, _rmindr
    @staticmethod
    def _get_values_from_marked_lines_div(marked_value_lines: List[str], ruler_line: str, config: GumosConfig = GumosConfig()) -> List[str]:
        _ruler_base = Gumoś.get_ruler_base(ruler_line)
        _values = []
        _rmindr = ''
        for line in marked_value_lines:
            _line = GumosOps._apply_reminder_to_value_line(_rmindr * _ruler_base, line, config)
            _symbol, _rmindr = GumosOps._get_value_from_marked_line_div(_line, ruler_line, config)
            _values.append(_symbol)
        if _rmindr:
            _values.append(f'.{GumosOps._get_reminder_value_div(_rmindr, ruler_line, config)}')
        return _values
    @staticmethod
    def _get_reminder_value_div(reminder: str, ruler_line: str, config: GumosConfig = GumosConfig()) -> str:
        _scale = Gumoś.get_ruler_scale(ruler_line)
        _rmindr = reminder
        _rmindr_val = ''
        while len(_rmindr_val) < config.div_precision:
            idx = int(len(ruler_line) * len(_rmindr) / _scale)
            _ruler = list(ruler_line[:idx + 1])
            _rmindr = ''
            while True:
                ruler_pop = _ruler.pop()
                if ruler_pop not in config.chars:
                    _rmindr_val += ruler_pop
                    break
                else: _rmindr += ruler_pop
            if not _rmindr: break
        return _rmindr_val

    @staticmethod
    def _apply_reminder_to_value_line(reminder: str, value_line: str, config: GumosConfig = GumosConfig()) -> str:
        _line = str(value_line)
        if reminder:
            if not _line.startswith(config.start_char):
                reminder = f'{config.start_char}{reminder[1:]}'
            _line = _line.replace(config.mark_char, f'{reminder}{config.mark_char}')
        return _line
    @staticmethod
    def _round_value(value: str, symbols: List[str], config: GumosConfig = GumosConfig()) -> str:
        if len(value) < 2 or value[-1] == symbols[-1]: return value
        to_round = value[-2]
        round_dir = value[-1]
        value = value[:-2]
        for x in range(len(symbols)):
            if symbols[x] == round_dir:
                for y in range(len(symbols)):
                    if symbols[y] == to_round:
                        value += symbols[y]
                        return value
            if symbols[-(x + 2)] == round_dir:
                for y in range(len(symbols)):
                    if symbols[y] == to_round:
                        value += symbols[y + 1]
                        return value
        return value


def get_expected_value_str(expected, config):
    _expected = str(expected)
    if _expected.endswith('.0'): _expected = _expected[:-2]
    _fp_sep_idx = _expected.rindex('.') if '.' in _expected else None
    if _fp_sep_idx and len(_expected) - _fp_sep_idx > config.div_precision:
        _expected = _expected[:_fp_sep_idx + config.div_precision + 1]
    return _expected

def test_mul_div():
    config = GumosConfig()
    silent = False
    div_result = GumosOps.divide(Value(5), Value(3), silent, config)
    print(get_expected_value_str(5 / 3, config))
    mul_result = GumosOps.multiply(Value(5), Value(3), silent, config)
    print(get_expected_value_str(5 * 3, config))
    div_result = GumosOps.divide(Value(69037), Value(3), silent, config)
    print(get_expected_value_str(69037 / 3, config))
    mul_result = GumosOps.multiply(Value(69037), Value(3), silent, config)
    print(get_expected_value_str(69037 * 3, config))
    div_result = GumosOps.divide(Value(65037), Value(3), silent, config)
    print(get_expected_value_str(65037 / 3, config))
    mul_result = GumosOps.multiply(Value(65037), Value(3), silent, config)
    print(get_expected_value_str(65037 * 3, config))

def test_mul_div2():
    config = GumosConfig()
    scales = [2, 3, 5, 11, 17]
    values = [5, 69037, 65037, 142857, 789456, 25083, 10002, 987654321]
    silent = True
    show_results = True

    for value in values:
        for scale in scales:
            mul_result = GumosOps.multiply(Value(value), Value(scale), silent, config)
            expected = get_expected_value_str(value * scale, config)
            info = f'{value} × {scale} = EXPECTED: {expected} GOT: {mul_result}'.ljust(69)
            if mul_result != expected or not silent or show_results:
                print(f'{info} {"OK" if expected == mul_result else "BAD"}')
            div_result = GumosOps.divide(Value(value), Value(scale), silent, config)
            expected = get_expected_value_str(value / scale, config)
            info = f'{value} ÷ {scale} = EXPECTED: {expected} GOT: {div_result}'.ljust(69)
            if div_result != expected or not silent or show_results:
                print(f'{info} {"OK" if expected == div_result else "BAD"}')

def test_lines():
    config = GumosConfig()
    ruler_line = Gumoś.get_ruler_line(Value(1), config)
    print('\nRuler:\n')
    print(ruler_line)
    print('\n\nSkip-leading-zeros=False\n')
    print("\n".join(Gumoś.get_ruler_lines(ruler_line, False, config)))
    print('\n\nSkip-leading-zeros=True\n')
    print("\n".join(Gumoś.get_ruler_lines(ruler_line, True, config)))
    print('\n')

def run_tests():
    print('run_tests\n')
    test_mul_div()
    test_mul_div2()
    test_lines()


if __name__ == '__main__':
    print('Hello Gumoś!')
    run_tests()
