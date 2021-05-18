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
            # Checking if the slot is on hold
            sqltext = ("select * from CareGiverSchedule where CaregiverSlotSchedulingId = %d"
                       % (CaregiverSchedulingID))
            cursor.execute(sqltext)
            caregiver_result = cursor.fetchone()
            slotStatus = caregiver_result['SlotStatus']
            if slotStatus != 1:
                raise ValueError()

            # Reserving Vaccine Doses
            sqltext = "select DosesPerPatient from Vaccines where VaccineName = '{}'".format(Vaccine.vaccine)
            cursor.execute(sqltext)
            dosesPerPatient = cursor.fetchone()["DosesPerPatient"]
            Vaccine.ReserveDoses(dosesPerPatient, cursor)

            # Initial Entry in the Vaccine Appointment Table of the FIRST DOSE
            VaccineName = Vaccine.vaccine
            CaregiverId = caregiver_result['CaregiverId']
            ReservationDate = caregiver_result['WorkDay']
            ReservationStartHour = caregiver_result["SlotHour"]
            ReservationStartMinute = caregiver_result["SlotMinute"]
            AppointmentDuration = 15
            SlotStatus = 1
            DoseNumber = 1

            sqltext = ("INSERT INTO VaccineAppointments (VaccineName, PatientId, CaregiverId, ReservationDate, " +
                       "ReservationStartHour, ReservationStartMinute, AppointmentDuration, SlotStatus, DoseNumber)  " +
                       "Values ('{}', {}, {}, '{}', {}, {}, {}, {}, {})".format(VaccineName, self.PatientId, CaregiverId,
                        ReservationDate, ReservationStartHour, ReservationStartMinute, AppointmentDuration, SlotStatus, DoseNumber))
            cursor.execute(sqltext)
            cursor.connection.commit()
            cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            self.firstAppointmentId = cursor.fetchone()['Identity']

            # Initial Entry in the Vaccine Appointment Table of the SECOND DOSE
            if dosesPerPatient != 2:
                return 
            else:
                self.reserveAppt2(caregiver_result, VaccineName, cursor)

            # use caregiverschedulerid put on hold dose # 2


        except ValueError:
            print("The slot is not currently on hold...")
            cursor.connection.rollback()
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Reserving Appointments")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqltext)
        
        return caregiver_result 

    def reserveAppt2(self, appt1, Vaccine, cursor):  #date
        # appt1 is the row of caregiverschedule table corresponding to first appointement
        # date is datetime
        #reserve first availible slot in 3-6 weeks with same caregiver. 
        date = appt1['WorkDay']
        lowerD = date + timedelta(days = 21)  #21
        upperD = date + timedelta(days = 42)  #42

        CaregiverID = appt1['CaregiverId']
        #print(type(upperD), upperD)
        #print(type(str(upperD)))
        try:
            # Checking if the slot is on hold
            sqltext = ("select * from CareGiverSchedule where CaregiverId ="
                        + str(CaregiverID) + " AND (WorkDay >= '" + str(lowerD) + "' AND WorkDay <= '" + str(upperD) + 
                        "') AND SlotStatus = 0;") 
            cursor.execute(sqltext)
            appt2Result = cursor.fetchone()
            #slotStatus = appt2Result['SlotStatus']
            print(sqltext,appt2Result)
            
            if (appt2Result == None):
                raise ValueError()

            # might need to change value for slotstatus in the update
            sqltext2 = "Update CareGiverSchedule Set SlotStatus = 1 WHERE CaregiverSlotSchedulingId = '" + str(appt2Result['CaregiverSlotSchedulingId']) + "' ;"
            cursor.execute(sqltext2)
            cursor.connection.commit()

            # Reserving Vaccine Doses
            # sqltext = "select DosesPerPatient from Vaccines where VaccineName = '{}'".format(Vaccine.vaccine)
            # cursor.execute(sqltext)
            # dosesPerPatient = cursor.fetchone()["DosesPerPatient"]
            # Vaccine.ReserveDoses(dosesPerPatient, cursor)

            # Initial Entry in the Vaccine Appointment Table of the FIRST DOSE
            VaccineName = Vaccine
            CaregiverId = appt2Result['CaregiverId']
            ReservationDate = appt2Result['WorkDay']
            ReservationStartHour = appt2Result["SlotHour"]
            ReservationStartMinute = appt2Result["SlotMinute"]
            AppointmentDuration = 15
            SlotStatus = 1
            DoseNumber = 2

            sqltext = ("INSERT INTO VaccineAppointments (VaccineName, PatientId, CaregiverId, ReservationDate, " +
                       "ReservationStartHour, ReservationStartMinute, AppointmentDuration, SlotStatus, DoseNumber)  " +
                       "Values ('{}', {}, {}, '{}', {}, {}, {}, {}, {})".format(VaccineName, self.PatientId, CaregiverId,
                        ReservationDate, ReservationStartHour, ReservationStartMinute, AppointmentDuration, SlotStatus, DoseNumber))
            cursor.execute(sqltext)
            cursor.connection.commit()

            # cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            # self.firstAppointmentId = cursor.fetchone()['Identity']

            # use caregiverschedulerid put on hold dose # 2
            print('Appt 1: ',date)
            #print('Appt 2: ',ReservationDate)
            print('Appt 2: ', appt2Result['WorkDay'])
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


