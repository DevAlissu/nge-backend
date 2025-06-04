-- Tabela Setor
CREATE TABLE Setor (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    estimated_consumption DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabela Monitoring
CREATE TABLE Monitoring (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL DEFAULT '',
    description VARCHAR(500) NOT NULL,
    estimated_consumption DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabela TypeSection
CREATE TABLE TypeSection (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabela ProductionLine
CREATE TABLE ProductionLine (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    value_mensuration_estimated DOUBLE PRECISION NOT NULL,
    setor_id INTEGER REFERENCES Setor(id) ON DELETE SET NULL
);

-- Tabela Equipament
CREATE TABLE Equipament (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    power DOUBLE PRECISION NOT NULL DEFAULT 0,
    tension DOUBLE PRECISION NOT NULL DEFAULT 0,
    energy_consumption DOUBLE PRECISION NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    max_consumption DOUBLE PRECISION NOT NULL DEFAULT 0,
    min_consumption DOUBLE PRECISION NOT NULL DEFAULT 0,
    production_line_id INTEGER REFERENCES ProductionLine(id) ON DELETE SET NULL
);

-- Tabela DeviceIot
CREATE TABLE DeviceIot (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    type_device VARCHAR(255),
    equipement_id INTEGER REFERENCES Equipament(id) ON DELETE SET NULL
);

-- Tabela Section
CREATE TABLE Section (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    is_monitored BOOLEAN NOT NULL DEFAULT FALSE,
    monitoring_id INTEGER REFERENCES Monitoring(id) ON DELETE SET NULL,
    setor_id INTEGER REFERENCES Setor(id) ON DELETE SET NULL,
    productionLine_id INTEGER REFERENCES ProductionLine(id) ON DELETE SET NULL,
    equipament_id INTEGER REFERENCES Equipament(id) ON DELETE SET NULL,
    DeviceIot_id INTEGER REFERENCES DeviceIot(id) ON DELETE SET NULL,
    type_section_id INTEGER REFERENCES TypeSection(id) ON DELETE SET NULL,
    secticon_parent_id INTEGER REFERENCES Section(id) ON DELETE SET NULL
);

-- Tabela HistoricalMeasurement
CREATE TABLE HistoricalMeasurement (
    id SERIAL PRIMARY KEY,
    total_consumption DOUBLE PRECISION NOT NULL,
    start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    monitoring_id INTEGER REFERENCES Monitoring(id) ON DELETE SET NULL
);

-- Tabela EquipamentLine
CREATE TABLE EquipamentLine (
    id SERIAL PRIMARY KEY,
    create_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    productionLine_id INTEGER REFERENCES ProductionLine(id) ON DELETE SET NULL,
    equipament_id INTEGER REFERENCES Equipament(id) ON DELETE SET NULL
);

-- Tabela AssociationIot
CREATE TABLE AssociationIot (
    id SERIAL PRIMARY KEY,
    date_association TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    monitoring_id INTEGER REFERENCES Monitoring(id) ON DELETE SET NULL,
    device_iot_id INTEGER REFERENCES DeviceIot(id) ON DELETE SET NULL,
    section_id INTEGER REFERENCES Section(id) ON DELETE SET NULL
);

-- Tabela Product
CREATE TABLE Product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    photo VARCHAR(255) DEFAULT 'product_photos/default_avatar.png'
);

-- Tabela ProductItem
CREATE TABLE ProductItem (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    barcode VARCHAR(255),
    product_id INTEGER REFERENCES Product(id) ON DELETE SET NULL
);

-- Tabela Mensuration
CREATE TABLE Mensuration (
    id SERIAL PRIMARY KEY,
    date_mensuration TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    value_mensuration DOUBLE PRECISION NOT NULL,
    type_mensuration VARCHAR(255) NOT NULL,
    equipament_id INTEGER REFERENCES Equipament(id) ON DELETE SET NULL,
    ProductItem_id INTEGER REFERENCES ProductItem(id) ON DELETE SET NULL
);

-- Tabela ReportEffiency
CREATE TABLE ReportEffiency (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    consumption_total DOUBLE PRECISION NOT NULL,
    production_total DOUBLE PRECISION NOT NULL,
    efficiency DOUBLE PRECISION NOT NULL,
    period TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    setor_id INTEGER REFERENCES Setor(id) ON DELETE SET NULL
);

-- Tabela CustomUser
CREATE TABLE CustomUser (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(254) NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'GAME',
    name VARCHAR(255),
    avatar_url VARCHAR(255) DEFAULT 'product_photos/default_avatar.png',
    total_nansen_coins DOUBLE PRECISION NOT NULL DEFAULT 0,
    total_xp DOUBLE PRECISION NOT NULL DEFAULT 0,
    nivel INTEGER NOT NULL DEFAULT 1,
    last_activity TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    setor_id INTEGER REFERENCES Setor(id) ON DELETE SET NULL,
    productionLine_id INTEGER REFERENCES ProductionLine(id) ON DELETE SET NULL,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabela Mission
CREATE TABLE Mission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    quantity_na DOUBLE PRECISION NOT NULL DEFAULT 0,
    energy_meta DOUBLE PRECISION NOT NULL DEFAULT 0,
    nansen_coins DOUBLE PRECISION NOT NULL DEFAULT 0,
    quantity_xp DOUBLE PRECISION NOT NULL DEFAULT 0,
    status VARCHAR(15) NOT NULL DEFAULT 'Pendente',
    date_start DATE NOT NULL,
    date_end DATE NOT NULL,
    is_order_production BOOLEAN NOT NULL DEFAULT FALSE,
    monitoring_id INTEGER REFERENCES Monitoring(id) ON DELETE SET NULL,
    product_id INTEGER REFERENCES Product(id) ON DELETE SET NULL
);

-- Tabela Mission_Users (intermediária para ManyToMany entre Mission e CustomUser)
CREATE TABLE Mission_Users (
    id SERIAL PRIMARY KEY,
    mission_id INTEGER REFERENCES Mission(id) ON DELETE CASCADE,
    customuser_id INTEGER REFERENCES CustomUser(id) ON DELETE CASCADE,
    UNIQUE (mission_id, customuser_id)
);

-- Tabela MissionProgress
CREATE TABLE MissionProgress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES CustomUser(id) ON DELETE CASCADE,
    mission_id INTEGER REFERENCES Mission(id) ON DELETE CASCADE,
    status VARCHAR(15) NOT NULL DEFAULT 'Pendente',
    current_progress DOUBLE PRECISION NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, mission_id)
);

