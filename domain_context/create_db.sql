CREATE TABLE CarCategories (
    CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    CategoryName TEXT
);

CREATE TABLE CarModels (
    ModelID INTEGER PRIMARY KEY AUTOINCREMENT,
    ModelName TEXT,
    CategoryID INTEGER,
    ImageURL TEXT,
    FOREIGN KEY (CategoryID) REFERENCES CarCategories (CategoryID)
);

CREATE TABLE CarGrades (
    GradeID INTEGER PRIMARY KEY AUTOINCREMENT,
    GradeName TEXT,
    Description TEXT,
    ModelID INTEGER,
    FOREIGN KEY (ModelID) REFERENCES CarModels (ModelID)
);

CREATE TABLE Engines (
    EngineID INTEGER PRIMARY KEY AUTOINCREMENT,
    EngineType TEXT
);

CREATE TABLE Bases (
    BaseID INTEGER PRIMARY KEY AUTOINCREMENT,
    GradeID INTEGER,
    EngineID INTEGER,
    BasePrice INTEGER,
    Rank INTEGER,
    FuelEfficiency REAL,
    FuelCostPerKilo REAL,
    MonthlyMainteCost REAL,
    MonthlyInsuranceCost REAL,
    MonthlyParkingCost REAL,
    MonthlyPriceDropRate REAL,
    FOREIGN KEY (GradeID) REFERENCES CarGrades (GradeID),
    FOREIGN KEY (EngineID) REFERENCES Engines (EngineID)
);

CREATE TABLE Colors (
    ColorID INTEGER PRIMARY KEY AUTOINCREMENT,
    ColorName TEXT,
    ImageURL TEXT,
    AdditionalCost INTEGER
);

CREATE TABLE Exteriors (
    ExteriorID INTEGER PRIMARY KEY AUTOINCREMENT,
    Item TEXT,
    ImageURL TEXT,
    AdditionalCost INTEGER
);

CREATE TABLE GradeExteriors (
    GradeExteriorID INTEGER PRIMARY KEY AUTOINCREMENT,
    GradeID INTEGER,
    ExteriorID INTEGER,
    FOREIGN KEY (GradeID) REFERENCES CarGrades (GradeID),
    FOREIGN KEY (ExteriorID) REFERENCES Exteriors (ExteriorID)
);

CREATE TABLE Interiors (
    InteriorID INTEGER PRIMARY KEY AUTOINCREMENT,
    Item TEXT,
    ImageURL TEXT,
    AdditionalCost INTEGER
);

CREATE TABLE GradeInteriors (
    GradeInteriorID INTEGER PRIMARY KEY AUTOINCREMENT,
    GradeID INTEGER,
    InteriorID INTEGER,
    FOREIGN KEY (GradeID) REFERENCES CarGrades (GradeID),
    FOREIGN KEY (InteriorID) REFERENCES Interiors (InteriorID)
);

CREATE TABLE Customizations (
    CustomizationID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER,
    BaseID INTEGER,
    FOREIGN KEY (UserID) REFERENCES Users (UserID),
    FOREIGN KEY (BaseID) REFERENCES Bases (BaseID)
);

CREATE TABLE ExteriorCustomizations (
    ExteriorCustomizationID INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomizationID INTEGER,
    ExteriorID INTEGER,
    FOREIGN KEY (CustomizationID) REFERENCES Customizations (CustomizationID),
    FOREIGN KEY (ExteriorID) REFERENCES Exteriors (ExteriorID)
);

CREATE TABLE ColorCustomizations (
    ColorCustomizationID INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomizationID INTEGER,
    ColorID INTEGER,
    FOREIGN KEY (CustomizationID) REFERENCES Customizations (CustomizationID),
    FOREIGN KEY (ColorID) REFERENCES Colors (ColorID)
);

CREATE TABLE InteriorCustomizations (
    InteriorCustomizationID INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomizationID INTEGER,
    InteriorID INTEGER,
    FOREIGN KEY (CustomizationID) REFERENCES Customizations (CustomizationID),
    FOREIGN KEY (InteriorID) REFERENCES Interiors (InteriorID)
);

CREATE TABLE Users (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserName TEXT,
    Email TEXT,
    Place TEXT
);