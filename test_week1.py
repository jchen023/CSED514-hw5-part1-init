import unittest
import os
import pymssql
from sql_connection_manager import SqlConnectionManager
from enums import *
from utils import *
from COVID19_vaccine import COVID19Vaccine as covid

class TestVaccineFunction(unittest.TestCase):
    def testVaccine_init(self):
        print(os.getenv("Server"),
                                    os.getenv("DBName"),
                                    os.getenv("UserID"),
                                    os.getenv("Password"))
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
    
    def testInvalid_vaccine(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                      DBname=os.getenv("DBName"),
                                      UserId=os.getenv("UserID"),
                                      Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    # create a new VaccineCaregiver object
                    self.vaccine_a = covid(vaccine="MicroChipInsideYou",
                                                    cursor=cursor)
                    # check if the patient is correctly inserted into the database
                    sqlQuery = '''
                                SELECT *
                                FROM Vaccines;
                               '''

                    #self.vaccine_a.AddDoses(4, cursor)

                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()
                    
                    if rows[0]['VaccineName'] != '':
                        self.fail("Vaccine naming failed")
                    
                    clear_tables(sqlClient)
                except Exception:
                    # In this case, the exception should be thrown to pass the test so no failure here.
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    
    
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
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Adding doses failed")

    def testAdd_negative_dose(self):

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
                                SELECT Inventory
                                FROM Vaccine
                                WHERE VaccineName = 'Moderna'
                                '''

                    self.vaccine_a.AddDoses(-4, cursor)

                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()


                    if rows[0]['Inventory'] != 0:
                        self.fail("Adding negative # of doses failed")

                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Adding negative # of doses failed")

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
                                SELECT TotalDoses
                                FROM Vaccines
                                WHERE VaccineName = 'AstraZeneca'
                                '''

                    self.vaccine_a.AddDoses(4, cursor)
                    self.vaccine_a.ReserveDoses(2, cursor)

                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()


                    if rows[0]['TotalDoses'] != 2:
                        self.fail("Reserving doses failed")

                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Reserving doses failed")

    def testReserve_negative_doses(self):

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
                                SELECT Inventory
                                FROM Vaccine
                                WHERE VaccineName = 'AstraZeneca'
                                '''

                    self.vaccine_a.AddDoses(4, cursor)
                    self.vaccine_a.ReserveDoses(-2, cursor)

                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()

                    if rows[0]['Inventory'] != 4:
                        self.fail("Reserving negative # of doses failed")

                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Reserving negative # of doses failed")
    
    
    def testTemp_doseAZ(self):

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
                                SELECT MaxStorageTemperature
                                FROM Vaccine
                                WHERE VaccineName = 'AstraZeneca'
                                AND MaxStorageTemperature > 36
                                '''

                    self.vaccine_a.AddDoses(1, cursor)

                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()

                    if rows != []:
                        self.fail("Astrazeneca Temperature problem")

                    clear_tables(sqlClient)

                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Astrazeneca Temperature problem")


    def testTemp_doseMD(self):

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
                                SELECT MaxStorageTemperature
                                FROM Vaccine
                                WHERE VaccineName = 'Moderna'
                                AND MaxStorageTemperature > -20
                                '''

                    self.vaccine_a.AddDoses(1, cursor)

                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()

                    if rows != []:
                        self.fail("Moderna Temperature problem")

                    clear_tables(sqlClient)

                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Moderna Temperature problem")


    def testTemp_dosePZ(self):

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
                    # check if the patient is correctly inserted into the database
                    sqlQuery = '''
                                SELECT MaxStorageTemperature
                                FROM Vaccine
                                WHERE VaccineName = 'Pfizer'
                                AND MaxStorageTemperature > -70
                                '''

                    self.vaccine_a.AddDoses(1, cursor)

                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()

                    if rows != []:
                        self.fail("Pfizer Temperature problem")

                    clear_tables(sqlClient)

                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Pfizer Temperature problem")

    def testTemp_doseJJ(self):

        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    # create a new VaccineCaregiver object
                    self.vaccine_a = covid(vaccine="J&J",
                                                    cursor=cursor)
                    # check if the patient is correctly inserted into the database
                    sqlQuery = '''
                                SELECT MaxStorageTemperature
                                FROM Vaccine
                                WHERE VaccineName = 'J&J'
                                AND MaxStorageTemperature > 90
                                '''

                    self.vaccine_a.AddDoses(1, cursor)

                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()

                    if rows != []:
                        self.fail("J&J Temperature problem")

                    clear_tables(sqlClient)

                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("J&J Temperature problem")

if __name__ == '__main__':
    unittest.main()