from datetime import datetime
from datetime import timedelta
import pymssql


class COVID19Vaccine:
    ''' Adds the CareGiver to the DB and adds vaccine scheduling slots '''
    def __init__(self, vaccine):
        self.vaccine = vaccine
        self.sqltext = "INSERT INTO Vaccine (VaccineName) VALUES ('" + vaccine + "')"
        self.caregiverId = 0
        try:
            cursor.execute(self.sqltext)
            cursor.connection.commit()
            cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            _identityRow = cursor.fetchone()
            self.caregiverId = _identityRow['Identity']
            # cursor.connection.commit()
            print('Query executed successfully. Caregiver : ' + name
                  + ' added to the database using Caregiver ID = ' + str(self.caregiverId))
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Caregivers! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)



    def AddDoses(self, doses, cursor):
        self.sqltext = "Update Vaccine Set capacity = capacity



    def ReserveDoses(self, doses, cursor):

        cursor.connection.commit()

print