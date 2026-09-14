def dec2any(source: int, target_symbols: str) -> str:
    neg = source < 0
    dec = abs(source)
    result = ''
    while dec > 0:
        dec, mod = divmod(dec, len(target_symbols))
        result += target_symbols[mod]
    if neg: result += '-'
    return result[::-1]

def any2dec(source: str, source_symbols: str) -> int:
    neg = source.startswith('-')
    src = source[::-1] if not neg else source[::-1][:-1]
    result = 0
    for x in range(len(src)):
        result += source_symbols.index(src[x]) * len(source_symbols) ** x
    return result if not neg else -result

def any2any(source: str, source_symbols: str, target_symbols: str) -> str:
    return dec2any(any2dec(source, source_symbols), target_symbols)

# -----------------------------------------------------------------------

def any_to_any(source: str, source_symbols: str, target_symbols: str):
    symbols_map = _get_symbols_map(source_symbols, target_symbols)
    neg = source.startswith('-')
    src = source[::-1] if not neg else source[::-1][:-1]
    result = ''
    if len(source_symbols) == len(target_symbols):
        for v in src:
            result += symbols_map[v]
    elif len(source_symbols) > len(target_symbols):
        for v in src:
            result += _any_to_any_single(v, source_symbols, target_symbols, symbols_map)
    else:
        chunk_size = len(next(iter(symbols_map)))
        size_mod = len(src) % chunk_size
        if size_mod > 0:
            src += source_symbols[0] * size_mod
        while len(src) > 0:
            result += symbols_map[src[:chunk_size]]
            src = src[chunk_size:]
    if neg: result += '-'
    return result[::-1]

def _any_to_any_single(source: str, source_symbols: str, target_symbols: str, symbols_map):
    target_size = len([m for m in symbols_map if symbols_map[m]])
    source_size = len(source_symbols)
    source_val = source_symbols.index(source)
    result = ''
    current_pos = source_size - 1
    current_val = 0
    while current_pos > 0:
        if symbols_map[current_pos]:
            if current_val + current_pos <= source_val:
                result += target_symbols[min(current_pos, len(target_symbols) - 1)]
                current_val += current_pos
            else:
                result += target_symbols[0]
        current_pos -= 1
    return result[::-1]

def _get_symbols_map(source_symbols: str, target_symbols: str):
    symbols_map = {}
    if len(source_symbols) == len(target_symbols):
        for x in range(len(target_symbols)):
            symbols_map[source_symbols[x]] = target_symbols[x]
    elif len(source_symbols) < len(target_symbols):
        reverse_map = _get_symbols_map(target_symbols, source_symbols)
        for x in range(len(target_symbols)):
            symbols_map[_any_to_any_single(target_symbols[x], target_symbols, source_symbols, reverse_map)] = target_symbols[x]
    else:
        target_base = len(target_symbols)
        current_exp = 0
        for x in range(len(source_symbols)):
            symbols_map[x] = x == target_base ** current_exp
            if symbols_map[x]:
                current_exp += 1
    return symbols_map


def _get_symbols_map2(source_symbols: str, target_symbols: str):
    symbols_map = {}
    if len(source_symbols) == len(target_symbols):
        for x in range(len(target_symbols)):
            symbols_map[source_symbols[x]] = target_symbols[x]
    elif len(source_symbols) < len(target_symbols):
        reverse_map = _get_symbols_map(target_symbols, source_symbols)
        for x in range(len(target_symbols)):
            symbols_map[_any_to_any_single(target_symbols[x], target_symbols, source_symbols, reverse_map)] = target_symbols[x]
    else:
        target_base = len(target_symbols)
        current_exp = 0
        nearest_val = target_base ** current_exp
        for x in range(len(source_symbols)):
            if x < len(target_symbols):
                symbols_map[source_symbols[x]] = target_symbols[x]
            else:
                temp_res = ''
                temp_total = 0

            if x == nearest_val:
                symbols_map[x] = True
                current_exp += 1
                nearest_val = target_base ** current_exp
            else:
                symbols_map[x] = False
    return symbols_map