-- Tabela Achievement
CREATE TABLE Achievement (
    id SERIAL PRIMARY KEY,
    user_achievement_id INTEGER REFERENCES CustomUser(id) ON DELETE CASCADE,
    mission_id INTEGER REFERENCES Mission(id) ON DELETE SET NULL,
    description TEXT NOT NULL,
    nansen_coins DOUBLE PRECISION NOT NULL DEFAULT 0,
    quantity_xp DOUBLE PRECISION NOT NULL DEFAULT 0,
    nivel INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabela Reward
CREATE TABLE Reward (
    id SERIAL PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    points DOUBLE PRECISION NOT NULL,
    type_reward VARCHAR(100) NOT NULL,
    mission_id INTEGER REFERENCES Mission(id) ON DELETE SET NULL
);

-- Tabela Claim
CREATE TABLE Claim (
    id SERIAL PRIMARY KEY,
    data_claim TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(255) NOT NULL,
    user_claim_id INTEGER REFERENCES CustomUser(id) ON DELETE SET NULL,
    reward_id INTEGER REFERENCES Reward(id) ON DELETE SET NULL
);

-- Tabela Quiz
CREATE TABLE Quiz (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL
);

-- Tabela MissionQuiz
CREATE TABLE MissionQuiz (
    id SERIAL PRIMARY KEY,
    create_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mission_id INTEGER REFERENCES Mission(id) ON DELETE SET NULL,
    quiz_id INTEGER REFERENCES Quiz(id) ON DELETE SET NULL
);

-- Tabela Question
CREATE TABLE Question (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES Quiz(id) ON DELETE CASCADE,
    text TEXT NOT NULL DEFAULT ''
);

-- Tabela ResponseQuiz
CREATE TABLE ResponseQuiz (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES Question(id) ON DELETE CASCADE,
    text VARCHAR(255) NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE
);

-- Tabela UserResponse
CREATE TABLE UserResponse (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES CustomUser(id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES Question(id) ON DELETE CASCADE,
    selected_response_id INTEGER REFERENCES ResponseQuiz(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabela ProductLoja
CREATE TABLE ProductLoja (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    image VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0
);

-- Tabela Compra
CREATE TABLE Compra (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES CustomUser(id) ON DELETE CASCADE,
    data_compra TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finalizada BOOLEAN NOT NULL DEFAULT TRUE
);

-- Tabela ItemCompra
CREATE TABLE ItemCompra (
    id SERIAL PRIMARY KEY,
    compra_id INTEGER REFERENCES Compra(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES ProductLoja(id) ON DELETE CASCADE,
    quantidade INTEGER NOT NULL,
    preco_unitario DECIMAL(10,2) NOT NULL
);