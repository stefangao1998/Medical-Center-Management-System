"""
    The module is about Center.
"""
import sys
import data
import math

class Center(object):
    def __init__(self, name):
        self.name = name

    def set_rate(self, patient, rate):
        if rate.isdigit():
            dm = data.DataModel('../db/patient_centres_rate.csv')
            if dm.find(mode="strict", email=patient, name=self.name) == []:
                dm.insert(rate=rate, email=patient, name=self.name)
            else:
                dm.update('rate',rate, email=patient, name=self.name)

    def get_rate(self):
        dm = data.DataModel('../db/patient_centres_rate.csv')
        res = dm.find(mode="strict", name=self.name)
        if res == []:
            return 0
        rate_list = list(map(lambda x:int(x['rate']),filter(lambda x:x['rate'].isdigit(), res)))
        return sum(rate_list)/float(len(rate_list))
    
    def info(self):
        dm = data.DataModel('../db/health_centres.csv')
        res = dm.find(mode="strict", name=self.name)[0]
        return res

    def list_providers(self):
        dm1 = data.DataModel('../db/provider_health_centre.csv')
        f1 = dm1.find(mode="strict", health_centre_name=self.name)

        return f1   


        
if __name__ == '__main__':
    pass
    