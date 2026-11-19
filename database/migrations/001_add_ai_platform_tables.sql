
-- =================================================
-- AI GYM INTELLIGENCE PLATFORM
-- MIGRATION 001: AI-READY OPERATIONAL TABLES
-- =================================================

-- 1. ATTENDANCE
CREATE TABLE attendance (
    attendance_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    member_id INT NOT NULL
        REFERENCES members(member_id),

    check_in TIMESTAMP NOT NULL,
    check_out TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_attendance_time
        CHECK (check_out IS NULL OR check_out > check_in)
);


-- 2. PAYMENTS
CREATE TABLE payments (
    payment_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    membership_id INT NOT NULL
        REFERENCES memberships(membership_id),

    amount NUMERIC(10,2) NOT NULL
        CHECK (amount > 0),

    payment_date TIMESTAMP NOT NULL,

    payment_method VARCHAR(30) NOT NULL,

    payment_status VARCHAR(20) NOT NULL,

    transaction_reference VARCHAR(100) UNIQUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_payment_method
        CHECK (
            payment_method IN (
                'UPI',
                'CARD',
                'CASH',
                'NET_BANKING'
            )
        ),

    CONSTRAINT valid_payment_status
        CHECK (
            payment_status IN (
                'SUCCESS',
                'FAILED',
                'PENDING',
                'REFUNDED'
            )
        )
);


-- 3. MEMBER GOALS
CREATE TABLE member_goals (
    goal_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    member_id INT NOT NULL
        REFERENCES members(member_id),

    goal_type VARCHAR(30) NOT NULL,

    target_value NUMERIC(10,2) NOT NULL
        CHECK (target_value > 0),

    unit VARCHAR(30) NOT NULL,

    start_date DATE NOT NULL,

    target_date DATE NOT NULL,

    goal_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    completed_at DATE,

    CONSTRAINT valid_goal_completion_date
        CHECK (
            completed_at IS NULL
            OR (
                completed_at >= start_date
                AND completed_at <= target_date
            )
        ),

    CONSTRAINT valid_goal_status
        CHECK (
            goal_status IN (
                'ACTIVE',
                'COMPLETED',
                'ABANDONED'
            )
        )
);


-- 4. PERFORMANCE INDEXES

CREATE INDEX idx_attendance_member_id
ON attendance(member_id);

CREATE INDEX idx_attendance_check_in
ON attendance(check_in);

CREATE INDEX idx_payments_membership_id
ON payments(membership_id);

CREATE INDEX idx_payments_payment_date
ON payments(payment_date);

CREATE INDEX idx_payments_status
ON payments(payment_status);

CREATE INDEX idx_member_goals_member_id
ON member_goals(member_id);

CREATE INDEX idx_member_goals_status
ON member_goals(goal_status);
