
-- ============================================
-- GYM & FITNESS ANALYTICS DATABASE
-- TABLE CREATION
-- ============================================

-- 1. MEMBERS
CREATE TABLE members (
    member_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20),
    join_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TRAINERS
CREATE TABLE trainers (
    trainer_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    hire_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. MEMBERSHIP PLANS
CREATE TABLE membership_plans (
    plan_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    plan_name VARCHAR(50) UNIQUE NOT NULL,
    duration_months INT NOT NULL CHECK (duration_months > 0),
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. MEMBERSHIPS
CREATE TABLE memberships (
    membership_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    member_id INT NOT NULL REFERENCES members(member_id),
    plan_id INT NOT NULL REFERENCES membership_plans(plan_id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_membership_dates
        CHECK (end_date >= start_date),

    CONSTRAINT valid_membership_status
        CHECK (status IN ('ACTIVE', 'EXPIRED', 'CANCELLED'))
);

-- 5. EXERCISES
CREATE TABLE exercises (
    exercise_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    exercise_name VARCHAR(100) UNIQUE NOT NULL,
    muscle_group VARCHAR(50) NOT NULL,
    difficulty VARCHAR(20) NOT NULL,

    CONSTRAINT valid_difficulty
        CHECK (difficulty IN ('BEGINNER', 'INTERMEDIATE', 'ADVANCED'))
);

-- 6. WORKOUT SESSIONS
CREATE TABLE workout_sessions (
    session_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    member_id INT NOT NULL REFERENCES members(member_id),
    trainer_id INT REFERENCES trainers(trainer_id),
    session_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    duration_minutes INT CHECK (duration_minutes > 0),
    notes TEXT
);

-- 7. WORKOUT LOGS
CREATE TABLE workout_logs (
    workout_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id INT NOT NULL REFERENCES workout_sessions(session_id),
    exercise_id INT NOT NULL REFERENCES exercises(exercise_id),
    sets INT NOT NULL CHECK (sets > 0),
    reps INT NOT NULL CHECK (reps > 0),
    weight_kg NUMERIC(6,2) NOT NULL DEFAULT 0
        CHECK (weight_kg >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