def _get_symbols_map_new(source_symbols: str, target_symbols: str):
    result = {}
    src_base = len(source_symbols)
    if src_base == len(target_symbols):
        for x in (range(src_base)):
            result[target_symbols[x]] = source_symbols[x]
    elif src_base > len(target_symbols):
        for k, v in _get_symbols_map_new(target_symbols, source_symbols).items():
            result[v] = k
    else:
        max_len = 1
        for value in range(len(target_symbols)):
            if value == 0:
                rep = source_symbols[0]
            else:
                rep = ''
                n = value
                while n > 0:
                    n, mod = divmod(n, src_base)
                    rep = source_symbols[mod] + rep
            result[target_symbols[value]] = rep[::-1] # nie zawsze, tylko gdy binarny
            max_len = max(max_len, len(rep))
        for k in result: # tutaj tez, tylko kiedy sa liczby binarne
            result[k] = result[k].rjust(max_len, source_symbols[0])
        temp_result = {}
        for k,v in result.items():
            temp_result[v] = k
        result = temp_result
    return result



def convert(source: str, source_symbols: str, target_symbols: str):
    symbols_map = _get_symbols_map_new(source_symbols, target_symbols)
    neg = source.startswith('-')
    src = source[::-1] if not neg else source[::-1][:-1]
    chunk_size = len(next(iter(symbols_map)))
    result = ''
    while len(src) > 0:
        cur_chunk_size = chunk_size
        chunk = src[:cur_chunk_size]
        while cur_chunk_size > 1 and chunk not in symbols_map:
            cur_chunk_size -= 1
            chunk = src[:cur_chunk_size]
        result += symbols_map[chunk] if chunk in symbols_map else '!'
        src = src[cur_chunk_size:]
    if neg: result += '-'
    return result[::-1]


