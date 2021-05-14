from datetime import datetime
from datetime import timedelta
import vaccine_caregiver
import pymssql


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
            sqltext = ("select SlotStatus from CareGiverSchedule where CaregiverSlotSchedulingId = %d"
                       % (CaregiverSchedulingID))
            cursor.execute(sqltext)
            slotStatus = cursor.fetchone()['SlotStatus']
            if slotStatus != 1:
                raise ValueError()

            sqltext = "select "


        except ValueError:
            print("The slot is not currently on hold...")
            cursor.connection.rollback()
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Reserving Appointments")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqltext)

    def ScheduleAppointment(self):
        pass


