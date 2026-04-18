-- Run this in your Supabase SQL editor to create the nutrition_log table.

CREATE TABLE IF NOT EXISTS nutrition_log (
    id                    BIGSERIAL PRIMARY KEY,
    product_name          TEXT,
    serving_size          TEXT,
    servings_per_container TEXT,
    calories              NUMERIC,
    total_fat_g           NUMERIC,
    saturated_fat_g       NUMERIC,
    trans_fat_g           NUMERIC,
    cholesterol_mg        NUMERIC,
    sodium_mg             NUMERIC,
    total_carbohydrates_g NUMERIC,
    dietary_fiber_g       NUMERIC,
    total_sugars_g        NUMERIC,
    added_sugars_g        NUMERIC,
    protein_g             NUMERIC,
    vitamin_d_mcg         NUMERIC,
    calcium_mg            NUMERIC,
    iron_mg               NUMERIC,
    potassium_mg          NUMERIC,
    language              VARCHAR(10),
    notes                 TEXT,
    scanned_at            TIMESTAMPTZ DEFAULT now()
);