from traceback import format_exception_only
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

                    if len(rows) != 1 and rows[0]['TotalDoses'] != 4:
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
                                SELECT AvailableDoses
                                FROM Vaccines
                                WHERE VaccineName = 'AstraZeneca'
                                '''

                    self.vaccine_a.AddDoses(4, cursor)

                    self.vaccine_a.ReserveDoses(1, cursor)

                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()

                    print(rows)
                    if rows[0]['AvailableDoses'] != 3:
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

                    self.vaccine_a.AddDoses(1, cursor)
                    patient_a.ReserveAppointment( vaccRes_a.PutHoldOnAppointmentSlot(cursor), self.vaccine_a, cursor)

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

                    self.vaccine_a.AddDoses(2, cursor)

                    patient_a.ReserveAppointment( vaccRes_a.PutHoldOnAppointmentSlot(cursor), self.vaccine_a, cursor)

                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()

                    if not rows or rows[1]['SlotStatus'] != 1 or len(rows) != 2:
                        self.fail("Reserving appt. 2 failed")

                    sqltext2 = "SELECT * FROM PATIENTS WHERE PatientId = " + str(patient_a.PatientId) + ";"
                    cursor.execute(sqltext2)
                    rows2 = cursor.fetchall()
                    #print(rows2)
                    if not rows2 or rows2[0]['VaccineStatus'] != 1:
                        self.fail("Reserving appt. 2 failed")

                    clear_tables(sqlClient)

                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Reserving appt. 2 failed")
    
    def test_scheduling(self):
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

                    patient_a = patient('George Washington', 0, cursor=cursor)
                    vaccRes_a = VaccineReserve()

                    caregiversList = []
                    caregiversList.append(VaccineCaregiver('Pierce Hawthorne', cursor))
                    caregiversList.append(VaccineCaregiver('Ben Chang', cursor))
                    caregivers = {}
                    for cg in caregiversList:
                        cgid = cg.caregiverId
                        caregivers[cgid] = cg

                    self.vaccine_a.AddDoses(2, cursor)
                    patient_a.ReserveAppointment(vaccRes_a.PutHoldOnAppointmentSlot(cursor), self.vaccine_a, cursor)
                    patient_a.ScheduleAppointment(cursor)

                    # check if the appointment get scheduled correctly
                    sqlQuery1 = "SELECT * FROM CareGiverSchedule WHERE CaregiverSlotSchedulingId = " \
                            + str(patient_a.firstCareGiverSchedulingId) + "and SlotStatus = 2;"
                    cursor.execute(sqlQuery1)
                    rows1 = cursor.fetchall()
                    if not rows1:
                        self.fail('Caregiver Schedule not properly added')
                    ###################################
                    sqlQuery2 = "SELECT * FROM Patients WHERE PatientId = " + str(patient_a.PatientId) + \
                               "AND VaccineStatus = 2;"
                    cursor.execute(sqlQuery2)
                    rows2 =cursor.fetchall()
                    if not rows2:
                        self.fail('Patient not properly updated')
                    ###################################
                    sqlQuery3 = "SELECT * FROM VaccineAppointments WHERE VaccineAppointmentId  = "+ \
                           str(patient_a.firstAppointmentId) + " AND SlotStatus = 2;"
                    cursor.execute(sqlQuery3)
                    rows3 =cursor.fetchall()
                    if not rows3:
                        self.fail('Vaccine Appointment not properly updated')
                    #--------------------------------------------------------------------------------------------------------
                    sqlQuery4 = "SELECT * FROM CareGiverSchedule WHERE CaregiverSlotSchedulingId = " \
                            + str(patient_a.secondCareGiverSchedulingId) + "and SlotStatus = 2;"
                    cursor.execute(sqlQuery1)
                    rows4 = cursor.fetchall()
                    if not rows4:
                        self.fail('Caregiver Schedule not properly added')
                    ###################################
                    sqlQuery5 = "SELECT * FROM Patients WHERE PatientId = " + str(patient_a.PatientId) + \
                               "AND VaccineStatus = 2;"
                    cursor.execute(sqlQuery1)
                    rows5 = cursor.fetchall()
                    if not rows5:
                        self.fail('Patient not properly updated')
                    ###################################
                    sqlQuery6 = "SELECT * FROM VaccineAppointments WHERE VaccineAppointmentId  = "+ \
                           str(patient_a.firstAppointmentId) + " AND SlotStatus = 2;"
                    cursor.execute(sqlQuery1)
                    rows6 = cursor.fetchall()
                    if not rows6:
                        self.fail('Vaccine Appointment not properly updated')
                    ###################################

                    clear_tables(sqlClient)
                except Exception:
                    clear_tables(sqlClient)
                    self.fail("Scheduling Vaccine Appointment failed catastrophically")

    def test_Schedule_Third_Vaccine_Exception(self):
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

                    patient_a = patient('Larry Ellison', 7, cursor=cursor)
                    vaccRes_a = VaccineReserve()

                    caregiversList = []
                    caregiversList.append(VaccineCaregiver('Luka Milenkovic', cursor))
                    caregiversList.append(VaccineCaregiver('Audrey Calson', cursor))
                    caregivers = {}
                    for cg in caregiversList:
                        cgid = cg.caregiverId
                        caregivers[cgid] = cg

                    self.vaccine_a.AddDoses(2, cursor)
                    
                    with self.assertRaises(DoneWithVaccine):
                        patient_a.ReserveAppointment(vaccRes_a.PutHoldOnAppointmentSlot(cursor), self.vaccine_a, cursor)
                    
                    # if patient_a.PatientStatusCode >= 7:
                    #     self.fail("Dont try to get vaccinated again")
                    clear_tables(sqlClient)
                except Exception:
                    clear_tables(sqlClient)
                    self.fail("Vaccine Status Code Error")
    
    def test_only_one_vaccine_available(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            cursor = sqlClient.cursor(as_dict=True)
            db_cursor = sqlClient.cursor(as_dict=True)
            try:
                # clear the tables before testing
                clear_tables(sqlClient)
                # create a new VaccineCaregiver object
                vaccine_a = covid(vaccine="Moderna",
                                                cursor=db_cursor)

                patient_a = patient('Hugh Heffner', 0, cursor=db_cursor)
                vaccRes_a = VaccineReserve()

                caregiversList = []
                caregiversList.append(VaccineCaregiver('Hendrik Lenstra', db_cursor))
                caregiversList.append(VaccineCaregiver('Leonardo DiCaprio', db_cursor))
                caregivers = {}
                for cg in caregiversList:
                    cgid = cg.caregiverId
                    caregivers[cgid] = cg


                vaccine_a.AddDoses(1, cursor)
                patient_a.ReserveAppointment(vaccRes_a.PutHoldOnAppointmentSlot(cursor), vaccine_a, db_cursor)

                # Test reserve doses on vaccines table
                cursor.execute("select * from vaccines where vaccineName = 'Moderna'")
                vaccine_result = cursor.fetchall()
                self.assertEqual(len(vaccine_result), 1)
                self.assertEqual(vaccine_result[0]["AvailableDoses"], 0)
                self.assertEqual(vaccine_result[0]["TotalDoses"], 1)
                self.assertEqual(vaccine_result[0]["ReservedDoses"], 1)

                # Test reserve doses on caregivers table
                cursor.execute("select * from caregivers")
                caregiver_result = cursor.fetchall()
                self.assertEqual(len(caregiver_result), 2)
                self.assertEqual(caregiver_result[0]["CaregiverName"], 'Hendrik Lenstra')
                self.assertEqual(caregiver_result[1]["CaregiverName"], 'Leonardo DiCaprio')

                # Test reserve doses on Patients table
                cursor.execute("select * from patients")
                patient_result = cursor.fetchall()
                self.assertEqual(len(patient_result), 1)
                cursor.execute("select * from patients where VaccineStatus = 1")
                patient_scheduled_result = cursor.fetchall()
                self.assertEqual(len(patient_scheduled_result), 1)

                # Test reserve doses on Caregiver Schedule
                cursor.execute(
                    "select * from CareGiverSchedule where SlotStatus = 1 and VaccineAppointmentId IS NOT NULL")
                schedule_result = cursor.fetchall()
                self.assertEqual(len(schedule_result), 1)

                # Test reserve doses on vaccine appointment
                cursor.execute(
                    "select * from VaccineAppointments where SlotStatus = 1 and VaccineAppointmentId IS NOT NULL")
                appointment_result = cursor.fetchall()
                self.assertEqual(len(appointment_result), 1)

                # Test the sets of vaccine appointment id from caregiver schedule and vaccine appointment tables are the same
                appointmentIdSet_cg = set((x["VaccineAppointmentId"] for x in schedule_result))
                appointmentIdSet_va = set((x["VaccineAppointmentId"] for x in appointment_result))
                self.assertEqual(appointmentIdSet_cg, appointmentIdSet_va)

                patient_a.ScheduleAppointment(cursor)




            except(Exception):
                clear_tables(sqlClient)
                self.fail("Rollback Error")



if __name__ == '__main__':
    unittest.main()