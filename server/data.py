"""
    The module is used to read and update csv data,
    which is treated as database in this project.
"""
import sys
import traceback

# abstract class of all data model class
class DataModel(object):
    def __init__(self, path):
        self.path = path
        self.fields = []
        self.data = []
        self.load()

    def load(self):
        with open(self.path, 'r') as f:
            self.fields = f.readline().strip().split(',')
            while True:
                rd_in = f.readline().strip()
                if rd_in != "":
                    self.data.append(rd_in.split(','))
                else:
                    return

    def find(self, mode="similar", **field):
        def is_similar(a, b):
            a = a.lower().replace(' ', '')
            b = b.lower().replace(' ', '')
            if a in b or b in a:
                return True
            return False

        index = []
        ret = self.data[:]
        ret_dict = []
        try:
            for key in field:
                index.append(self.fields.index(key))
            for i in index:
                if mode == "strict":
                    ret = filter(lambda x: x[i] == field[self.fields[i]], ret)
                else:
                    ret = filter(lambda x: is_similar(x[i], field[self.fields[i]]), ret)

            for item in ret:
                ret_i = {}
                for k in range(len(item)):
                    ret_i[self.fields[k]] = item[k]
                ret_dict.append(ret_i)
            return ret_dict
        except:
            # print "Select Error ~ ", traceback.format_exc()
            return []

    def update(self, key, value, **fields):
        change_cnt = 0
        idxs = []
        for key in fields:
            idxs.append(self.fields.index(key))

        for i in range(len(self.data)):
            if all(map(lambda k: self.data[i][k] == fields[self.fields[k]], idxs)):
                self.data[i][self.fields.index(key)] = value
                change_cnt += 1
            i+= 1
        self.dump()
        return change_cnt

    def insert(self, **fields):
        if all([True if key in self.fields else False for key in fields]):
            ins = []
            for kk in self.fields:
                ins.append(fields[kk])
            if ins not in self.data:
                self.data.append(ins)
                self.dump()
                return True
        return False


    def dump(self):
        with open(self.path, 'w') as f:
            f.write(','.join(self.fields) + '\n')
            for line in self.data:
                f.write(','.join(line) + '\n')

        
if __name__ == '__main__':
    dm = DataModel('../db/patient.csv')
    dm.find(mode="similar")
    # print dm.update('provider_type', 'GP', provider_type='GP')
    # dm.insert(patient_email="zhou@gmail.com", password="cs1531")