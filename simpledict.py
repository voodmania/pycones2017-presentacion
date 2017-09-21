from collections import namedtuple

DictElement = namedtuple('DictElement', 'hash key value')
EMPTY = DictElement(None, None, None)
DELETED = DictElement(None, None, None)


class SimpleDict(object):
    def __init__(self):
        self._num_elements = 0
        self._num_bits_mask = 3
        self._set_size()
        self._table = [EMPTY for i in range(self._table_size)]
        print('SimpleDict.__init__ size: {} mask:{}'.format(self._table_size, hex(self._mask)))

    @staticmethod
    def _get_hash(key):
        key_hash = hash(key)
        key_hash += 2 ** 64 if key_hash < 0 else 0  # 2's complement
        return key_hash

    @staticmethod
    def _get_index(key_hash, mask):
        index = key_hash & mask
        yield index
        perturb = key_hash
        while True:
            index = (5 * index + perturb + 1) & 0xffffffffffffffff
            index &= mask
            yield index
            perturb >>= 5

    def _set_size(self):
        self._table_size = 2 ** self._num_bits_mask
        self._mask = self._table_size - 1

    def _resize(self):
        old_table = self._table
        self._num_bits_mask += 1
        self._set_size()
        self._table = [EMPTY for i in range(self._table_size)]
        for element in old_table:
            if element is not EMPTY and element is not DELETED:
                for index in SimpleDict._get_index(element.hash, self._mask):
                    if self._table[index] is EMPTY:
                        self._table[index] = element
                        break
            

    def add(self, key, value):
        key_hash = SimpleDict._get_hash(key)
        for index in SimpleDict._get_index(key_hash, self._mask):
            if not self._table[index].hash:
                self._table[index] = DictElement(key_hash, key, value)
                self._num_elements += 1
                print(f'{key}:{value} ({key_hash:64b}) added at index: {index}')
                if self._num_elements > 2 / 3 * self._table_size:
                    self._resize()
                return
            elif self._table[index].hash == key_hash:
                self._table[index] = DictElement(key_hash, key, value)
                return
            else:
                print(f'{key}:{value} ({key_hash:64b}) collision at index: {index}')

    def get(self, key):
        if self._num_elements:
            key_hash = SimpleDict._get_hash(key)
            for index in SimpleDict._get_index(key_hash, self._mask):
                element = self._table[index]
                if element is EMPTY:
                    raise KeyError
                elif element.hash == key_hash:
                    return element.value
        else:
            raise KeyError

    def delete(self, key):
        if self._num_elements:
            key_hash = SimpleDict._get_hash(key)
            for index in SimpleDict._get_index(key_hash, self._mask):
                element = self._table[index]
                if element is EMPTY:
                    raise KeyError
                elif element.hash == key_hash:
                    self._table[index] = DELETED
                    return
        else:
            raise KeyError

    def __repr__(self):
        row_format = '|index|hash' + (' ' * 60) + '|key     |value   |'
        rows = ['-' * len(row_format), row_format, '-' * len(row_format)]
        rows.extend([
            '|{}|{:>64}|{:>8}|{:>8}|'.format(
                f'{i:05b}', f'{e.hash:064b}' if e.hash else '', e.key or '', e.value or '')
            for i, e in enumerate(self._table)
        ])
        rows.append('-' * len(row_format))
        return '\n'.join(rows)


if __name__ == '__main__':
    d = SimpleDict()
    d.add('a', 1)
    d.add('b', 2)
    d.add('c', 3)
    d.add('d', 4)
    d.add('e', 5)
    # estado inicial del diccionario
    print(d)

    d.add('f', 6)
    # se dobla el tamaño de la tabla
    print(d)

    d.add('f', 66)
    # modificamos el valor asociado a una clave
    print(d)

    # obtenemos el valor asociado a una clave
    print(f'a: {d.get("a")}')
    print(f'b: {d.get("b")}')

    try:
        d.get('otro')
    except KeyError:
        # la clave no se encuentra en el diccionario
        print('clave no encontrada')

    d.delete('a')
    # estado tras borrar una clave
    print(d)
    try:
        d.get('a')
    except KeyError:
        # la clave ya no se encuentra en el diccionario
        print('clave no encontrada')

    d.add('a', 11)
    # añadimos de nuevo la clave-valor, ocupa el mismo índice
    print(d)