def convert2(source: str, source_symbols: str, target_symbols: str):
    src = source[::-1]
    src_base = len(source_symbols)
    src_map = source_symbols
    for x in range(1, len(src)):
        src_map += source_symbols * source_symbols.index(src[x]) * (src_base ** (x - 1))
    tgt_map = target_symbols * ((len(src_map) // len(target_symbols)))
    src_map = src_map[:src_map.rindex(src[0]) + 1]
    tgt_map = tgt_map[:len(src_map)]
    print(tgt_map)

    d, m = divmod(len(tgt_map), len(target_symbols))
    result = f'{target_symbols[m-1]}'
    while d >= len(target_symbols):
        d, m = divmod(d, len(target_symbols) - 1)
        result += f'{target_symbols[m-1]}'
    result += f'{target_symbols[d]}'
    #result = f'{target_symbols[d]}{target_symbols[m-1]}'
    return result[::-1]
    #result += f'{target_symbols[m]}'
    return f'{target_symbols[d]}{tgt_map[-1]}'
    while d >= len(target_symbols):
        d, m = divmod(d, len(target_symbols) - 1)
        result += f'{target_symbols[m]}'
    result += f'{target_symbols[d]}'
    return result

    repeats = 0
    while len(tgt_map) > len(target_symbols):
        tgt_map = tgt_map[len(target_symbols):]
        repeats += 1

    result = target_symbols[repeats] + tgt_map[-1]
    return result

def convert3(source: str, source_symbols: str, target_symbols: str):
    src = source[::-1]
    src_base = len(source_symbols)
    src_map = source_symbols
    for x in range(1, len(src)):
        src_map += source_symbols * source_symbols.index(src[x]) * (src_base ** (x - 1))
    tgt_map = target_symbols * ((len(src_map) // len(target_symbols)))
    src_map = src_map[:src_map.rindex(src[0]) + 1]
    tgt_map = tgt_map[:len(src_map)]
    result = ''
    d = len(tgt_map)
    while d >= len(target_symbols):
        d, m = divmod(d, len(target_symbols))
        result += f'{target_symbols[m-1]}'
    result += f'{target_symbols[d]}'
    return result[::-1]

def convert3_fast(source: str, source_symbols: str, target_symbols: str):
    src = source[::-1]
    src_base = len(source_symbols)
    tgt_base = len(target_symbols)
    length = source_symbols.index(src[0]) + 1
    for pos in range(1, len(src)):
        digit = source_symbols.index(src[pos])
        length += digit * (src_base ** pos)
    d = length
    result = ''
    while d >= tgt_base:
        d, m = divmod(d, tgt_base - 1)
        result += target_symbols[m - 1]
    result += target_symbols[d]
    return result[::-1]

def convert_simple(source: str, source_symbols: str, target_symbols: str):
    src_base = len(source_symbols)
    tgt_base = len(target_symbols)
    pos = 0
    multiplier = 1
    for digit in source[::-1]:
        pos += source_symbols.index(digit) * multiplier
        multiplier *= src_base
    if pos == 0:
        return target_symbols[0]
    result = ''
    while pos > 0:
        pos, mod = divmod(pos, tgt_base)
        result += target_symbols[mod]
    return result[::-1]

def mechanical_convert(source: str, source_symbols: str, target_symbols: str):
    source_value = list(source)
    source_counter = [source_symbols[0]]
    target_counter = [target_symbols[0]]
    def tick(counter, symbols):
        pos = len(counter) - 1
        while pos >= 0:
            current = symbols.index(counter[pos])
            if current + 1 < len(symbols):
                counter[pos] = symbols[current + 1]
                return
            counter[pos] = symbols[0]
            pos -= 1
        counter.insert(0, symbols[1])
    while source_counter != source_value:
        tick(source_counter, source_symbols)
        tick(target_counter, target_symbols)
    return ''.join(target_counter)

def mechanical_convert_x(source: str, source_symbols: str, target_symbols: str):
    source_state = [source_symbols.index(s) for s in source.lstrip(source_symbols[0])]
    source_counter = [0]
    target_counter = [0]
    def tick(counter, base):
        i = len(counter) - 1
        while i >= 0:
            counter[i] = (counter[i] + 1) % base
            if counter[i] != 0: break
            i -= 1
        if i < 0: counter.insert(0, 1)
    source_base = len(source_symbols)
    target_base = len(target_symbols)
    ticks = 0
    while source_counter != source_state:
        tick(source_counter, source_base)
        tick(target_counter, target_base)
        ticks += 1
    print(f'{ticks} ticks')
    return ''.join([target_symbols[t] for t in target_counter])

def mechanical_convert2(source, source_symbols, target_symbols):
    src = list(source)
    tgt = [target_symbols[0]]
    src_pos = [source_symbols.index(x) for x in src]
    def tick(counter, base):
        i = len(counter)-1
        while i >= 0:
            counter[i] += 1
            if counter[i] < base:
                return
            counter[i] = 0
            i -= 1
        counter.insert(0,1)
    target = [0]
    while ''.join(source_symbols[x] for x in src_pos) != source:
        tick(src_pos, len(source_symbols))
        tick(target, len(target_symbols))
    return ''.join(target_symbols[x] for x in target)


# TEST:
def test_map():
    src_val = '036'
    src_sys = 'oct'
    tgt_sys = 'hex'
    result = convert3_fast(src_val, SYSTEMS[src_sys], SYSTEMS[tgt_sys])
    print(f"{src_sys}({src_val}) = {tgt_sys}({result})")

# OUTPUT:
#oct(36) = hex(1E)



# OCT(36) = 3 full loops through all OCT symbols + 6
# OCT: 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7
# OCT:                i1              i2              i3           x   = 36
# HEX: 0 1 2 3 4 5 6 7 8 9 A B C D E F 0 1 2 3 4 5 6 7 8 9 A B C D E F
# HEX:                                i1                           x   = 1E

# 01
# 01234
# 01234567
# 0123456789ABCDEF

def test_map232():
    #src_val = '9C'
    src_val = '243'
    #src_val = '10011100'
    #src_sys = 'hex'
    src_sys = 'oct'
    #src_sys = 'bin'
    tgt_sys = 'hex'
    #tgt_sys = 'oct'
    #tgt_sys = 'bin'

    #result = convert(src_val, SYSTEMS[src_sys], SYSTEMS[tgt_sys])
    #print(f"{src_sys}({src_val}) = {tgt_sys}({result})")
    #back_result = convert(result, SYSTEMS[tgt_sys], SYSTEMS[src_sys])
    #print(f"{tgt_sys}({result}) = {src_sys}({back_result})")
    result = convert_simple(src_val, SYSTEMS[src_sys], SYSTEMS[tgt_sys])
    print(f"{src_sys}({src_val}) = {tgt_sys}({result})")
    result_back = convert_simple(result, SYSTEMS[tgt_sys], SYSTEMS[src_sys])
    print(f"{tgt_sys}({result}) = {src_sys}({result_back})")
    result_to_dec = convert_simple(result, SYSTEMS[tgt_sys], SYSTEMS['dec'])
    print(f"{tgt_sys}({result}) = dec({result_to_dec})")

def test_mechanical():
    #src_val = '9C'
    src_val = '0243'
    #src_val = '10011100'
    #src_sys = 'hex'
    src_sys = 'oct'
    #src_sys = 'bin'
    tgt_sys = 'hex'
    #tgt_sys = 'oct'
    #tgt_sys = 'bin'
    result = mechanical_convert(src_val, SYSTEMS[src_sys], SYSTEMS[tgt_sys])
    print(f"{src_sys}({src_val}) = {tgt_sys}({result})")
    result_back = mechanical_convert(result, SYSTEMS[tgt_sys], SYSTEMS[src_sys])
    print(f"{tgt_sys}({result}) = {src_sys}({result_back})")
    result_to_dec = mechanical_convert(result, SYSTEMS[tgt_sys], SYSTEMS['dec'])
    print(f"{tgt_sys}({result}) = dec({result_to_dec})")
    result_to_bin = mechanical_convert(result, SYSTEMS[tgt_sys], SYSTEMS['bin'])
    print(f"{tgt_sys}({result}) = bin({result_to_bin})")
    print(f"bin({result_to_bin}) = {src_sys}({mechanical_convert(result_to_bin, SYSTEMS['bin'], SYSTEMS[src_sys])})")

def test_mechanical2():
    #src_val = '9C'
    src_val = '243'
    #src_val = '10011100'
    #src_sys = 'hex'
    src_sys = 'oct'
    #src_sys = 'bin'
    tgt_sys = 'hex'
    #tgt_sys = 'oct'
    #tgt_sys = 'bin'
    result = mechanical_convert_x(src_val, SYSTEMS[src_sys], SYSTEMS[tgt_sys])
    print(f"{src_sys}({src_val}) = {tgt_sys}({result})")
    result_back = mechanical_convert_x(result, SYSTEMS[tgt_sys], SYSTEMS[src_sys])
    print(f"{tgt_sys}({result}) = {src_sys}({result_back})")
    result_to_dec = mechanical_convert_x(result, SYSTEMS[tgt_sys], SYSTEMS['dec'])
    print(f"{tgt_sys}({result}) = dec({result_to_dec})")
    result_to_bin = mechanical_convert_x(result, SYSTEMS[tgt_sys], SYSTEMS['bin'])
    print(f"{tgt_sys}({result}) = bin({result_to_bin})")
    print(f"bin({result_to_bin}) = {src_sys}({mechanical_convert_x(result_to_bin, SYSTEMS['bin'], SYSTEMS[src_sys])})")


SYSTEMS = {
    'bin': '01',
    'qtr': '0123',
    'oct': '01234567',
    'dec': '0123456789',
    'doz': '0123456789AB',
    'hex': '0123456789ABCDEF',
    'may': '𝋠𝋡𝋢𝋣𝋤𝋥𝋦𝋧𝋨𝋪𝋫𝋬𝋭𝋮𝋯𝋰𝋱𝋲𝋳',
    'tes': '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz&',
}

def test_any_to_any():
    src_val = '34'
    src_sys = 'hex'
    tgt_systems = ['bin']
    for tgt_sys in tgt_systems:
        result = any_to_any(src_val, SYSTEMS[src_sys], SYSTEMS[tgt_sys])
        print(f"{src_sys}({src_val}) = {tgt_sys}({result})")
        back_result = any_to_any(result, SYSTEMS[tgt_sys], SYSTEMS[src_sys])
        print(f"{tgt_sys}({result}) = {src_sys}({back_result})")
        continue
        for other_tgt_sys in tgt_systems:
            if other_tgt_sys == tgt_sys: continue
            other_result = any_to_any(result, SYSTEMS[tgt_sys], SYSTEMS[other_tgt_sys])
            print(f"{tgt_sys}({result}) = {other_tgt_sys}({other_result})")
            other_back_result = any_to_any(other_result, SYSTEMS[other_tgt_sys], SYSTEMS[tgt_sys])
            print(f"{other_tgt_sys}({other_result}) = {tgt_sys}({other_back_result})")
            print()
        print()


def test_numbers(numbers: list[int]):
    for num in numbers:
        conv = {}
        print(f'\n{num}:')
        for ns in SYSTEMS:
            conv[ns] = dec2any(num, SYSTEMS[ns])
        for c in conv:
            conv_line = f'{c}({conv[c]})'
            for ns in SYSTEMS:
                if ns == c: continue
                conv_line += f' = {ns}({any2any(conv[c], SYSTEMS[c], SYSTEMS[ns])})'
            print(conv_line)
        print()

def test():
    numbers = [3, 6, 9, 12, 33, 36, 39, 63, 66, 69, 93, 96, 99, 369, 693, 963, 999]
    test_numbers(numbers)
    print('\n\nNegatives:\n')
    test_numbers([-n for n in numbers])



def run_tests():
    print('run_tests')
    #test()
    #test_map232()
    test_mechanical2()
    #test_mechanical2()
    #test_any_to_any()


if __name__ == '__main__':
    print('Hello Numerics!')
    run_tests()
