def clear_tables(client):
    sqlQuery = '''
               DELETE FROM CareGiverSchedule
               DBCC CHECKIDENT ('CareGiverSchedule', RESEED, 0)          
               DELETE FROM VaccineAppointments
               DBCC CHECKIDENT ('VaccineAppointments', RESEED, 0)                     
               Truncate TABLE Vaccines         
               DELETE FROM Caregivers
               DBCC CHECKIDENT ('Caregivers', RESEED, 0)                        
               DELETE FROM Patients
               DBCC CHECKIDENT ('Patients', RESEED, 0)             
               '''
    client.cursor().execute(sqlQuery)
    client.commit()
