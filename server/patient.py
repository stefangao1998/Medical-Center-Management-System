"""
    The module is about patient.
"""
import sys
import data
import datetime

class Patient(object):
    def __init__(self, email):
        self.email = email

    def search(self, center="", provider="", service=""):
        dm1 = data.DataModel('../db/provider_health_centre.csv')
        f1 = dm1.find(mode="similar", provider_email=provider, health_centre_name=center)

        dm2 = data.DataModel('../db/provider.csv')
        f2 = dm2.find(mode="similar", provider_email=provider, provider_type=service)

        map_email_type = {}
        for item in f2:
            map_email_type[item['provider_email']] = item['provider_type']

        for item in f1:
            item['provider_type'] = map_email_type[item['provider_email']]

        return f1

    def authenticater(self, pwd):
        dm = data.DataModel('../db/patient.csv')
        if (dm.find(mode="strict", patient_email=self.email, password=pwd) != []):
            return True
        return False

    def book(self, provider, center, begin, end, comment):
        dm = data.DataModel('../db/book.csv')
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        return dm.insert(provider_email=provider, center_name=center, \
            patient_email=self.email, service_time=begin+'-'+end, \
            comment=comment, book_time=now, note="", medication_prescribed="")

    def query_book(self):
        dm = data.DataModel('../db/book.csv')
        f1 = dm.find(mode="similar", patient_email=self.email)
        return sorted(f1, key=lambda x:x["book_time"], reverse=True)
        
        
if __name__ == '__main__':
    pass
    