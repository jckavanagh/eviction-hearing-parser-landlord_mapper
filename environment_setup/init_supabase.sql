-- Eviction Hearing Parser - Supabase Database Initialization
-- Run this script in Supabase SQL Editor to set up all tables and views

-- =============================================
-- TABLES
-- =============================================

-- 1. CASE_DETAIL (Primary table)
CREATE TABLE IF NOT EXISTS CASE_DETAIL (
    CASE_NUMBER TEXT PRIMARY KEY NOT NULL,
    STATUS TEXT NOT NULL,
    REGISTER_URL TEXT NOT NULL,
    PRECINCT INT NOT NULL,
    STYLE TEXT NOT NULL,
    PLAINTIFF TEXT,
    DEFENDANTS TEXT,
    PLAINTIFF_ZIP TEXT,
    DEFENDANT_ZIP TEXT,
    CASE_TYPE TEXT,
    DATE_FILED TEXT,
    ACTIVE_OR_INACTIVE TEXT,
    JUDGMENT_AFTER_MORATORIUM TEXT,
    FIRST_COURT_APPEARANCE DATE
);

-- 2. DISPOSITION (References CASE_DETAIL)
CREATE TABLE IF NOT EXISTS DISPOSITION (
    ID SERIAL PRIMARY KEY,
    CASE_NUMBER TEXT NOT NULL UNIQUE,
    TYPE TEXT,
    DATE TEXT NOT NULL,
    AMOUNT TEXT,
    AWARDED_TO TEXT,
    AWARDED_AGAINST TEXT,
    ATTORNEYS_FOR_PLAINTIFFS TEXT,
    ATTORNEYS_FOR_DEFENDANTS TEXT,
    JUDGEMENT_FOR TEXT,
    MATCH_SCORE TEXT,
    COMMENTS TEXT,
    FOREIGN KEY(CASE_NUMBER) REFERENCES CASE_DETAIL(CASE_NUMBER)
);

-- 3. EVENT (References CASE_DETAIL)
CREATE TABLE IF NOT EXISTS EVENT (
    ID SERIAL PRIMARY KEY,
    CASE_NUMBER TEXT NOT NULL,
    EVENT_NUMBER INTEGER NOT NULL,
    DATE TEXT NOT NULL,
    TIME TEXT,
    OFFICER TEXT,
    RESULT TEXT,
    TYPE TEXT NOT NULL,
    ALL_TEXT TEXT,
    FOREIGN KEY(CASE_NUMBER) REFERENCES CASE_DETAIL(CASE_NUMBER),
    UNIQUE(CASE_NUMBER, EVENT_NUMBER)
);

-- 4. SETTING
CREATE TABLE IF NOT EXISTS SETTING (
    ID SERIAL PRIMARY KEY,
    CASE_NUMBER TEXT NOT NULL,
    CASE_LINK TEXT,
    SETTING_TYPE TEXT,
    SETTING_STYLE TEXT,
    JUDICIAL_OFFICER TEXT,
    SETTING_DATE TEXT,
    SETTING_TIME TEXT,
    HEARING_TYPE TEXT
);

-- Create index for SETTING table
CREATE UNIQUE INDEX IF NOT EXISTS idx_setting_case_style_date_time
ON SETTING (CASE_NUMBER, SETTING_TYPE, HEARING_TYPE, SETTING_DATE);

-- =============================================
-- VIEWS
-- =============================================

-- 1. v_case (Combined case and disposition view)
CREATE OR REPLACE VIEW v_case AS
 SELECT DISTINCT
    cd.case_number,
    cd.status,
    cd.register_url,
    cd.precinct,
    cd.style,
    cd.plaintiff,
    cd.defendants,
    cd.plaintiff_zip,
    cd.defendant_zip,
    cd.date_filed as date,
    cd.case_type,
    d.type,
    d.amount,
    d.awarded_to,
    d.awarded_against
   FROM case_detail cd
     LEFT JOIN disposition d ON cd.case_number = d.case_number;

-- 2. eviction_events (Filtered eviction events)
CREATE OR REPLACE VIEW eviction_events AS
 SELECT case_detail.case_number,
    case_detail.case_type,
    event.event_number,
    event.date,
    event."time",
    event.officer,
    event.result,
    event.type,
    event.all_text
   FROM case_detail,
    event
  WHERE case_detail.case_number = event.case_number 
    AND case_detail.case_type = 'Eviction'::text;

-- 3. filings_archive (Archive view)
CREATE OR REPLACE VIEW filings_archive AS
 SELECT case_detail.case_number,
    case_detail.status,
    case_detail.precinct,
    case_detail.style,
    case_detail.plaintiff,
    case_detail.defendants,
    case_detail.plaintiff_zip,
    case_detail.defendant_zip,
    case_detail.case_type,
    case_detail.date_filed,
    case_detail.active_or_inactive,
    case_detail.judgment_after_moratorium,
    case_detail.first_court_appearance,
    disposition.type,
    disposition.date,
    disposition.amount,
    disposition.awarded_to,
    disposition.awarded_against,
    disposition.judgement_for,
    disposition.match_score,
    disposition.attorneys_for_plaintiffs,
    disposition.attorneys_for_defendants,
    disposition.comments
   FROM case_detail,
    disposition
  WHERE case_detail.case_number = disposition.case_number;

-- =============================================
-- DONE!
-- =============================================
-- All tables and views have been created successfully.

