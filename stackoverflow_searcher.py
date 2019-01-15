from datetime import datetime
import struct


class Searcher(object):

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__instance.name = "The one"
        return cls.__instance

    def __init__(self):
        self.offset_dict = {}
        try:
            with open('stackoverflow/post_inv_offset.dat', mode='rb') as r:
                cnt = 0
                while True:
                    term_leng = struct.unpack('i', r.read(4))[0]
                    term = r.read(term_leng).decode("utf-8")
                    offset = struct.unpack('i', r.read(4))[0]
                    self.offset_dict[term] = offset
        except:
            print("LOADED")
            pass
        self.idx_fp = open('stackoverflow/post_inv_idx.dat', mode='rb')

    def __del__(self):
        self.idx_fp.close()

    def search(self, term, from_date=datetime(1, 1, 1), until_date=datetime.now()):
        if term not in self.offset_dict:
            return []
        self.idx_fp.seek(self.offset_dict[term])

        whole_leng = struct.unpack('i', self.idx_fp.read(4))[0]
        len_str = struct.unpack('i', self.idx_fp.read(4))[0]
        whole_leng -= len_str
        read_term = self.idx_fp.read(len_str).decode("utf-8")
        assert(read_term==term)
        data = list()
        while whole_leng > 0:
            id, date, wc = struct.unpack('iii', self.idx_fp.read(12))
            wc_dt = datetime.utcfromtimestamp(date)
            whole_leng -= 12
            if from_date < wc_dt < until_date:
                data.append((id, date, wc))
        return data


if __name__ == "__main__":
    s = Searcher()
    print(len(s.search('numpy', datetime(2000, 1, 1), datetime(2009, 1, 1))))
    print(len(s.search('numpy', datetime(2000, 1, 1), datetime(2010, 1, 1))))
    print(len(s.search('numpy', datetime(2000, 1, 1), datetime(2011, 1, 1))))
    print(len(s.search('numpy', datetime(2000, 1, 1), datetime(2012, 1, 1))))
    print(len(s.search('numpy', datetime(2000, 1, 1), datetime(2013, 1, 1))))
    print(len(s.search('numpy', datetime(2000, 1, 1), datetime(2014, 1, 1))))
    print(len(s.search('numpy', datetime(2000, 1, 1), datetime(2015, 1, 1))))
    print(len(s.search('numpy', datetime(2000, 1, 1), datetime(2016, 1, 1))))
    print(len(s.search('numpy', datetime(2000, 1, 1), datetime(2017, 1, 1))))
    print(len(s.search('numpy', datetime(2010, 1, 1), datetime(2017, 1, 1))))
    print(len(s.search('numpy', datetime(2011, 1, 1), datetime(2017, 1, 1))))
    print(len(s.search('numpy', datetime(2012, 1, 1), datetime(2017, 1, 1))))
    print(len(s.search('numpy', datetime(2013, 1, 1), datetime(2017, 1, 1))))
    print(len(s.search('numpy', datetime(2014, 1, 1), datetime(2017, 1, 1))))
    print(len(s.search('numpy', datetime(2015, 1, 1), datetime(2017, 1, 1))))
    print(len(s.search('os')))
    print(len(s.search('pandas')))
    print(len(s.search('datetime')))
    print(len(s.search('scipy')))
