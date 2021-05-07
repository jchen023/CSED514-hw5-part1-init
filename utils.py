def clear_tables(client):
    sqlQuery = '''
               Truncate Table CareGiverSchedule
               DBCC CHECKIDENT ('CareGiverSchedule', RESEED, 0)
               Delete From Caregivers
               DBCC CHECKIDENT ('Caregivers', RESEED, 0)
               Truncate TABLE VaccineAppointment
               DBCC CHECKIDENT ('VaccineAppointment', RESEED, 0)
               Delete FROM Vaccine
               DBCC CHECKIDENT ('Vaccine', RESEED, 0)
               '''
    client.cursor().execute(sqlQuery)
    client.commit()
  # Truncate Table VaccineAppointment
  #              DBCC CHECKIDENT ('VaccineAppointment', RESEED, 0)
  #              Delete Table Vaccine
  #              DBCC CHECKIDENT ('Vaccine', RESEED, 0)