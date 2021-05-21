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

                patientscursor = []
                for _ in range(5):
                    patientscursor.append(sqlClient.cursor(as_dict=True))

                patientsList = []
                patientName = ('Charlie T. Munger', 'Ben Bernanke', 'Janet Yellen', 'Jorome Powell', 'Benjamin Graham')
                patientsList.append(patient('Charlie T. Munger', 0, dbcursor_patient))
                patientsList.append(patient('Ben Bernanke', 0, dbcursor_patient))
                patientsList.append(patient('Janet Yellen', 0, dbcursor_patient))
                patientsList.append(patient('Jorome Powell', 0, dbcursor_patient))
                patientsList.append(patient('Benjamin Graham', 0, dbcursor_patient))
                patients = {}
                for pt in patientsList:
                    ptid = pt.PatientId
                    patients[ptid] = pt

                vrs = VaccineReserve()
                cursor = sqlClient.cursor(as_dict=True)
                for i in range(5):
                    patientsList[i].ReserveAppointment(vrs.PutHoldOnAppointmentSlot(patientscursor[i]), pfizer, patientscursor[i])

                    # Test reserve doses on vaccines table
                    cursor.execute("select * from vaccines where vaccineName = 'Pfizer'")
                    vaccine_result = cursor.fetchall()
                    self.assertEqual(len(vaccine_result), 1)
                    self.assertEqual(vaccine_result[0]["AvailableDoses"], max(0, 5 - 2 - i * 2))
                    self.assertEqual(vaccine_result[0]["TotalDoses"], 5)
                    self.assertEqual(vaccine_result[0]["ReservedDoses"], min(5, 2 + i * 2))

                    # Test reserve doses on caregivers table
                    cursor.execute("select * from caregivers")
                    caregiver_result = cursor.fetchall()
                    self.assertEqual(len(caregiver_result), 2)
                    self.assertEqual(caregiver_result[0]["CaregiverName"], 'Barack Obama')
                    self.assertEqual(caregiver_result[1]["CaregiverName"], 'Joseph Biden')

                    # Test reserve doses on Patients table
                    cursor.execute("select * from patients")
                    patient_result = cursor.fetchall()
                    self.assertEqual(len(patient_result), 5)
                    for j in range(5):
                        self.assertEqual(patient_result[j]["PatientName"], patientName[j])
                    cursor.execute("select * from patients where VaccineStatus = 1")
                    patient_scheduled_result = cursor.fetchall()
                    self.assertEqual(len(patient_scheduled_result), 1 if i <= 2 else 0)


                    # Test reserve doses on Caregiver Schedule
                    cursor.execute("select * from CareGiverSchedule where SlotStatus = 1 and VaccineAppointmentId IS NOT NULL")
                    schedule_result = cursor.fetchall()
                    if i <= 1:
                        self.assertEqual(len(schedule_result), 2)
                    elif i == 2:
                        self.assertEqual(len(schedule_result), 1)
                    else:
                        self.assertEqual(len(schedule_result), 0)

                    # Test reserve doses on vaccine appointment
                    cursor.execute(
                        "select * from VaccineAppointments where SlotStatus = 1 and VaccineAppointmentId IS NOT NULL")
                    appointment_result = cursor.fetchall()
                    if i <= 1:
                        self.assertEqual(len(appointment_result), 2)
                    elif i == 2:
                        self.assertEqual(len(appointment_result), 1)
                    else:
                        self.assertEqual(len(appointment_result), 0)

                    # Test the sets of vaccine appointment id from caregiver schedule and vaccine appointment tables are the same
                    appointmentIdSet_cg = set((x["VaccineAppointmentId"] for x in schedule_result))
                    appointmentIdSet_va = set((x["VaccineAppointmentId"] for x in appointment_result))
                    self.assertEqual(appointmentIdSet_cg, appointmentIdSet_va)

                    patientsList[i].ScheduleAppointment(patientscursor[i])

                    # Test schedule doses on vaccines table
                    cursor.execute("select * from vaccines where vaccineName = 'Pfizer'")
                    vaccine_result = cursor.fetchall()
                    self.assertEqual(len(vaccine_result), 1)
                    self.assertEqual(vaccine_result[0]["AvailableDoses"], max(0, 5 - 2 - i * 2))
                    self.assertEqual(vaccine_result[0]["TotalDoses"], 5)
                    self.assertEqual(vaccine_result[0]["ReservedDoses"], min(5, 2 + i * 2))

                    # Test schedule doses on caregivers table
                    cursor.execute("select * from caregivers")
                    caregiver_result = cursor.fetchall()
                    self.assertEqual(len(caregiver_result), 2)
                    self.assertEqual(caregiver_result[0]["CaregiverName"], 'Barack Obama')
                    self.assertEqual(caregiver_result[1]["CaregiverName"], 'Joseph Biden')

                    # Test schedule doses on Patients table
                    cursor.execute("select * from patients")
                    patient_result = cursor.fetchall()
                    self.assertEqual(len(patient_result), 5)
                    for j in range(5):
                        self.assertEqual(patient_result[j]["PatientName"], patientName[j])
                    cursor.execute("select * from patients where VaccineStatus = 2")
                    patient_scheduled_result = cursor.fetchall()
                    self.assertEqual(len(patient_scheduled_result), min(i + 1, 3))

                    # Test schedule doses on Caregiver Schedule
                    cursor.execute(
                        "select * from CareGiverSchedule where SlotStatus = 2 and VaccineAppointmentId IS NOT NULL")
                    schedule_result = cursor.fetchall()
                    self.assertEqual(len(schedule_result), min(5, 2 + i * 2))

                    # Test schedule doses on vaccine appointment
                    cursor.execute(
                        "select * from VaccineAppointments where SlotStatus = 2 and VaccineAppointmentId IS NOT NULL")
                    appointment_result = cursor.fetchall()
                    self.assertEqual(len(appointment_result), min(5, 2 + i * 2))

                    # Test the sets of vaccine appointment id from caregiver schedule and vaccine appointment tables are the same
                    appointmentIdSet_cg = set((x["VaccineAppointmentId"] for x in schedule_result))
                    appointmentIdSet_va = set((x["VaccineAppointmentId"] for x in appointment_result))
                    self.assertEqual(appointmentIdSet_cg, appointmentIdSet_va)

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

                    if rows[0]['SlotStatus'] != 1:
                        self.fail("Reserving appt. 1 failed")

                    sqltext2 = "SELECT * FROM PATIENTS WHERE PatientId = " + str(patient_a.PatientId) + ";"
                    cursor.execute(sqltext2)
                    rows2 = cursor.fetchall()
                    #print(rows2)
                    if rows2[0]['VaccineStatus'] != 1:
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

                    sqltext2 = "SELECT * FROM PATIENTS WHERE PatientId = " + str(patient_a.PatientId) + ";"
                    cursor.execute(sqltext2)
                    rows2 = cursor.fetchall()
                    #print(rows2)
                    if rows2[0]['VaccineStatus'] != 1:
                        self.fail("Reserving appt. 2 failed")

                    clear_tables(sqlClient)

                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Reserving appt. 2 failed")



if __name__ == '__main__':
    unittest.main()