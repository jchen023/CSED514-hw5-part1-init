import unittest
import os

from sql_connection_manager import SqlConnectionManager
from vaccine_caregiver import VaccineCaregiver
from enums import *
from utils import *
# from covid19_vaccine import COVID19Vaccine as covid
# from vaccine_patient import VaccinePatient as patient

class TestDB(unittest.TestCase):

    def test_db_connection(self):
        try:
            self.connection_manager = SqlConnectionManager(Server=os.getenv("Server"),
                                                           DBname=os.getenv("DBName"),
                                                           UserId=os.getenv("UserID"),
                                                           Password=os.getenv("Password"))
            self.conn = self.connection_manager.Connect()
        except Exception:
            self.fail("Connection to databse failed")


class TestVaccineCaregiver(unittest.TestCase):
    def test_init(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    # create a new VaccineCaregiver object
                    self.caregiver_a = VaccineCaregiver(name="Steve Ma",
                                                    cursor=cursor)
                    # check if the patient is correctly inserted into the database
                    sqlQuery = '''
                               SELECT *
                               FROM Caregivers
                               WHERE CaregiverName = 'Steve Ma'
                               '''
                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()
                    if len(rows) < 1:
                        self.fail("Creating caregiver failed")
                    # clear the tables after testing, just in-case
                    # clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Creating caregiver failed")
    
    def test_verify_schedule(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    # create a new VaccineCaregiver object
                    self.caregiver_a = VaccineCaregiver(name="Steve Ma",
                                                    cursor=cursor)
                    # check if schedule has been correctly inserted into CareGiverSchedule
                    sqlQuery = '''
                               SELECT *
                               FROM Caregivers, CareGiverSchedule
                               WHERE Caregivers.CaregiverName = 'Steve Ma'
                                   AND Caregivers.CaregiverId = CareGiverSchedule.CaregiverId
                               '''
                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()
                    hoursToSchedlue = [10,11]
                    minutesToSchedlue = [0, 15, 30, 45]
                    for row in rows:
                        slot_hour = row["SlotHour"]
                        slot_minute = row["SlotMinute"]
                        if slot_hour not in hoursToSchedlue or slot_minute not in minutesToSchedlue:
                            self.fail("CareGiverSchedule verification failed")
                    # clear the tables after testing, just in-case
                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("CareGiverSchedule verification failed")


if __name__ == '__main__':
    unittest.main()

# import unittest
# import os

# from sql_connection_manager import SqlConnectionManager
# from vaccine_caregiver import VaccineCaregiver
# from enums import *
# from utils import *
# from COVID19_vaccine import COVID19Vaccine as covid
# # from vaccine_patient import VaccinePatient as patient

# class TestDB(unittest.TestCase):

#     def test_db_connection(self):
#         try:
#             self.connection_manager = SqlConnectionManager(Server=os.getenv("Server"),
#                                                            DBname=os.getenv("DBName"),
#                                                            UserId=os.getenv("UserID"),
#                                                            Password=os.getenv("Password"))

#             self.conn = self.connection_manager.Connect()
#         except Exception:
#             self.fail("Connection to databse failed")


# class TestVaccineCaregiver(unittest.TestCase):
#     def test_init(self):
#         with SqlConnectionManager(Server=os.getenv("Server"),
#                                   DBname=os.getenv("DBName"),
#                                   UserId=os.getenv("UserID"),
#                                   Password=os.getenv("Password")) as sqlClient:
#             with sqlClient.cursor(as_dict=True) as cursor:
#                 try:
#                     # clear the tables before testing
#                     clear_tables(sqlClient)
#                     # create a new VaccineCaregiver object
#                     self.caregiver_a = VaccineCaregiver(name="Steve Ma",
#                                                     cursor=cursor)
#                     # check if the patient is correctly inserted into the database
#                     sqlQuery = '''
#                                SELECT *
#                                FROM Caregivers
#                                WHERE CaregiverName = 'Steve Ma'
#                                '''
#                     cursor.execute(sqlQuery)
#                     rows = cursor.fetchall()
#                     if len(rows) < 1:
#                         self.fail("Creating caregiver failed")
#                     # clear the tables after testing, just in-case
#                     # clear_tables(sqlClient)
#                 except Exception:
#                     # clear the tables if an exception occurred
#                     clear_tables(sqlClient)
#                     self.fail("Creating caregiver failed")
    
#     def test_verify_schedule(self):
#         with SqlConnectionManager(Server=os.getenv("Server"),
#                                   DBname=os.getenv("DBName"),
#                                   UserId=os.getenv("UserID"),
#                                   Password=os.getenv("Password")) as sqlClient:
#             with sqlClient.cursor(as_dict=True) as cursor:
#                 try:
#                     # clear the tables before testing
#                     clear_tables(sqlClient)
#                     # create a new VaccineCaregiver object
#                     self.caregiver_a = VaccineCaregiver(name="Steve Ma",
#                                                     cursor=cursor)
#                     # check if schedule has been correctly inserted into CareGiverSchedule
#                     sqlQuery = '''
#                                SELECT *
#                                FROM Caregivers, CareGiverSchedule
#                                WHERE Caregivers.CaregiverName = 'Steve Ma'
#                                    AND Caregivers.CaregiverId = CareGiverSchedule.CaregiverId
#                                '''
#                     cursor.execute(sqlQuery)
#                     rows = cursor.fetchall()
#                     hoursToSchedlue = [10,11]
#                     minutesToSchedlue = [0, 15, 30, 45]
#                     for row in rows:
#                         slot_hour = row["SlotHour"]
#                         slot_minute = row["SlotMinute"]
#                         if slot_hour not in hoursToSchedlue or slot_minute not in minutesToSchedlue:
#                             self.fail("CareGiverSchedule verification failed")
#                     # clear the tables after testing, just in-case
#                     clear_tables(sqlClient)
#                 except Exception:
#                     # clear the tables if an exception occurred
#                     clear_tables(sqlClient)
#                     self.fail("CareGiverSchedule verification failed")


# class TestVaccineFunction(unittest.TestCase):
#     def testVaccine_init(self):
#         with SqlConnectionManager(Server=os.getenv("Server"),
#                                       DBname=os.getenv("DBName"),
#                                       UserId=os.getenv("UserID"),
#                                       Password=os.getenv("Password")) as sqlClient:
#             with sqlClient.cursor(as_dict=True) as cursor:
#                 try:
#                     # clear the tables before testing
#                     clear_tables(sqlClient)
#                     # create a new VaccineCaregiver object
#                     self.vaccine_a = covid(vaccine="Pfizer",
#                                                     cursor=cursor)
#                     # check if the patient is correctly inserted into the database
#                     sqlQuery = '''
#                                 SELECT Inventory
#                                 FROM Vaccine
#                                 WHERE VaccineName = "Pfizer"
#                                 '''
#                     cursor.execute(sqlQuery)
#                     rows = cursor.fetchall()

#                     if rows != 0:
#                         self.fail("Vaccine initialization failed")
#                     if len(rows != 1):
#                         self.fail("Vaccine initialization failed")

#                     clear_tables(sqlClient)
#                 except Exception:
#                     # clear the tables if an exception occurred
#                     clear_tables(sqlClient)
#                     self.fail("Vaccine initialization failed")

#     def testAdd_dose(self):

#         with SqlConnectionManager(Server=os.getenv("Server"),
#                                   DBname=os.getenv("DBName"),
#                                   UserId=os.getenv("UserID"),
#                                   Password=os.getenv("Password")) as sqlClient:
#             with sqlClient.cursor(as_dict=True) as cursor:
#                 try:
#                     # clear the tables before testing
#                     clear_tables(sqlClient)
#                     # create a new VaccineCaregiver object
#                     self.vaccine_a = covid(vaccine="Moderna",
#                                                     cursor=cursor)
#                     # check if the patient is correctly inserted into the database
#                     sqlQuery = '''
#                                 SELECT Inventory
#                                 FROM Vaccine
#                                 WHERE VaccineName = "Moderna"
#                                 '''

#                     COVID19Vaccine.AddDoses(4, cursor)

#                     cursor.execute(sqlQuery)
#                     rows = cursor.fetchall()

#                     if rows != 4:
#                         self.fail("Adding doses failed")

#                     clear_tables(sqlClient)
#                 except Exception:
#                     # clear the tables if an exception occurred
#                     clear_tables(sqlClient)
#                     self.fail("Adding doses failed")

#     def testReserve_dose(self):

#         with SqlConnectionManager(Server=os.getenv("Server"),
#                                   DBname=os.getenv("DBName"),
#                                   UserId=os.getenv("UserID"),
#                                   Password=os.getenv("Password")) as sqlClient:
#             with sqlClient.cursor(as_dict=True) as cursor:
#                 try:
#                     # clear the tables before testing
#                     clear_tables(sqlClient)
#                     # create a new VaccineCaregiver object
#                     self.vaccine_a = covid(vaccine="AstraZeneca",
#                                                     cursor=cursor)
#                     # check if the patient is correctly inserted into the database
#                     sqlQuery = '''
#                                 SELECT Inventory
#                                 FROM Vaccine
#                                 WHERE VaccineName = "AstraZeneca"
#                                 '''

#                     COVID19Vaccine.AddDoses(4, cursor)
#                     COVID19Vaccine.ReserveDoses(2, cursor)

#                     cursor.execute(sqlQuery)
#                     rows = cursor.fetchall()

#                     if rows != 2:
#                         self.fail("Reserving doses failed")

#                     clear_tables(sqlClient)
#                 except Exception:
#                     # clear the tables if an exception occurred
#                     clear_tables(sqlClient)
#                     self.fail("Reserving doses failed")


# if __name__ == '__main__':
#     unittest.main()
