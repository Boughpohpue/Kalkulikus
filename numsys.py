from enum import Enum


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

class NumSysConverter:
    @staticmethod
    def dec2any(source: int, target_symbols: str) -> str:
        neg = source < 0
        dec = abs(source)
        result = ''
        while dec > 0:
            dec, mod = divmod(dec, len(target_symbols))
            result += target_symbols[mod]
        if neg: result += '-'
        return result[::-1]
    @staticmethod
    def any2dec(source: str, source_symbols: str) -> int:
        neg = source.startswith('-')
        src = source[::-1] if not neg else source[::-1][:-1]
        result = 0
        for x in range(len(src)):
            result += source_symbols.index(src[x]) * len(source_symbols) ** x
        return result if not neg else -result
    @staticmethod
    def any2any(source: str, source_symbols: str, target_symbols: str) -> str:
        return NumSysConverter.dec2any(NumSysConverter.any2dec(source, source_symbols), target_symbols)



def test():
    for x in range(1, 51):
        print(f'{x}\t\t -> TRI = {NumSysConverter.any2any(str(x), NumSys.DEC, NumSys.TRI)}\t\t -> SEX = {NumSysConverter.any2any(str(x), NumSys.DEC, NumSys.SEX)}\t\t -> NON = {NumSysConverter.any2any(str(x), NumSys.DEC, NumSys.NON)}\t\t -> DOZ = {NumSysConverter.any2any(str(x), NumSys.DEC, NumSys.DOZ)}')


def run_tests():
    print('run_tests')
    test()


if __name__ == '__main__':
    print('Hello NumSys!')
    run_tests()
