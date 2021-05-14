from datetime import datetime
from datetime import timedelta
import pymssql


class COVID19Vaccine:

    def __init__(self, vaccine, cursor):
        try:
            self.vaccine = vaccine.title()

            if vaccine == "Pfizer":
                _DateBetweenDoses = 14
                _DoseNeeded = 2
                _TotalDoses = 0
            elif vaccine == "Moderna":
                _DateBetweenDoses = 28
                _DoseNeeded = 2
                _TotalDoses = 0
            elif vaccine in "J&J":
                _DateBetweenDoses = 0
                _DoseNeeded = 1
                _TotalDoses = 0
            elif vaccine == "AstraZeneca":
                _DateBetweenDoses = 30
                _DoseNeeded = 2
                _TotalDoses = 0
            else:
                raise NameError()
                _DateBetweenDoses = -1
                _DoseNeeded = -1
                _MaxStorageTemperature = -10000

            self.sqltext = \
                "INSERT INTO Vaccines (VaccineName, DaysBetweenDoses, DosesPerPatient, TotalDoses) VALUES ('%s', %d, %d, %d);" % (
                    self.vaccine,
                    _DateBetweenDoses,
                    _DoseNeeded,
                    _TotalDoses
                )
            self.vid = 0

            cursor.execute(self.sqltext)
            cursor.connection.commit()
            cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            _identityRow = cursor.fetchone()
            self.vid = _identityRow['Identity']
            cursor.connection.commit()
            print('Query executed successfully. Vaccine : ' + self.vaccine
                  + ' added to the database using Vaccine ID = ' + str(self.vid))
        except NameError:
            print("Please Add Pfizer, Moderna, J&J or AstraZeneca. For other vaccine, please contact customer service MARK FRIEDMAN at (425) 949-2302")
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for COVID VACCINE! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)


    def AddDoses(self, doses, cursor):
        self.sqltext = \
            "Update Vaccines Set TotalDoses = TotalDoses +  %d Where VaccineName = %s" % (
                doses,
                self.vaccine
            )
        try:
            if doses <= 0:
                raise ValueError()
            cursor.execute(self.sqltext)
            cursor.connection.commit()
            print('Query executed successfully. Dose Added')
        except ValueError as e:
            print("Please add a positive integer. VACCINE NOT ADDED")
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for COVID VACCINE (ADD DOSE)! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)

    def ReserveDoses(self, doses, cursor):
        self.sqltext = \
            "Update Vaccine Set Available = Available -  %d Where Vid = %d" % (
                doses,
                self.vid
            )
        try:
            if doses <= 0:
                raise ValueError()
            cursor.execute(self.sqltext)
            cursor.connection.commit()
            print('Query executed successfully. Dose Deleted')
        except ValueError as e:
            print("Please add a positive integer. VACCINE NOT RESERVED")
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for COVID VACCINE (RESERVE DOSE)! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)

if __name__ == "__main__":
    COVID19Vaccine("pfizer")
