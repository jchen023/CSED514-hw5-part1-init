import datetime
from enum import IntEnum
import os
import pymssql
import traceback

from sql_connection_manager import SqlConnectionManager
from vaccine_caregiver import VaccineCaregiver
from enums import *
from utils import *
from COVID19_vaccine import COVID19Vaccine as covid
from VaccinePatient import VaccinePatient as patient


class VaccineReservationScheduler:

    def __init__(self):
        return

    def PutHoldOnAppointmentSlot(self, cursor):
        ''' Method that reserves a CareGiver appointment slot &
        returns the unique scheduling slotid
        Should return -2 if no slot is available  or -1 if there is a database error'''

        # Note to students: this is a stub that needs to replaced with your code

        # replacing 0 with -2 to cover edge case
        #
        self.slotSchedulingId = -2
        self.getAppointmentSQL = "SELECT * FROM CareGiverSchedule WHERE SlotStatus = 0 ORDER BY WorkDay, SlotHour;"
        try:
            cursor.execute(self.getAppointmentSQL)
            rows = cursor.fetchone()
            self.slotSchedulingId = rows['CaregiverSlotSchedulingId']

            if rows:
                sqlText = "Update CareGiverSchedule Set SlotStatus = 1 WHERE CaregiverSlotSchedulingId =" \
                          + str(rows['CaregiverSlotSchedulingId']) + "and SlotStatus = 0;"
                cursor.execute(sqlText)
                cursor.connection.commit()
            return self.slotSchedulingId

        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])           
            print("SQL text that resulted in an Error: " + self.getAppointmentSQL)
            cursor.connection.rollback()
            return -1

    def ScheduleAppointmentSlot(self, slotid, cursor):
        '''method that marks a slot on Hold with a definite reservation  
        slotid is the slot that is currently on Hold and whose status will be updated 
        returns the same slotid when the database update succeeds 
        returns -2 is there if the database update fails
        returns -1 the same slotid when the database command fails
        returns 21 if the slotid parm is invalid '''
        # Note to students: this is a stub that needs to replaced with your code
        if slotid < 0:
            return -2
        self.slotSchedulingId = slotid

        self.getAppointmentSQL = "SELECT * FROM CareGiverSchedule WHERE SlotStatus = 1 AND CaregiverSlotSchedulingId =" + str(self.slotSchedulingId) + ";"

        try:
            cursor.execute(self.getAppointmentSQL)
            rows = cursor.fetchone()

            if rows:
                sqlText = "Update CareGiverSchedule Set SlotStatus = 2 WHERE CaregiverSlotSchedulingId =" + \
                          str(self.slotSchedulingId) + ";"
                cursor.execute(sqlText)
                cursor.connection.commit()
            else:
                print('Invalid SlotID')
                self.slotSchedulingId = 21
            return self.slotSchedulingId

        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing! ")
            print("Exception code: " + db_err.args[0])
            if len(db_err.args) > 1:
                print("Exception message: " + str(db_err.args[1]))  
            print("SQL text that resulted in an Error: " + self.getAppointmentSQL)
            return -1


if __name__ == '__main__':
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:

            clear_tables(sqlClient)
            vrs = VaccineReservationScheduler()

            # get a cursor from the SQL connection
            dbcursor = sqlClient.cursor(as_dict=True)
            dbcursor_1 = sqlClient.cursor(as_dict=True)

            # Initialize the caregivers, patients & vaccine supply
            caregiversList = []
            caregiversList.append(VaccineCaregiver('Carrie Nation', dbcursor))
            caregiversList.append(VaccineCaregiver('Clare Barton', dbcursor))
            caregivers = {}
            for cg in caregiversList:
                cgid = cg.caregiverId
                caregivers[cgid] = cg

            moderna = covid('Moderna', dbcursor)
            moderna.AddDoses(7, dbcursor)
            # b.ReserveDoses(7, dbcursor)
            # c = covid('hello world', dbcursor)

            p1 = patient('Mark Friedman', 0, dbcursor_1)
            print('LOOK')
            p1.ReserveAppointment(vrs.PutHoldOnAppointmentSlot(dbcursor_1), moderna, dbcursor_1)

            # Add a vaccine and Add doses to inventory of the vaccine
            # Ass patients
            # Schedule the patients
            
            # Test cases done!
            # clear_tables(sqlClient)
