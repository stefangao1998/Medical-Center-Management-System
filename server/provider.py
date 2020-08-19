"""
    The module is about provider.
"""
import sys
import data

class Provider(object):
    def __init__(self, email):
        self.email = email

    def authenticater(self, pwd):
        dm = data.DataModel('../db/provider.csv')
        if (dm.find(mode="strict", provider_email=self.email, password=pwd) != []):
            return True
        return False

    def set_rate(self, patient, rate):
        if rate.isdigit():
            dm = data.DataModel('../db/patient_provider_rate.csv')
            if dm.find(mode="strict", provider_email=self.email) == []:
                dm.insert(rate=rate, patient_email=patient, provider_email=self.email)
            else:
                dm.update('rate',rate, patient_email=patient, provider_email=self.email)

    def get_rate(self):
        dm = data.DataModel('../db/patient_provider_rate.csv')
        res = dm.find(mode="strict", provider_email=self.email)
        if res == []:
            return 0
        rate_list = list(map(lambda x:int(x['rate']),filter(lambda x:x['rate'].isdigit(), res)))
        return sum(rate_list)/float(len(rate_list))
    
    def info(self):
        dm = data.DataModel('../db/provider.csv')
        res = dm.find(mode="strict", provider_email=self.email)[0]
        return res

    def list_centers(self):
        dm1 = data.DataModel('../db/provider_health_centre.csv')
        f1 = dm1.find(mode="strict", provider_email=self.email)
        return f1   

    def book_history(self):
        dm = data.DataModel('../db/book.csv')
        f1 = dm.find(mode="similar", provider_email=self.email)
        return sorted(f1, key=lambda x:x["book_time"], reverse=True)

    def consult(self, patient, center, service_time, note, medication_prescribed ):
        dm = data.DataModel('../db/book.csv')
        dm.update('note', note, provider_email=self.email, center_name=center, \
            patient_email=patient, service_time=service_time)

        dm.update('medication_prescribed', medication_prescribed, provider_email=self.email, center_name=center, \
            patient_email=patient, service_time=service_time)
    
    def query_consult(self, patient):
        dm = data.DataModel('../db/book.csv')
        f1 = dm.find(mode="similar", provider_email=self.email, patient_email=patient)
        return sorted(f1, key=lambda x:x["service_time"], reverse=True)

        
if __name__ == '__main__':
    pass
    