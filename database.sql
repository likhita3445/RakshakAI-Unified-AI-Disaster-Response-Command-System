-- ============================================================================
-- RAKSHAKAI — ENTERPRISE SUPABASE / POSTGRESQL PRODUCTION DATABASE SCHEMA
-- Unified AI Disaster Response Command System with PostGIS & Realtime Support
-- ============================================================================

-- 1. Enable Required PostgreSQL / Supabase Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- 2. Custom Enumerated Types
DO $$ BEGIN
    CREATE TYPE disaster_type_enum AS ENUM ('FLOOD', 'FIRE', 'LANDSLIDE', 'EARTHQUAKE', 'CYCLONE', 'INDUSTRIAL_HAZARD');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE urgency_level_enum AS ENUM ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE agency_type_enum AS ENUM ('COMMANDER', 'NDRF', 'POLICE', 'MEDICAL', 'FIRE', 'SDRF', 'CIVIL_DEFENSE', 'PUBLIC');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE route_status_enum AS ENUM ('CLEAR', 'CONGESTED', 'HAZARD_WARNING', 'BLOCKED', 'DESTROYED');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE dispatch_status_enum AS ENUM ('PENDING', 'DISPATCHED', 'EN_ROUTE', 'ON_SCENE', 'COMPLETED', 'CANCELLED');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE shelter_status_enum AS ENUM ('OPERATIONAL', 'NEAR_CAPACITY', 'FULL', 'STANDBY', 'EVACUATING');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE recon_source_enum AS ENUM ('SATELLITE_ISRO_RISAT', 'SATELLITE_SENTINEL', 'UAV_DRONE_QUAD', 'FIELD_SCOUT', 'CCTV_COMMAND');
EXCEPTION WHEN duplicate_object THEN null; END $$;


-- ============================================================================
-- 3. Core Tables
-- ============================================================================

