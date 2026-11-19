
-- 1. Remaining trainers
INSERT INTO trainers
(full_name, email, specialization, hire_date)
VALUES
('Priya Sharma', 'priya@gym.com', 'Yoga', '2022-08-10'),
('Vikram Raj', 'vikram@gym.com', 'Weight Loss', '2023-06-20'),
('Divya Nair', 'divya@gym.com', 'Functional Training', '2021-11-05'),
('Karthik S', 'karthik@gym.com', 'Bodybuilding', '2024-02-12');

-- 2. Membership plans
INSERT INTO membership_plans
(plan_name, duration_months, price)
VALUES
('Monthly', 1, 1500.00),
('Quarterly', 3, 4000.00),
('Half-Yearly', 6, 7500.00),
('Annual', 12, 14000.00);

-- 3. Exercises
INSERT INTO exercises
(exercise_name, muscle_group, difficulty)
VALUES
('Bench Press', 'Chest', 'INTERMEDIATE'),
('Squat', 'Legs', 'INTERMEDIATE'),
('Deadlift', 'Back', 'ADVANCED'),
('Pull Up', 'Back', 'INTERMEDIATE'),
('Shoulder Press', 'Shoulders', 'INTERMEDIATE'),
('Bicep Curl', 'Arms', 'BEGINNER'),
('Tricep Pushdown', 'Arms', 'BEGINNER'),
('Leg Press', 'Legs', 'BEGINNER'),
('Plank', 'Core', 'BEGINNER'),
('Running', 'Cardio', 'BEGINNER');
