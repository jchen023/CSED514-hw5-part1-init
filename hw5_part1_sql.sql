-- Given CREATE TABLE statements to start your databas
Create Table Caregivers(
	CaregiverId int IDENTITY PRIMARY KEY,
	CaregiverName varchar(50)
	);

Create Table AppointmentStatusCodes(
	StatusCodeId int PRIMARY KEY,
	StatusCode   varchar(30)
);

INSERT INTO AppointmentStatusCodes (statusCodeId, StatusCode)
	VALUES (0, 'Open');
INSERT INTO AppointmentStatusCodes (statusCodeId, StatusCode)
	VALUES (1, 'OnHold');
INSERT INTO AppointmentStatusCodes (statusCodeId, StatusCode)
	VALUES (2, 'Scheduled');
INSERT INTO AppointmentStatusCodes (statusCodeId, StatusCode)
	VALUES (3, 'Completed');
INSERT INTO AppointmentStatusCodes (statusCodeId, StatusCode)
	VALUES (4, 'Missed');

Create Table CareGiverSchedule(
	CaregiverSlotSchedulingId int Identity PRIMARY KEY, 
	CaregiverId int DEFAULT 0 NOT NULL
		CONSTRAINT FK_CareGiverScheduleCaregiverId FOREIGN KEY (caregiverId)
			REFERENCES Caregivers(CaregiverId),
	WorkDay date,
	SlotTime time,
	SlotHour int DEFAULT 0 NOT NULL,
	SlotMinute int DEFAULT 0 NOT NULL,
	SlotStatus int  DEFAULT 0 NOT NULL
		CONSTRAINT FK_CaregiverStatusCode FOREIGN KEY (SlotStatus) 
		     REFERENCES AppointmentStatusCodes(StatusCodeId),
	VaccineAppointmentId int DEFAULT 0 NOT NULL);


Create Table Vaccine(
	Vid INT Identity,
	CaregiverId INT REFERENCES Caregivers(CaregiverId),
	VaccineName VARCHAR(50),
	DateBetweenDoses INT,
	DoseNeeded INT,
	MinStorageTemperature FLOAT,
	Inventory INT DEFAULT 0 NOT NULL
	Primary Key (CaregiverId, Vid)
);


Create Table Patient(
	PatientId INT Primary Key,
	PatientName VARCHAR(50),
	Zipcode INT,
	Phone VARCHAR(15),
	DOB DATE
);

Create Table VaccineAppointment(
	VaccineAppointmentId INT PRIMARY KEY,
	PatientId INT REFERENCES Patient(PatientId),
	CaregiverId INT REFERENCES Caregivers(CareGiverId),
	Vid INT REFERENCES Vaccine,
	DoseNumber INT DEFAULT 1
);



-- INSERT INTO Vaccine (Vid,VaccineName,DateBetweenDoses, DoseNeeded, MinStorageTemperature) VALUES (1, 'Pfizer', 14, 2, -60.0),
-- (2, 'Moderna', 28,2, -20.0), (3, 'J&J',0, 1, 0.0);



-- Update vaccine set DoseNeeded = DoseNeeded + 2

-- select * from vaccine

-- Additional helper code for your use if needed

-- --- Drop commands to restructure the DB
-- DROP TABLE VaccineAppointment
-- DROP TABLE Patient
-- DROP TABLE VaccineInventory
-- DROP TABLE Vaccine
-- Drop Table CareGiverSchedule
-- Drop Table AppointmentStatusCodes
-- Drop Table Caregivers



-- Go

-- --- Commands to clear the active database Tables for unit testing
-- Truncate Table CareGiverSchedule
-- DBCC CHECKIDENT ('CareGiverSchedule', RESEED, 0)
-- Delete From Caregivers
-- DBCC CHECKIDENT ('Caregivers', RESEED, 0)
<<<<<<< HEAD
-- GO

-------------------------------------------------------
-- Create Table Vaccine(
-- 	Vid INT PRIMARY KEY,
-- 	VaccineName VARCHAR(50),
-- 	DateBetweenDoses INT,
-- 	DoseNeeded INT,
-- 	MinStorageTemperature FLOAT
-- );

-- Create Table VaccineInventory(
-- 	Cid INT REFERENCES Caregivers(CaregiverId),
-- 	Vid INT REFERENCES Vaccine(Vid),
-- 	Inventory INT DEFAULT 0 NOT NULL,
-- 	Primary Key (Cid, Vid)
-- );

-- INSERT INTO Vaccine (Vid,VaccineName,DateBetweenDoses, DoseNeeded, MinStorageTemperature) VALUES (1, 'Pfizer', 14, 2, -60.0),
-- (2, 'Moderna', 28,2, -20.0), (3, 'J&J',0, 3, 0.0);
=======
-- GO
>>>>>>> 895877ec97444b169ed840bdd9089676694f81b3
