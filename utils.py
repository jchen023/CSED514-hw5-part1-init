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


# def clear_tables(client):
#     sqlQuery = '''
#                Truncate Table CareGiverSchedule
#                DBCC CHECKIDENT ('CareGiverSchedule', RESEED, 0)
#                Delete From Caregivers
#                DBCC CHECKIDENT ('Caregivers', RESEED, 0)
#                Truncate TABLE VaccineAppointment
#                DBCC CHECKIDENT ('VaccineAppointment', RESEED, 0)
#                Delete FROM Vaccine
#                DBCC CHECKIDENT ('Vaccine', RESEED, 0)
#                '''
#     client.cursor().execute(sqlQuery)
#     client.commit()

  # Truncate Table VaccineAppointment
  #              DBCC CHECKIDENT ('VaccineAppointment', RESEED, 0)
  #              Delete Table Vaccine
  #              DBCC CHECKIDENT ('Vaccine', RESEED, 0)