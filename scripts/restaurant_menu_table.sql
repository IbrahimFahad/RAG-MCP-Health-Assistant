-- Run this in your Supabase SQL editor to create the restaurant_menu table

CREATE TABLE IF NOT EXISTS restaurant_menu (
    id              BIGSERIAL PRIMARY KEY,
    restaurant_key  TEXT NOT NULL,
    restaurant_name TEXT NOT NULL,
    restaurant_ar   TEXT NOT NULL,
    restaurant_cat  TEXT NOT NULL,
    restaurant_emoji TEXT NOT NULL,
    item_name       TEXT NOT NULL,
    item_name_ar    TEXT NOT NULL,
    item_category   TEXT NOT NULL,
    calories        INTEGER,
    protein_g       NUMERIC(6,1),
    carbs_g         NUMERIC(6,1),
    fat_g           NUMERIC(6,1),
    sodium_mg       NUMERIC(8,1),
    fiber_g         NUMERIC(6,1),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast restaurant filtering
CREATE INDEX IF NOT EXISTS idx_restaurant_menu_key ON restaurant_menu(restaurant_key);
CREATE INDEX IF NOT EXISTS idx_restaurant_menu_calories ON restaurant_menu(calories);