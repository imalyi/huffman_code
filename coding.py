class HeapIsEmpty(Exception):
    pass


class Symbol:
    def __init__(self, char: str, frequency: int) -> None:
        self.char = char
        self.frequency = frequency
        self.code = None

    def __str__(self):
        return f"{self.char}({chr(self.char)}): {self.frequency}: {self.code}"

    def __repr__(self):
        return f"{self.char}({chr(self.char)}): {self.frequency}: {self.code}"


class Node:
    def __init__(self, value: int = None, symbol: Symbol = None, left=None, rigth=None) -> None:
        self.symbol = symbol
        if not value:
            self.value = symbol.frequency
        else:
            self.value = value
        self.left = left  # left child
        self.right = rigth  # right child

    def __int__(self) -> int:
        return self.symbol.frequency

    def __str__(self):
        if not self.symbol:
            return f"{self.value}: {self.left}-{self.right}"
        return f"{self.symbol}"

    def __repr__(self):
        return f"{self.symbol}: {self.left}-{self.right}"


class Heap:
    """Primitive heap"""
    def __init__(self, sort_key=lambda x: x, init_arr=None):
        if init_arr is None:
            init_arr = []

        self.__sort_key = sort_key
        self.__heap = init_arr.copy()
        self.__sort()

    def get_min(self) -> Node:
        if not self.empty:
            min = self.__heap[-1]
            self.__heap = self.__heap[0:len(self.__heap)-1]
            self.__sort()
            return min
        raise HeapIsEmpty

    def __sort(self):
        self.__heap.sort(key=self.__sort_key, reverse=True)

    def put(self, el):
        self.__heap.append(el)
        self.__sort()

    @property
    def empty(self):
        if len(self.__heap) == 0:
            return True
        return False


class File:
    def __init__(self, filename: str) -> None:
        self.__text = None
        self.filename = filename

    @property
    def text(self) -> str:
        if not self.__text:
            with open(self.filename, 'rb') as f:
                self.__text = f.read()
        return self.__text


class Text:
    def __init__(self, file: File):
        self.file = file
        self.__symbols = None
        self.text = self.file.text

    @property
    def symbols(self) -> list:
        tmp = {}
        if self.__symbols == None:
            self.__symbols = []
            for symbol in list(self.file.text):
                if not tmp.get(symbol):
                    tmp[symbol] = 0
                tmp[symbol] += 1
            for symbol, freq in tmp.items():
                self.__symbols.append(Symbol(symbol, freq))
        return self.__symbols


class Tree:
    def __init__(self, text: Text) -> None:
        self.text = text
        self.__build_tree()
        self.__generate_codes('', self._tree)
        self.__print_codes()
        self.current = self._tree

    def __print_codes(self):
        for s in self.text.symbols:
            print(s)

    def get_symbol(self, byte, arr):
        if byte == '0':
            self.current = self.current.left
        else:
            self.current = self.current.right

        if not self.current.left:
            arr.append(chr(self.current.symbol.char))
            self.current = self._tree

    @property
    def dict(self):
        tmp = {}
        for s in self.text.symbols:
            tmp[s.char] = bytes(s.code, 'ascii')
        return tmp

    def __build_tree(self):
        symbols = self.text.symbols.copy()
        symbols = list(map(lambda s: Node(symbol=s), symbols))
        heap = Heap(init_arr=symbols, sort_key=lambda n: n.value,)

        while not heap.empty:
            try:
                left = heap.get_min()
            except HeapIsEmpty:
                self._tree = heap
                return
            try:
                rigth = heap.get_min()
            except HeapIsEmpty:
                self._tree = left
                return
            heap.put(Node(value=left.value + rigth.value, left=left, rigth=rigth))

    def __generate_codes(self, connection_val: str, nex_el: Node):
        if not nex_el:
            return
        self.__generate_codes(connection_val + '0', nex_el.left)
        self.__generate_codes(connection_val + '1', nex_el.right)
        if nex_el.symbol:
            nex_el.symbol.code = connection_val


class Encoder:
    def __init__(self, tree: Tree, text: Text) -> None:
        self.tree = tree
        self.text = text
        self.__encode()
        self.__save()

    @property
    def output_filename(self):
        return f"encoded_{self.text.file.filename}"

    def __encode(self):
        encoded_text = bytes()
        for byte in self.text.file.text:
            encoded_text += self.tree.dict.get(byte)
        self.encoded_text = encoded_text

    def __save(self):
        with open(self.output_filename, 'wb') as f:
            f.write(self.encoded_text)


class Decoder:
    def __init__(self, filename: str, tree: Tree) -> None:
        self.tree = tree
        self.filename = filename
        self._raw_text = b''
        self.__open()
        self.decoded = self.__decode()

    def __open(self):
        with open(self.filename, 'r') as f:
            self._raw_text = f.read()
            
    def __decode(self) -> str:
        res = []
        for byte in self._raw_text:
            self.tree.get_symbol(byte, res)
        return ''.join(res)


if __name__ == "__main__":
    text = Text(File('test.txt'))
    t = Tree(text)

    e = Encoder(t, text)
    d = Decoder('encoded_test.txt', t)

    print('Zakodowany tekst:')
    print(e.encoded_text)

    print('Odkodowany tekst:')

    print(d.decoded)