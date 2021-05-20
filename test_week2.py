from VaccinePatient import NotEnoughVaccine, VaccinePatient
import unittest
import os
import pymssql
from sql_connection_manager import SqlConnectionManager
from enums import *
from utils import *
from COVID19_vaccine import COVID19Vaccine as covid
from COVID19_vaccine import COVID19Vaccine as covid
from VaccinePatient import VaccinePatient as patient

class Part2Test(unittest.TestCase):
    def FiveDosesTwoCareGiverFivePatient(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                      DBname=os.getenv("DBName"),
                                      UserId=os.getenv("UserID"),
                                      Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    clear_tables(sqlClient)
                    # create a new VaccineCaregiver object
                    self.vaccine_a = covid(vaccine="Pfizer",
                                           cursor=cursor)
                    # check if the patient is correctly inserted into the database
                    sqlQuery = '''
                                                   SELECT TotalDoses
                                                   FROM Vaccines
                                                   WHERE VaccineName = 'Pfizer';
                                                   '''
                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()

                    if rows[0]['TotalDoses'] != 0:
                        self.fail("Vaccine initialization failed")
                    if len(rows) != 1:
                        self.fail("Vaccine initialization failed")

                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Vaccine initialization failed")
    
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
                    
                    self.vaccine_a.ReserveDoses(2, cursor)

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

                    self.patient_a = patient('Bob Marley', 0, cursor=cursor)

                    # check if the patient is correctly inserted into the database
                    sqlQuery = "SELECT * FROM VaccineAppointments WHERE VaccineName = 'Pfizer' AND PatientId = "+\
                            str(self.patient_a.PatientId) +";"
                                
                    
                    self.vaccine_a.AddDoses(1, cursor)
                    self.patient_a.ReserveAppointment(self.patient_a.CaregiverSchedId1, self.patient_a.PatientName)

                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()

                    print('hihi',rows)
                    if rows[0]['SlotStatus'] != 1:
                        self.fail("Reserving appt. failed")

                    clear_tables(sqlClient)

                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Reserving appt. failed")
if __name__ == '__main__':
    unittest.main()