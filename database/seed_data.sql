-- SQL Seed Data for ramayana-sustainability-training Database

-- Modules
INSERT INTO modules (name) VALUES 
('Dharma in Business'), 
('Harmony with Nature'), 
('Collective Welfare'), 
('Resource Management'), 
('Humility and Service');

-- Sample Users
INSERT INTO users (username, password) VALUES 
('admin', '$2b$10$QWzgNRsbkek23M0hpyCR2uzlGdeCb8jIhZgjmKbVNFz2fO33ySAO2'), 
('john_doe', '$2b$10$RTWoSkdPC6SBui7NTtB1V.LvGFe0RRfjcK4uM5J0ljSgTleECiMUm'), 
('jane_smith', '$2b$10$1kyGqD6nE15XHo22fMRu6uVgDiPmO2.nffM6YaI/OPNYmO5T3Ky3m');

-- Sample Progress Data
INSERT INTO progress (user_id, module_id, status) VALUES 
(1, 1, 'completed'), 
(1, 2, 'in-progress'), 
(2, 1, 'not-started'), 
(3, 2, 'completed');
