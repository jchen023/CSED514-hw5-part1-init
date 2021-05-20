from VaccinePatient import NotEnoughVaccine, DoneWithVaccine, VaccinePatient
import unittest
import os
from sql_connection_manager import SqlConnectionManager
from utils import *
from COVID19_vaccine import COVID19Vaccine as covid
from vaccine_caregiver import VaccineCaregiver
from VaccinePatient import VaccinePatient as patient
from vaccine_reservation_scheduler import VaccineReservationScheduler as VaccineReserve

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

    def testAdd_dose(self):

        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    # create a new VaccineCaregiver object
                    self.vaccine_a = covid(vaccine="Moderna",
                                                    cursor=cursor)
                    # check if the patient is correctly inserted into the database
                    sqlQuery = '''
                                SELECT TotalDoses
                                FROM Vaccines
                                WHERE VaccineName = 'Moderna'
                                '''

                    self.vaccine_a.AddDoses(4, cursor)

                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()


                    if rows[0]['TotalDoses'] != 4:
                        self.fail("Adding doses failed")

                    clear_tables(sqlClient)
                    print('opps')
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Adding doses failed")

    def testReserve_dose(self):

        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    # create a new VaccineCaregiver object
                    self.vaccine_a = covid(vaccine="AstraZeneca",
                                                    cursor=cursor)
                    # check if the patient is correctly inserted into the database
                    sqlQuery = '''
                                SELECT AvailableDoses
                                FROM Vaccines
                                WHERE VaccineName = 'AstraZeneca'
                                '''

                    self.vaccine_a.AddDoses(4, cursor)
                    
                    self.vaccine_a.ReserveDoses(1, cursor)

                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()

                    print(rows)
                    if rows[0]['AvailableDoses'] != 2:
                        self.fail("Reserving doses failed")

                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Reserving doses failed")

    def test_ReserveAppt1(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    # create a new VaccineCaregiver object
                    self.vaccine_a = covid(vaccine="Pfizer",
                                                    cursor=cursor)

                    patient_a = patient('Bob Marley', 0, cursor=cursor)
                    vaccRes_a = VaccineReserve()

                    caregiversList = []
                    caregiversList.append(VaccineCaregiver('Britta Perry', cursor))
                    caregiversList.append(VaccineCaregiver('Troy Barnes', cursor))
                    caregivers = {}
                    for cg in caregiversList:
                        cgid = cg.caregiverId
                        caregivers[cgid] = cg

                    # check if the patient is correctly inserted into the database
                    sqlQuery = "SELECT * FROM VaccineAppointments WHERE VaccineName = 'Pfizer' AND PatientId = "+\
                            str(patient_a.PatientId) +";"
                                
                    #print('in')
                    self.vaccine_a.AddDoses(1, cursor)

                    patient_a.ReserveAppointment( vaccRes_a.PutHoldOnAppointmentSlot(cursor), self.vaccine_a, cursor)
                    #print('finally')
                    
                    
                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()

                    #print('hihi',rows)
                    if rows[0]['SlotStatus'] != 1:
                        self.fail("Reserving appt. 1 failed")

                    clear_tables(sqlClient)

                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Reserving appt. 1 failed")

    def test_ReserveAppt2(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    # create a new VaccineCaregiver object
                    self.vaccine_a = covid(vaccine="Pfizer",
                                                    cursor=cursor)

                    patient_a = patient('Vladimir Putin', 0, cursor=cursor)
                    vaccRes_a = VaccineReserve()

                    caregiversList = []
                    caregiversList.append(VaccineCaregiver('Jeffrey Winger', cursor))
                    caregiversList.append(VaccineCaregiver('Annie Edison', cursor))
                    caregivers = {}
                    for cg in caregiversList:
                        cgid = cg.caregiverId
                        caregivers[cgid] = cg

                    # check if the patient is correctly inserted into the database
                    sqlQuery = "SELECT * FROM VaccineAppointments WHERE VaccineName = 'Pfizer' AND PatientId = "+\
                            str(patient_a.PatientId) +";"

                    #print('in')
                    self.vaccine_a.AddDoses(2, cursor)

                    patient_a.ReserveAppointment( vaccRes_a.PutHoldOnAppointmentSlot(cursor), self.vaccine_a, cursor)
                    #print('finally')


                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()


                    if rows[1]['SlotStatus'] != 1 or len(rows) != 2:
                        self.fail("Reserving appt. 2 failed")

                    clear_tables(sqlClient)

                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Reserving appt. 2 failed")



if __name__ == '__main__':
    unittest.main()