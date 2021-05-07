import unittest
import os
import pymssql
from sql_connection_manager import SqlConnectionManager
from enums import *
from utils import *
from COVID19_vaccine import COVID19Vaccine as covid

class TestVaccineFunction(unittest.TestCase):
    def testVaccine_init(self):
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
                                SELECT Inventory
                                FROM Vaccine
                                WHERE VaccineName = 'Pfizer';
                                '''
                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()
                    
                    if rows[0]['Inventory'] != 0:
                        self.fail("Vaccine initialization failed")
                    if len(rows) != 1:
                        self.fail("Vaccine initialization failed")

                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Vaccine initialization failed")
    
    # def testInvalid_vaccine(self):
    #     with SqlConnectionManager(Server=os.getenv("Server"),
    #                                   DBname=os.getenv("DBName"),
    #                                   UserId=os.getenv("UserID"),
    #                                   Password=os.getenv("Password")) as sqlClient:
    #         with sqlClient.cursor(as_dict=True) as cursor:
    #             try:
    #                 # clear the tables before testing
    #                 clear_tables(sqlClient)
    #                 # create a new VaccineCaregiver object
    #                 self.vaccine_a = covid(vaccine="MicroChipInsideYou",
    #                                                 cursor=cursor)
    #                 # check if the patient is correctly inserted into the database
    #                 sqlQuery = '''
    #                             SELECT VaccineName
    #                             FROM Vaccine
    #                             WHERE VaccineName = 'Pfizer';
    #                             '''
    
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
                                SELECT Inventory
                                FROM Vaccine
                                WHERE VaccineName = 'Moderna'
                                '''

                    self.vaccine_a.AddDoses(4, cursor)

                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()


                    if rows[0]['Inventory'] != 4:
                        self.fail("Adding doses failed")

                    clear_tables(sqlClient)
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
                                SELECT Inventory
                                FROM Vaccine
                                WHERE VaccineName = 'AstraZeneca'
                                '''

                    self.vaccine_a.AddDoses(4, cursor)
                    self.vaccine_a.ReserveDoses(2, cursor)

                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()


                    if rows[0]['Inventory'] != 2:
                        self.fail("Reserving doses failed")

                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Reserving doses failed")

if __name__ == '__main__':
    unittest.main()

                        
