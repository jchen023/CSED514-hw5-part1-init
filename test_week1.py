import unittest
import os
import pymssql
from sql_connection_manager import SqlConnectionManager
from COVID19_vaccine import COVID19Vaccine
from enums import *
from utils import *

class TestVaccineFunction(unittest.TestCase):
    def testVaccine_init(self):
        try:
            with SqlConnectionManager(Server=os.getenv("Server"),
                                      DBname=os.getenv("DBName"),
                                      UserId=os.getenv("UserID"),
                                      Password=os.getenv("Password")) as sqlClient:
                with sqlClient.cursor(as_dict=True) as cursor:
                    try:
                        # clear the tables before testing
                        clear_tables(sqlClient)
                        # create a new VaccineCaregiver object
                        self.vaccine_a = COVID19Vaccine(vaccine="Pfizer",
                                                        cursor=cursor)
                        # check if the patient is correctly inserted into the database
                        sqlQuery = '''
                                    SELECT Inventory
                                    FROM Vaccine
                                    WHERE VaccineName = "Pfizer"
                                    '''
                        cursor.execute(sqlQuery)
                        rows = cursor.fetchall()
                        
                        if rows != 0:
                            self.fail("Vaccine initialization failed")
                        if len(rows != 1):
                            self.fail("Vaccine initialization failed")
                        
                        clear_tables(sqlClient)
                    except Exception:
                        # clear the tables if an exception occurred
                        clear_tables(sqlClient)
                        self.fail("Vaccine initialization failed")

    def testAdd_dose(self):
        try:
            with SqlConnectionManager(Server=os.getenv("Server"),
                                        DBname=os.getenv("DBName"),
                                        UserId=os.getenv("UserID"),
                                        Password=os.getenv("Password")) as sqlClient:
                with sqlClient.cursor(as_dict=True) as cursor:
                    try:
                        # clear the tables before testing
                        clear_tables(sqlClient)
                        # create a new VaccineCaregiver object
                        self.vaccine_a = COVID19Vaccine(vaccine="Moderna",
                                                        cursor=cursor)
                        # check if the patient is correctly inserted into the database
                        sqlQuery = '''
                                    SELECT Inventory
                                    FROM Vaccine
                                    WHERE VaccineName = "Moderna"
                                    '''

                        COVID19Vaccine.AddDoses(4,cursor)

                        cursor.execute(sqlQuery)
                        rows = cursor.fetchall()

                        if rows != 4:
                            self.fail("Adding doses failed")

                        clear_tables(sqlClient)
                    except Exception:
                        # clear the tables if an exception occurred
                        clear_tables(sqlClient)
                        self.fail("Adding doses failed")

    def testReserve_dose(self):
        try:
            with SqlConnectionManager(Server=os.getenv("Server"),
                                      DBname=os.getenv("DBName"),
                                      UserId=os.getenv("UserID"),
                                      Password=os.getenv("Password")) as sqlClient:
                with sqlClient.cursor(as_dict=True) as cursor:
                    try:
                        # clear the tables before testing
                        clear_tables(sqlClient)
                        # create a new VaccineCaregiver object
                        self.vaccine_a = COVID19Vaccine(vaccine="AstraZeneca",
                                                        cursor=cursor)
                        # check if the patient is correctly inserted into the database
                        sqlQuery = '''
                                    SELECT Inventory
                                    FROM Vaccine
                                    WHERE VaccineName = "AstraZeneca"
                                    '''

                        COVID19Vaccine.AddDoses(4,cursor)
                        COVID19Vaccine.ReserveDoses(2,cursor)

                        cursor.execute(sqlQuery)
                        rows = cursor.fetchall()

                        if rows != 2:
                            self.fail("Reserving doses failed")

                        clear_tables(sqlClient)
                    except Exception:
                        # clear the tables if an exception occurred
                        clear_tables(sqlClient)
                        self.fail("Reserving doses failed")

if __name__ == '__main__':
    unittest.main()

                        
