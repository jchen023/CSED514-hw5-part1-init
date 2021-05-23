from datetime import datetime
from datetime import timedelta
import vaccine_caregiver
import pymssql
from sql_connection_manager import SqlConnectionManager
import os

class NotEnoughVaccine(Exception):
    pass

class DoneWithVaccine(Exception):
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
            self.firstAppointmentId, self.secondAppointmentId = -1, -1

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
            if self.PatientStatusCode >= 7:  # probably replace 4 with 7
                raise DoneWithVaccine

            if self.PatientStatusCode == 0:
                # This is the part where we let others schedule their first dose
                # If they already have scheduled their first dose, their status code would be 1
                # and would go on to trying to schedule their second dose, after the if statement.
                # This is, of course, based on the fact that we would put status code for
                # patients who received one dose vaccine as "two-dose received" to avoid any confusion.

                # Checking if the slot is on hold
                sqltext = ("select * from CareGiverSchedule where CaregiverSlotSchedulingId = %d"
                           % (CaregiverSchedulingID))
                cursor.execute(sqltext)
                caregiver_result = cursor.fetchone()
                slotStatus = caregiver_result['SlotStatus']
                if slotStatus != 1:
                    raise ValueError()
                self.firstCareGiverSchedulingId = CaregiverSchedulingID

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
                CaregiverId = caregiver_result['CaregiverId']
                ReservationDate = caregiver_result['WorkDay']
                ReservationStartHour = caregiver_result["SlotHour"]
                ReservationStartMinute = caregiver_result["SlotMinute"]
                AppointmentDuration = 15
                SlotStatus = 1
                DoseNumber = 1

                sqltext = "UPDATE Patients SET VaccineStatus = 1 WHERE PatientId = {}".format(self.PatientId)
                cursor.execute(sqltext)
                cursor.connection.commit()
                self.PatientStatusCode = 1

                Vaccine.ReserveDoses(1, cursor)

                sqltext = ("INSERT INTO VaccineAppointments (VaccineName, PatientId, CaregiverId, ReservationDate, " +
                           "ReservationStartHour, ReservationStartMinute, AppointmentDuration, SlotStatus, DoseNumber)  " +
                           "Values ('{}', {}, {}, '{}', {}, {}, {}, {}, {})".format(VaccineName, self.PatientId, CaregiverId,
                            ReservationDate, ReservationStartHour, ReservationStartMinute, AppointmentDuration, SlotStatus, DoseNumber))
                cursor.execute(sqltext)
                cursor.connection.commit()
                cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
                self.firstAppointmentId = cursor.fetchone()['Identity']

                sqltext = "Update CareGiverSchedule Set VaccineAppointmentId = {} WHERE CaregiverSlotSchedulingId = {} and SlotStatus = 1;" \
                    .format(self.firstAppointmentId, CaregiverSchedulingID)
                cursor.execute(sqltext)
                cursor.connection.commit()

                print("{}'s First Appointment ID: {}; CareGiverScheduler ID: {}".format(self.PatientName,
                                                                                        self.firstAppointmentId,
                                                                                        self.firstCareGiverSchedulingId))

                # Initial Entry in the Vaccine Appointment Table of the SECOND DOSE
                if dosesPerPatient != 2:
                    return

            with SqlConnectionManager(Server=os.getenv("Server"),
                DBname=os.getenv("DBName"),
                UserId=os.getenv("UserID"),
                Password=os.getenv("Password")) as sqlClient:
                new_cursor = sqlClient.cursor(as_dict=True)
                self.reserveAppt2(caregiver_result, Vaccine, new_cursor)

            if self.secondAppointmentId >= 0:
                print("{}'s Second Appointment ID: {}; CareGiverScheduler ID: {}".format(self.PatientName,
                                                                                        self.secondAppointmentId,
                                                                                        self.secondCareGiverSchedulingId))
        except NotEnoughVaccine:
            print("There is no available vaccine dose available for {}".format(self.PatientName))
            cursor.connection.rollback()
            self.firstAppointmentId, self.firstCareGiverSchedulingId = -1, -1
        except DoneWithVaccine:
            cursor.connection.rollback()
            print("{} has already scheduled both vaccines, please patiently wait for your booster shot.".format(
                self.PatientName))
            raise DoneWithVaccine
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
        try:
            # Checking if the slot is on hold
            sqltext = ("select * from CareGiverSchedule where WorkDay >= '"
                       + str(lowerD) + "' AND WorkDay <= '" + str(upperD) +
                        "' AND SlotStatus = 0 ORDER BY WorkDay, SlotHour;")
            cursor.execute(sqltext)
            appt2Result = cursor.fetchone()
            if not appt2Result:
                raise NotEnoughVaccine
            self.secondCareGiverSchedulingId = appt2Result['CaregiverSlotSchedulingId']

            # Find an opening in the caregiver schedule
            sqltext = "Update CareGiverSchedule Set SlotStatus = 1 WHERE CaregiverSlotSchedulingId = {} and SlotStatus = 0;"\
                .format(str(appt2Result['CaregiverSlotSchedulingId']))
            cursor.execute(sqltext)
            cursor.connection.commit()


            VaccineName = Vaccine.vaccine
            CaregiverId = appt2Result['CaregiverId']
            ReservationDate = appt2Result['WorkDay']
            ReservationStartHour = appt2Result["SlotHour"]
            ReservationStartMinute = appt2Result["SlotMinute"]
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
                .format(str(self.secondAppointmentId), str(self.secondCareGiverSchedulingId))
            cursor.execute(sqltext)
            cursor.connection.commit()

        except NotEnoughVaccine:
            print("We have reserved {}'s first appointment but there is either no second appointment slot available or not enough doses left.".format(self.PatientName))
            self.secondAppointmentId, self.secondCareGiverSchedulingId= -1, -1
            cursor.connection.rollback()
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Reserving Appointments")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqltext)

    def ScheduleAppointment(self, cursor):
        # Vaccines Inventory is handled in the reservation function.
        try:
            if self.firstAppointmentId >= 0:
                sqltext1 = "Update CareGiverSchedule Set SlotStatus = 2 WHERE CaregiverSlotSchedulingId = " \
                            + str(self.firstCareGiverSchedulingId) + "and SlotStatus = 1;" + \
                           "Update Patients Set VaccineStatus = 2 WHERE PatientId = " + str(self.PatientId) + \
                               "AND VaccineStatus = 1;" +\
                            " Update VaccineAppointments Set SlotStatus = 2 WHERE VaccineAppointmentId  = "+ \
                           str(self.firstAppointmentId) + " AND SlotStatus = 1;"
                cursor.execute(sqltext1)
                cursor.connection.commit()
            if self.secondAppointmentId >= 0:
                sqltext2 = "Update CareGiverSchedule Set SlotStatus = 2 WHERE CaregiverSlotSchedulingId = " \
                        + str(self.secondCareGiverSchedulingId) + "and SlotStatus = 1;" + \
                       "Update Patients Set VaccineStatus = 5 WHERE PatientId = " + str(self.PatientId) + \
                           "AND VaccineStatus = 4;" +\
                        " Update VaccineAppointments Set SlotStatus = 2 WHERE VaccineAppointmentId  = "+ \
                           str(self.secondAppointmentId) + " AND SlotStatus = 1;"
                cursor.execute(sqltext2)
                cursor.connection.commit()

        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Reserving Appointments")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error")

