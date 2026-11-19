
-- ============================================
-- GYM & FITNESS ANALYTICS DATABASE
-- INDEXES AND CONSTRAINTS
-- ============================================

-- Membership lookup indexes
CREATE INDEX idx_memberships_member_id
ON memberships(member_id);

CREATE INDEX idx_memberships_plan_id
ON memberships(plan_id);

CREATE INDEX idx_memberships_status
ON memberships(status);

-- Workout session lookup indexes
CREATE INDEX idx_workout_sessions_member_id
ON workout_sessions(member_id);

CREATE INDEX idx_workout_sessions_trainer_id
ON workout_sessions(trainer_id);

CREATE INDEX idx_workout_sessions_date
ON workout_sessions(session_date);

-- Workout log lookup indexes
CREATE INDEX idx_workout_logs_session_id
ON workout_logs(session_id);

CREATE INDEX idx_workout_logs_exercise_id
ON workout_logs(exercise_id);

-- Exercise lookup index
CREATE INDEX idx_exercises_muscle_group
ON exercises(muscle_group);