-- 3.1. Disaster Zones & Inundation Monitoring
CREATE TABLE IF NOT EXISTS public.disaster_zones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_code VARCHAR(32) UNIQUE NOT NULL,            -- e.g. 'ZONE-DELHI-YAMUNA-A'
    name VARCHAR(255) NOT NULL,                       -- e.g. 'Area A — Yamuna Riverbank Zone'
    disaster_type disaster_type_enum NOT NULL DEFAULT 'FLOOD',
    urgency urgency_level_enum NOT NULL DEFAULT 'HIGH',
    priority_score NUMERIC(5, 2) NOT NULL DEFAULT 50.00 CHECK (priority_score >= 0 AND priority_score <= 100),
    
    -- Demographics Telemetry
    total_affected INTEGER NOT NULL DEFAULT 0,
    vulnerable_elderly INTEGER NOT NULL DEFAULT 0,
    vulnerable_children INTEGER NOT NULL DEFAULT 0,
    vulnerable_critical INTEGER NOT NULL DEFAULT 0,
    vulnerable_disabled INTEGER NOT NULL DEFAULT 0,
    vulnerable_pregnant INTEGER NOT NULL DEFAULT 0,
    medical_crisis_flag BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Environmental & Inundation Telemetry
    flood_inundation_percent NUMERIC(5, 2) DEFAULT 0.0 CHECK (flood_inundation_percent >= 0 AND flood_inundation_percent <= 100),
    water_level_meters NUMERIC(6, 2) DEFAULT 0.0,
    water_crest_threshold_meters NUMERIC(6, 2) DEFAULT 205.33,
    
    -- PostGIS Geospatial Location
    location_centroid GEOGRAPHY(Point, 4326) NOT NULL,
    hazard_perimeter GEOGRAPHY(Polygon, 4326),
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3.2. Multilingual Emergency Reports (Citizens & Field Telemetry)
CREATE TABLE IF NOT EXISTS public.emergency_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_code VARCHAR(64) UNIQUE NOT NULL,
    zone_id UUID REFERENCES public.disaster_zones(id) ON DELETE SET NULL,
    
    -- Raw Report Details
    raw_text TEXT NOT NULL,
    input_mode VARCHAR(20) DEFAULT 'VOICE' CHECK (input_mode IN ('VOICE', 'TEXT', 'SMS', 'RADIO_TRANSCRIPT')),
    language_code VARCHAR(10) DEFAULT 'hi',           -- 'hi', 'en', 'bn', 'mr', 'ta', etc.
    caller_phone VARCHAR(32),                         -- Masked/Sanitized PII
    
    -- AI Extracted NLP Entities
    extracted_disaster VARCHAR(64),
    estimated_people_count INTEGER DEFAULT 1,
    medical_emergency BOOLEAN DEFAULT FALSE,
    nlp_confidence NUMERIC(4, 3) DEFAULT 0.950,
    raw_ai_json JSONB DEFAULT '{}'::jsonb,
    
    -- PostGIS Coordinates & Offline Tracking
    location GEOGRAPHY(Point, 4326),
    is_offline_cached BOOLEAN NOT NULL DEFAULT FALSE,
    synced_at TIMESTAMPTZ,
    
    status VARCHAR(32) DEFAULT 'VERIFIED' CHECK (status IN ('PENDING', 'VERIFIED', 'TRIAGED', 'RESOLVED', 'DUPLICATE')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3.3. Dynamic Road Network, Bridges & Evacuation Routes
CREATE TABLE IF NOT EXISTS public.routes_and_bridges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_name VARCHAR(128) NOT NULL,                 -- e.g. 'Route B (Highland Bypass)'
    route_code VARCHAR(32) UNIQUE NOT NULL,           -- e.g. 'ROUTE-B-DEL'
    route_type VARCHAR(32) DEFAULT 'PRIMARY_ROAD',    -- 'HIGHWAY', 'BYPASS', 'WATER_CHANNEL', 'AIR_CORRIDOR'
    status route_status_enum NOT NULL DEFAULT 'CLEAR',
    
    safety_score INTEGER NOT NULL DEFAULT 85 CHECK (safety_score >= 0 AND safety_score <= 100),
    distance_km NUMERIC(6, 2) NOT NULL,
    estimated_transit_minutes INTEGER,
    
    bridge_structural_hazard_percent NUMERIC(5, 2) DEFAULT 0.0,
    submerged_depth_meters NUMERIC(4, 2) DEFAULT 0.0,
    is_recommended_bypass BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Spatial Path Polyline
    route_path GEOGRAPHY(LineString, 4326),
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3.4. Multi-Agency Emergency Resource Inventory
CREATE TABLE IF NOT EXISTS public.resource_inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agency agency_type_enum NOT NULL,
    resource_type VARCHAR(64) NOT NULL,               -- 'ALS_AMBULANCE', 'NDRF_RUBBER_BOAT', 'WATER_AIRDROP_LITERS', 'MEDKIT_CLASS_A'
    base_location_name VARCHAR(128) NOT NULL,
    
    total_quantity INTEGER NOT NULL DEFAULT 0 CHECK (total_quantity >= 0),
    deployed_quantity INTEGER NOT NULL DEFAULT 0 CHECK (deployed_quantity >= 0),
    available_quantity INTEGER GENERATED ALWAYS AS (total_quantity - deployed_quantity) STORED,
    
    staging_coordinates GEOGRAPHY(Point, 4326),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3.5. Tactical Emergency Dispatches & Action Plans
CREATE TABLE IF NOT EXISTS public.dispatches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dispatch_code VARCHAR(64) UNIQUE NOT NULL,        -- e.g. 'DISPATCH-20260825-001'
    zone_id UUID REFERENCES public.disaster_zones(id) ON DELETE RESTRICT,
    assigned_agency agency_type_enum NOT NULL,
    assigned_route_id UUID REFERENCES public.routes_and_bridges(id),
    
    mission_title VARCHAR(255) NOT NULL,
    task_instructions JSONB NOT NULL,                 -- Step-by-step tactical orders
    allocated_resources JSONB NOT NULL,               -- {"ambulances": 2, "ndrf_boats": 1, "water_liters": 500}
    
    status dispatch_status_enum NOT NULL DEFAULT 'DISPATCHED',
    dispatched_by VARCHAR(128) DEFAULT 'RAKSHAKAI_CORE_AI',
    commander_override_notes TEXT,
    
    dispatched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- 3.6. Relief Shelters & Safe Evacuation Hubs (NEW)
CREATE TABLE IF NOT EXISTS public.relief_shelters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shelter_code VARCHAR(32) UNIQUE NOT NULL,         -- e.g. 'SHELTER-NORTH-01'
    name VARCHAR(255) NOT NULL,                       -- e.g. 'North District Stadium Community Shelter'
    status shelter_status_enum NOT NULL DEFAULT 'OPERATIONAL',
    
    total_capacity INTEGER NOT NULL DEFAULT 500 CHECK (total_capacity > 0),
    current_occupancy INTEGER NOT NULL DEFAULT 0 CHECK (current_occupancy >= 0),
    available_beds INTEGER GENERATED ALWAYS AS (total_capacity - current_occupancy) STORED,
    
    has_medical_bay BOOLEAN NOT NULL DEFAULT TRUE,
    has_backup_generator BOOLEAN NOT NULL DEFAULT TRUE,
    food_ration_kits_available INTEGER DEFAULT 1000,
    potable_water_liters INTEGER DEFAULT 5000,
    
    contact_officer_name VARCHAR(128),
    contact_phone VARCHAR(32),
    
    location_coordinates GEOGRAPHY(Point, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3.7. Satellite & Drone Computer Vision Reconnaissance (NEW)
CREATE TABLE IF NOT EXISTS public.drone_satellite_recon (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recon_code VARCHAR(64) UNIQUE NOT NULL,           -- e.g. 'RECON-YAMUNA-DRONE-04'
    source_type recon_source_enum NOT NULL DEFAULT 'UAV_DRONE_QUAD',
    zone_id UUID REFERENCES public.disaster_zones(id) ON DELETE SET NULL,
    
    image_url TEXT,
    flight_altitude_meters NUMERIC(6, 2) DEFAULT 120.0,
    flooded_area_sq_km NUMERIC(6, 2) NOT NULL DEFAULT 0.0,
    collapsed_structures_count INTEGER DEFAULT 0,
    bridge_collapse_detected BOOLEAN NOT NULL DEFAULT FALSE,
    ai_vision_confidence_percent NUMERIC(5, 2) DEFAULT 94.80,
    
    detected_victim_clusters JSONB DEFAULT '[]'::jsonb, -- [{'lat': 28.614, 'lng': 77.209, 'est_count': 35}]
    bounding_box_geom GEOGRAPHY(Polygon, 4326),
    
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3.8. IoT River Sensor & Weather Telemetry Stream (NEW)
CREATE TABLE IF NOT EXISTS public.sensor_telemetry_streams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sensor_code VARCHAR(32) NOT NULL,                 -- e.g. 'IOT-YAMUNA-BRIDGE-04'
    sensor_type VARCHAR(32) NOT NULL,                 -- 'WATER_LEVEL_ULTRASONIC', 'RIVER_VELOCITY', 'RAIN_GAUGE'
    current_reading_value NUMERIC(8, 2) NOT NULL,
    unit_of_measure VARCHAR(16) NOT NULL,             -- 'METERS', 'M_PER_SEC', 'MM_PER_HR'
    
    warning_threshold NUMERIC(8, 2) NOT NULL,
    critical_threshold NUMERIC(8, 2) NOT NULL,
    is_threshold_breached BOOLEAN GENERATED ALWAYS AS (current_reading_value >= critical_threshold) STORED,
    
    sensor_coordinates GEOGRAPHY(Point, 4326) NOT NULL,
    reading_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3.9. AI Decision Explainability & Math Traceability
CREATE TABLE IF NOT EXISTS public.explainability_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_id UUID REFERENCES public.disaster_zones(id) ON DELETE CASCADE,
    priority_score_calculated NUMERIC(5, 2) NOT NULL,
    
    -- Formula Factor Weights Breakdown
    population_score_points NUMERIC(5, 2) NOT NULL,
    vulnerable_score_points NUMERIC(5, 2) NOT NULL,
    medical_urgency_points NUMERIC(5, 2) NOT NULL,
    route_penalty_points NUMERIC(5, 2) NOT NULL,
    flood_severity_points NUMERIC(5, 2) NOT NULL,
    
    detailed_factors JSONB NOT NULL,
    prompt_context_used TEXT,
    ai_model_version VARCHAR(64) DEFAULT 'RakshakAI-Local-v2.0',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3.10. Cryptographic Tamper-Proof Audit Chain (Legal & Judicial Inquiries)
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sequence_id BIGSERIAL UNIQUE,
    agency agency_type_enum NOT NULL,
    action_type VARCHAR(64) NOT NULL,                 -- 'DISPATCH_APPROVED', 'ROUTE_CLOSED', 'OVERRIDE_EXECUTED'
    details JSONB NOT NULL,
    actor_id VARCHAR(128) NOT NULL,                   -- User ID / Commander ID
    ip_address INET,
    
    -- Blockchain-style SHA-256 hash chaining
    previous_entry_hash VARCHAR(64) NOT NULL DEFAULT '',
    current_entry_hash VARCHAR(64) NOT NULL,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================================
-- 4. Spatial & Performance Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_disaster_zones_centroid ON public.disaster_zones USING GIST (location_centroid);
CREATE INDEX IF NOT EXISTS idx_disaster_zones_priority ON public.disaster_zones (priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_emergency_reports_location ON public.emergency_reports USING GIST (location);
CREATE INDEX IF NOT EXISTS idx_routes_path ON public.routes_and_bridges USING GIST (route_path);
CREATE INDEX IF NOT EXISTS idx_shelters_location ON public.relief_shelters USING GIST (location_coordinates);
CREATE INDEX IF NOT EXISTS idx_dispatches_status ON public.dispatches (status);
CREATE INDEX IF NOT EXISTS idx_recon_bounding ON public.drone_satellite_recon USING GIST (bounding_box_geom);
CREATE INDEX IF NOT EXISTS idx_sensor_telemetry_time ON public.sensor_telemetry_streams (sensor_code, reading_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_sequence ON public.audit_logs (sequence_id);


-- ============================================================================
-- 5. Stored Procedures & Geospatial Queries
-- ============================================================================

-- 5.1. Find Nearest Available Resources by Radius
CREATE OR REPLACE FUNCTION public.find_nearest_resources(
    p_lat DOUBLE PRECISION,
    p_lng DOUBLE PRECISION,
    p_radius_km DOUBLE PRECISION DEFAULT 15.0,
    p_agency agency_type_enum DEFAULT NULL
)
RETURNS TABLE (
    inventory_id UUID,
    agency agency_type_enum,
    resource_type VARCHAR,
    available_qty INTEGER,
    base_name VARCHAR,
    distance_km DOUBLE PRECISION
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.id,
        r.agency,
        r.resource_type,
        r.available_quantity,
        r.base_location_name,
        ST_Distance(r.staging_coordinates, ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326)::geography) / 1000.0 AS distance_km
    FROM public.resource_inventory r
    WHERE r.available_quantity > 0
      AND (p_agency IS NULL OR r.agency = p_agency)
      AND ST_DWithin(r.staging_coordinates, ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326)::geography, p_radius_km * 1000.0)
    ORDER BY distance_km ASC;
END;
$$;

-- 5.2. Find Nearest Open Relief Shelter with Available Capacity (NEW)
CREATE OR REPLACE FUNCTION public.find_nearest_open_shelter(
    p_lat DOUBLE PRECISION,
    p_lng DOUBLE PRECISION,
    p_required_beds INTEGER DEFAULT 10
)
RETURNS TABLE (
    shelter_id UUID,
    shelter_name VARCHAR,
    available_beds INTEGER,
    has_medical BOOLEAN,
    distance_km DOUBLE PRECISION
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id,
        s.name,
        s.available_beds,
        s.has_medical_bay,
        ST_Distance(s.location_coordinates, ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326)::geography) / 1000.0 AS distance_km
    FROM public.relief_shelters s
    WHERE s.status IN ('OPERATIONAL', 'NEAR_CAPACITY')
      AND s.available_beds >= p_required_beds
    ORDER BY distance_km ASC
    LIMIT 5;
END;
$$;

-- 5.3. Auto-Update Timestamp Trigger
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_disaster_zones_updated BEFORE UPDATE ON public.disaster_zones FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_routes_updated BEFORE UPDATE ON public.routes_and_bridges FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_shelters_updated BEFORE UPDATE ON public.relief_shelters FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


-- ============================================================================
-- 6. Analytical Views for Command Dashboard
-- ============================================================================

-- 6.1. Live Emergency Command Dashboard Overview View
CREATE OR REPLACE VIEW public.v_live_disaster_command_matrix AS
SELECT 
    z.id AS zone_id,
    z.zone_code,
    z.name AS zone_name,
    z.disaster_type,
    z.urgency,
    z.priority_score,
    z.total_affected,
    (z.vulnerable_elderly + z.vulnerable_children + z.vulnerable_critical + z.vulnerable_disabled) AS total_vulnerable_count,
    z.medical_crisis_flag,
    z.flood_inundation_percent,
    COALESCE(COUNT(DISTINCT r.id), 0) AS verified_emergency_reports_count,
    COALESCE(COUNT(DISTINCT d.id) FILTER (WHERE d.status = 'DISPATCHED'), 0) AS active_dispatches_count
FROM public.disaster_zones z
LEFT JOIN public.emergency_reports r ON r.zone_id = z.id
LEFT JOIN public.dispatches d ON d.zone_id = z.id
GROUP BY z.id;


-- ============================================================================
-- 7. Supabase Row Level Security (RLS) & Realtime Publication
-- ============================================================================

ALTER TABLE public.disaster_zones ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.emergency_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.routes_and_bridges ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resource_inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dispatches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.relief_shelters ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.drone_satellite_recon ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sensor_telemetry_streams ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.explainability_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- 7.1. Public Read Policies for Critical Alerts & Evacuation
CREATE POLICY "Public can view active disaster zones" ON public.disaster_zones FOR SELECT USING (true);
CREATE POLICY "Public can view safe route status" ON public.routes_and_bridges FOR SELECT USING (true);
CREATE POLICY "Public can view open shelters" ON public.relief_shelters FOR SELECT USING (true);
CREATE POLICY "Public can submit emergency reports" ON public.emergency_reports FOR INSERT WITH CHECK (true);

-- 7.2. Authenticated Agencies Full Access Policies
CREATE POLICY "Commanders and Responders manage dispatches" ON public.dispatches FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users view inventory" ON public.resource_inventory FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users view drone recon" ON public.drone_satellite_recon FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "System generates audit logs" ON public.audit_logs FOR INSERT WITH CHECK (true);
CREATE POLICY "Public cannot alter audit logs" ON public.audit_logs FOR UPDATE USING (false);

-- 7.3. Enable Supabase Realtime for Live Map & Dispatches
ALTER PUBLICATION supabase_realtime ADD TABLE public.disaster_zones;
ALTER PUBLICATION supabase_realtime ADD TABLE public.emergency_reports;
ALTER PUBLICATION supabase_realtime ADD TABLE public.dispatches;
ALTER PUBLICATION supabase_realtime ADD TABLE public.routes_and_bridges;
ALTER PUBLICATION supabase_realtime ADD TABLE public.relief_shelters;
ALTER PUBLICATION supabase_realtime ADD TABLE public.sensor_telemetry_streams;


-- ============================================================================
-- 8. Seed Telemetry Data
-- ============================================================================

INSERT INTO public.disaster_zones (zone_code, name, disaster_type, urgency, priority_score, total_affected, vulnerable_elderly, vulnerable_children, vulnerable_critical, vulnerable_disabled, medical_crisis_flag, flood_inundation_percent, location_centroid)
VALUES 
('ZONE-DEL-A', 'Area A — Yamuna Riverbank Zone', 'FLOOD', 'CRITICAL', 94.00, 850, 42, 17, 8, 12, true, 85.00, ST_SetSRID(ST_MakePoint(77.2090, 28.6139), 4326)::geography),
('ZONE-DEL-B', 'Area B — North District Sector 4', 'FLOOD', 'HIGH', 72.00, 420, 12, 5, 2, 4, false, 40.00, ST_SetSRID(ST_MakePoint(77.2090, 28.6640), 4326)::geography),
('ZONE-DEL-C', 'Area C — East Colony Shelter', 'FLOOD', 'MEDIUM', 38.00, 180, 5, 2, 0, 1, false, 25.00, ST_SetSRID(ST_MakePoint(77.2800, 28.6250), 4326)::geography)
ON CONFLICT (zone_code) DO NOTHING;

INSERT INTO public.routes_and_bridges (route_name, route_code, status, safety_score, distance_km, estimated_transit_minutes, is_recommended_bypass)
VALUES
('Route B (Highland Bypass)', 'ROUTE-B-BYPASS', 'CLEAR', 96, 7.4, 14, true),
('Route A (Direct Highway)', 'ROUTE-A-HWY', 'BLOCKED', 12, 4.2, 999, false),
('Route C (East Corridor)', 'ROUTE-C-EAST', 'HAZARD_WARNING', 74, 10.1, 22, false)
ON CONFLICT (route_code) DO NOTHING;

INSERT INTO public.relief_shelters (shelter_code, name, total_capacity, current_occupancy, has_medical_bay, food_ration_kits_available, potable_water_liters, location_coordinates)
VALUES
('SHELTER-NORTH-01', 'North District Stadium Safe Center', 1000, 240, true, 1800, 8500, ST_SetSRID(ST_MakePoint(77.1950, 28.6720), 4326)::geography),
('SHELTER-EAST-02', 'East Delhi Community Relief Shelter', 600, 110, true, 950, 4200, ST_SetSRID(ST_MakePoint(77.2750, 28.6300), 4326)::geography)
ON CONFLICT (shelter_code) DO NOTHING;

INSERT INTO public.drone_satellite_recon (recon_code, source_type, flooded_area_sq_km, collapsed_structures_count, bridge_collapse_detected, ai_vision_confidence_percent, detected_victim_clusters)
VALUES
('RECON-DEL-DRONE-01', 'UAV_DRONE_QUAD', 4.20, 42, true, 94.80, '[{"lat": 28.6139, "lng": 77.2090, "est_count": 35, "status": "ROOFTOP_STRANDED"}]'::jsonb)
ON CONFLICT (recon_code) DO NOTHING;

INSERT INTO public.sensor_telemetry_streams (sensor_code, sensor_type, current_reading_value, unit_of_measure, warning_threshold, critical_threshold, sensor_coordinates)
VALUES
('IOT-YAMUNA-BRIDGE-04', 'WATER_LEVEL_ULTRASONIC', 206.50, 'METERS', 205.33, 206.00, ST_SetSRID(ST_MakePoint(77.2090, 28.6139), 4326)::geography);
