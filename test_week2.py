from VaccinePatient import NotEnoughVaccine
import unittest
import os
from sql_connection_manager import SqlConnectionManager
from utils import *
from COVID19_vaccine import COVID19Vaccine as covid
from vaccine_caregiver import VaccineCaregiver
from VaccinePatient import VaccinePatient as patient

class TestPart2(unittest.TestCase):
    def testFiveDosesTwoCareGiversFivePatients(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                      DBname=os.getenv("DBName"),
                                      UserId=os.getenv("UserID"),
                                      Password=os.getenv("Password")) as sqlClient:
            dbcursor_vaccine = sqlClient.cursor(as_dict=True)
            try:
                clear_tables(sqlClient)
                # create a new Vaccine and add 5 doses of vaccines
                pfizer = covid("Pfizer", dbcursor_vaccine)
                pfizer.AddDoses(5, dbcursor_vaccine)

                # check if the patient is correctly inserted into the database
                sqlQuery = "SELECT * from Vaccines where VaccineName = 'Pfizer';"

                dbcursor_vaccine.execute(sqlQuery)
                rows = dbcursor_vaccine.fetchall()

                if not (rows[0]["AvailableDoses"] == 5 and rows[0]["TotalDoses"] == 5
                        and rows[0]["ReservedDoses"] == 0 and rows[0]["DosesPerPatient"] == 2
                        and len(rows) == 1):
                    self.fail("Vaccine initialization failed")

                dbcursor_caregiver = sqlClient.cursor(as_dict=True)
                # create two new caregivers
                caregiversList = []
                caregiversList.append(VaccineCaregiver('Barack Obama', dbcursor_caregiver))
                caregiversList.append(VaccineCaregiver('Joseph Biden', dbcursor_caregiver))
                caregivers = {}
                for cg in caregiversList:
                    cgid = cg.caregiverId
                    caregivers[cgid] = cg

                dbcursor_patient = sqlClient.cursor(as_dict=True)

                patientcursor = []
                for _ in range(5):
                    patientcursor.append(sqlClient.cursor(as_dict=True))

                patientsList = []
                patientsList.append(patient('Ben Bernanke', 0))
                patients = {}
                for pt in patientsList:
                    ptid = pt.PatientId
                    patients[ptid] = pt

            # patients = []
            # for _ in range(5):
            #     patients.append()
            #

                clear_tables(sqlClient)
            except Exception:
                # clear the tables if an exception occurred
                clear_tables(sqlClient)
                self.fail("Failing FiveDosesTwoCareGiversFivePatients")


if __name__ == '__main__':
    unittest.main()