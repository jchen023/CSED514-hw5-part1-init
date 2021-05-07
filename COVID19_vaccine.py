from datetime import datetime
from datetime import timedelta
import pymssql


class COVID19Vaccine:
    ''' Adds the CareGiver to the DB and adds vaccine scheduling slots '''
    def __init__(self, vaccine, cursor):
        self.vaccine = vaccine

        if vaccine == "Pfizer":
            _DateBetweenDoses = 14
            _DoseNeeded = 2
            _MaxStorageTemperature = -70
        elif vaccine == "Moderna":
            _DateBetweenDoses = 28
            _DoseNeeded = 2
            _MaxStorageTemperature = -20
        elif vaccine == "J&J":
            _DateBetweenDoses = 0
            _DoseNeeded = 1
            _MaxStorageTemperature = 90
        elif vaccine == "AstraZeneca":
            _DateBetweenDoses = 30
            _DoseNeeded = 2
            _MaxStorageTemperature = 36
        else:
            _DateBetweenDoses = -1
            _DoseNeeded = -1
            _MaxStorageTemperature = -10000


        self.sqltext = \
            "INSERT INTO Vaccine (VaccineName, DateBetweenDoses, DoseNeeded, MaxStorageTemperature) VALUES ('%s', %d, %d, %d);" % (
                self.vaccine,
                _DateBetweenDoses,
                _DoseNeeded,
                _MaxStorageTemperature
            )
        print(self.sqltext)
        self.vid = 0
        try:
            cursor.execute(self.sqltext)
            cursor.connection.commit()
            cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            _identityRow = cursor.fetchone()
            self.vid = _identityRow['Identity']
            cursor.connection.commit()
            print('Query executed successfully. Vaccine : ' + self.vaccine
                  + ' added to the database using Vaccine ID = ' + str(self.vid))
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for COVID VACCINE! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)


    def AddDoses(self, doses, cursor):
        self.sqltext = \
            "Update Vaccine Set Inventory = Inventory +  %d Where Vid = %d" % (
                doses,
                self.vid
            )
        try:
            cursor.execute(self.sqltext)
            cursor.connection.commit()
            print('Query executed successfully. Dose Added')
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for COVID VACCINE (ADD DOSE)! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)

    def ReserveDoses(self, doses, cursor):
        self.sqltext = \
            "Update Vaccine Set Inventory = Inventory -  %d Where Vid = %d" % (
                doses,
                self.vid
            )
        try:
            cursor.execute(self.sqltext)
            cursor.connection.commit()
            print('Query executed successfully. Dose Deleted')
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for COVID VACCINE (Delete DOSE)! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)

if __name__ == "__main__":
    COVID19Vaccine("pfizer")
