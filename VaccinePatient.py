from datetime import datetime
from datetime import timedelta
import vaccine_caregiver
import pymssql
from sql_connection_manager import SqlConnectionManager
import os

class NotEnoughVaccine(Exception):
    pass

class VaccinePatient:
    def __init__(self, PatientName, PatientStatusCode, cursor):
        try:
            self.sqltext = \
                "INSERT INTO Patients (PatientName, VaccineStatus) VALUES ('%s', %d);" % (
                    PatientName,
                    PatientStatusCode
                )
            self.PatientId = 0
            self.PatientName = PatientName
            self.PatientStatusCode = PatientStatusCode

            cursor.execute(self.sqltext)
            cursor.connection.commit()
            cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            _identityRow = cursor.fetchone()
            self.PatientId = _identityRow['Identity']
            cursor.connection.commit()
            print('Query executed successfully. Vaccine Patient : ' + self.PatientName
                  + ' added to the database using Patient ID = ' + str(self.PatientId))
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for VACCINE PATIENT! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)


    def ReserveAppointment(self, CaregiverSchedulingID, Vaccine, cursor):
        try:
            # Checking if the slot is on hold
            sqltext = ("select * from CareGiverSchedule where CaregiverSlotSchedulingId = %d"
                       % (CaregiverSchedulingID))
            cursor.execute(sqltext)
            self.caregiver_result = cursor.fetchone()
            slotStatus = self.caregiver_result['SlotStatus']
            if slotStatus != 1:
                raise ValueError()

            # Reserving Vaccine Doses
            sqltext = "select * from Vaccines where VaccineName = '{}'".format(Vaccine.vaccine)
            cursor.execute(sqltext)
            vaccine_result = cursor.fetchone()
            dosesPerPatient = vaccine_result["DosesPerPatient"]
            availableDoses = vaccine_result.get("AvailableDoses", 0)
            if not availableDoses:
                raise NotEnoughVaccine

            # Initial Entry in the Vaccine Appointment Table of the FIRST DOSE
            VaccineName = Vaccine.vaccine
            CaregiverId = self.caregiver_result['CaregiverId']
            ReservationDate = self.caregiver_result['WorkDay']
            ReservationStartHour = self.caregiver_result["SlotHour"]
            ReservationStartMinute = self.caregiver_result["SlotMinute"]
            AppointmentDuration = 15
            SlotStatus = 1
            DoseNumber = 1

            sqltext = "UPDATE Patients SET VaccineStatus = 1 WHERE PatientId = {}".format(self.PatientId)
            cursor.execute(sqltext)
            cursor.connection.commit()

            Vaccine.ReserveDoses(1, cursor)

            sqltext = ("INSERT INTO VaccineAppointments (VaccineName, PatientId, CaregiverId, ReservationDate, " +
                       "ReservationStartHour, ReservationStartMinute, AppointmentDuration, SlotStatus, DoseNumber)  " +
                       "Values ('{}', {}, {}, '{}', {}, {}, {}, {}, {})".format(VaccineName, self.PatientId, CaregiverId,
                        ReservationDate, ReservationStartHour, ReservationStartMinute, AppointmentDuration, SlotStatus, DoseNumber))
            cursor.execute(sqltext)
            cursor.connection.commit()
            cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            self.firstAppointmentId = cursor.fetchone()['Identity']

            print("First Appointment", self.firstAppointmentId)
            sqltext = "Update CareGiverSchedule Set VaccineAppointmentId = {} WHERE CaregiverSlotSchedulingId = {} and SlotStatus = 1;" \
                .format(self.firstAppointmentId, CaregiverSchedulingID)
            cursor.execute(sqltext)
            cursor.connection.commit()

            # Initial Entry in the Vaccine Appointment Table of the SECOND DOSE
            if dosesPerPatient != 2:
                return

            with SqlConnectionManager(Server=os.getenv("Server"),
                DBname=os.getenv("DBName"),
                UserId=os.getenv("UserID"),
                Password=os.getenv("Password")) as sqlClient:
                new_cursor = sqlClient.cursor(as_dict=True)
                self.reserveAppt2(self.caregiver_result, Vaccine, new_cursor)

            if self.secondAppointmentId >= 0:
                print("Second Appointment", self.secondAppointmentId)
            return self.caregiver_result
        except NotEnoughVaccine:
            print("There is no available vaccine dose available")
            cursor.connection.rollback()
        except ValueError:
            print("The slot is not currently on hold...")
            cursor.connection.rollback()
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Reserving Appointments")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqltext)

    def reserveAppt2(self, appt1, Vaccine, cursor):
        """ appt1 is the row of caregiverschedule table corresponding to first appointement """
        """ date is datetime """
        """ Reserve the first availible slot in 3-6 weeks."""
        date = appt1['WorkDay']
        lowerD = date + timedelta(days=21)
        upperD = date + timedelta(days=42)
        self.secondAppointmentId = -1
        try:
            # Checking if the slot is on hold
            sqltext = ("select * from CareGiverSchedule where WorkDay >= '"
                       + str(lowerD) + "' AND WorkDay <= '" + str(upperD) +
                        "' AND SlotStatus = 0;")
            cursor.execute(sqltext)
            self.appt2Result = cursor.fetchone()
            if not self.appt2Result:
                print("we have reserved your first appointment but there is not second appointment slot available.")

            # Find an opening in the caregiver schedule
            sqltext = "Update CareGiverSchedule Set SlotStatus = 1 WHERE CaregiverSlotSchedulingId = {} and SlotStatus = 0;"\
                .format(str(self.appt2Result['CaregiverSlotSchedulingId']))
            cursor.execute(sqltext)
            cursor.connection.commit()

            VaccineName = Vaccine.vaccine
            CaregiverId = self.appt2Result['CaregiverId']
            ReservationDate = self.appt2Result['WorkDay']
            ReservationStartHour = self.appt2Result["SlotHour"]
            ReservationStartMinute = self.appt2Result["SlotMinute"]
            AppointmentDuration = 15
            SlotStatus = 1
            DoseNumber = 2

            Vaccine.ReserveDoses(1, cursor)

            sqltext = ("INSERT INTO VaccineAppointments (VaccineName, PatientId, CaregiverId, ReservationDate, " +
                       "ReservationStartHour, ReservationStartMinute, AppointmentDuration, SlotStatus, DoseNumber)  " +
                       "Values ('{}', {}, {}, '{}', {}, {}, {}, {}, {})".format(VaccineName, self.PatientId, CaregiverId,
                        ReservationDate, ReservationStartHour, ReservationStartMinute, AppointmentDuration, SlotStatus, DoseNumber))
            cursor.execute(sqltext)
            cursor.connection.commit()

            cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            self.secondAppointmentId = cursor.fetchone()['Identity']

            sqltext = "Update CareGiverSchedule Set VaccineAppointmentId = {} WHERE CaregiverSlotSchedulingId = {} and SlotStatus = 1;" \
                .format(self.secondAppointmentId, str(appt2Result['CaregiverSlotSchedulingId']))
            cursor.execute(sqltext)
            cursor.connection.commit()

        except NotEnoughVaccine:
            print("We have reserved your first appointment but there is either no second appointment slot available or not enough doses left.")
            self.secondAppointmentId = -1
            cursor.connection.rollback()
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Reserving Appointments")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqltext)

    def ScheduleAppointment(self, cursor):
        appt1 = self.caregiver_result
        appt2 = self.appt2Result

        print('A1',appt1)
        print('A2',appt2)

        vaccApptId1 = appt1['VaccineAppointmentId']
        vaccApptId2 = appt2['VaccineAppointmentId']

        #caregiverSlotStat = 2

        try:
            sqltext1 = "Update CareGiverSchedule Set SlotStatus = 2 WHERE CaregiverSlotSchedulingId = " \
                        + str(appt1['CaregiverSlotSchedulingId']) + ";"

            sqltext2 = "Update CareGiverSchedule Set SlotStatus = 2 WHERE CaregiverSlotSchedulingId = " \
                        + str(appt2['CaregiverSlotSchedulingId']) + ";"

            cursor.execute(sqltext1)
            cursor.connection.commit()
            cursor.execute(sqltext2)
            cursor.connection.commit()

            print('id', vaccApptId1, vaccApptId2)

            sqltext3 = "SELECT * FROM VaccineAppointments WHERE VaccineAppointmentId = '"\
                        + str(vaccApptId1) + "' OR VaccineAppointmentId =  '" + str(vaccApptId2) + "';"

            cursor.execute(sqltext3)
            vaccineAppts = cursor.fetchall()
            print('Vacc:', vaccineAppts)
            pId1 = vaccineAppts[0]['PatientId']
            pId2 = vaccineAppts[1]['PatientId']

            print(pId1, pId2)

            sqltext4 = "Update Patient Set VaccineStatus = 2 WHERE PatientId = " + str(pId1) + ";"
            sqltext5 = "Update Patient Set VaccineStatus = 5 WHERE PatientId = " + str(pId2) + ";"

            cursor.execute(sqltext4)
            cursor.connection.commit()

            if not pId2:
                cursor.execute(sqltext5)
                cursor.connection.commit()

        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Reserving Appointments")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error")

