from VaccinePatient import NotEnoughVaccine
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