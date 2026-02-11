-- InsuranceHub Seed Data
-- Realistic Dutch insurance market data for demonstration

-- ============================================================
-- INSURERS
-- ============================================================
INSERT INTO insurers (name, code, api_endpoint, api_format, api_status, last_sync, contact_email, contact_phone, address, kvk_number)
VALUES
    ('Achmea', 'ACH', 'http://localhost:5000/mock/achmea', 'json', 'active',
     NOW() - INTERVAL '2 hours', 'api@achmea.nl', '+31 55 579 8100',
     'Handelsweg 2, 3707 NH Zeist', '27154399'),

    ('Aegon', 'AEG', 'http://localhost:5000/mock/aegon', 'xml', 'active',
     NOW() - INTERVAL '4 hours', 'connect@aegon.nl', '+31 70 344 3210',
     'Aegonplein 50, 2591 TV Den Haag', '27085000'),

    ('Allianz Nederland', 'ALZ', 'http://localhost:5000/mock/allianz', 'json', 'active',
     NOW() - INTERVAL '1 hour', 'partner@allianz.nl', '+31 10 440 3500',
     'Coolsingel 139, 3012 AG Rotterdam', '24077400'),

    ('ASR Nederland', 'ASR', 'http://localhost:5000/mock/asr', 'json', 'active',
     NOW() - INTERVAL '3 hours', 'intermediair@asr.nl', '+31 30 257 9111',
     'Archimedeslaan 10, 3584 BA Utrecht', '30070695'),

    ('NN Group', 'NNG', 'http://localhost:5000/mock/nn', 'xml', 'error',
     NOW() - INTERVAL '48 hours', 'api@nn-group.com', '+31 70 513 0303',
     'Schenkkade 65, 2595 AS Den Haag', '52387534'),

    ('Nationale-Nederlanden', 'NAT', 'http://localhost:5000/mock/nn-direct', 'json', 'active',
     NOW() - INTERVAL '6 hours', 'connect@nn.nl', '+31 70 513 0202',
     'Weena 505, 3013 AL Rotterdam', '27127564');

-- ============================================================
-- PRODUCTS
-- ============================================================

-- Achmea products
INSERT INTO products (insurer_id, product_code, name, product_type, description, base_premium, coverage_amount, deductible, rules_json, status, effective_date)
VALUES
    (1, 'ACH-WOZ-001', 'Woonhuis Verzekering Basis', 'property',
     'Basisverzekering voor uw woning tegen brand, storm en inbraak',
     25.50, 250000, 250,
     '{"age_factor": 1.0, "region_factor": {"north": 0.95, "south": 1.05, "west": 1.10, "east": 0.90}, "construction_year_discount": {"before_1970": 1.15, "1970_2000": 1.0, "after_2000": 0.90}}',
     'active', '2024-01-01'),

    (1, 'ACH-WOZ-002', 'Woonhuis Verzekering Plus', 'property',
     'Uitgebreide woonverzekering inclusief glasschade en leidingwater',
     42.75, 500000, 150,
     '{"age_factor": 1.0, "region_factor": {"north": 0.95, "south": 1.05, "west": 1.10, "east": 0.90}, "glass_coverage": true, "water_damage": true}',
     'active', '2024-01-01'),

    (1, 'ACH-INB-001', 'Inboedelverzekering Standaard', 'property',
     'Verzekering voor uw huisraad en persoonlijke bezittingen',
     15.80, 75000, 100,
     '{"value_factor": 1.0, "student_discount": 0.85}',
     'active', '2024-01-01'),

    (1, 'ACH-AUTO-001', 'Autoverzekering WA', 'auto',
     'Wettelijke aansprakelijkheid voor uw auto',
     35.00, 2500000, 0,
     '{"age_driver_factor": {"18-24": 1.8, "25-34": 1.2, "35-54": 1.0, "55+": 1.1}, "claim_free_years": {"0": 1.5, "1-3": 1.2, "4-7": 1.0, "8+": 0.75}, "mileage_factor": {"low": 0.9, "medium": 1.0, "high": 1.15}}',
     'active', '2024-01-01'),

    (1, 'ACH-AUTO-002', 'Autoverzekering AllRisk', 'auto',
     'Volledige cascodekking voor uw voertuig',
     85.00, 2500000, 500,
     '{"age_driver_factor": {"18-24": 1.8, "25-34": 1.2, "35-54": 1.0, "55+": 1.1}, "vehicle_value_factor": 0.03, "claim_free_years": {"0": 1.5, "1-3": 1.2, "4-7": 1.0, "8+": 0.75}}',
     'active', '2024-01-01');

-- Aegon products
INSERT INTO products (insurer_id, product_code, name, product_type, description, base_premium, coverage_amount, deductible, rules_json, status, effective_date)
VALUES
    (2, 'AEG-LIFE-001', 'Levensverzekering Standaard', 'life',
     'Overlijdensrisicoverzekering met vaste looptijd',
     15.75, 100000, 0,
     '{"age_factor": {"18-30": 0.8, "31-45": 1.0, "46-60": 1.5, "61-75": 2.5}, "smoker_surcharge": 1.5, "term_years": [10, 15, 20, 25, 30]}',
     'active', '2024-01-01'),

    (2, 'AEG-LIFE-002', 'Levensverzekering Premium', 'life',
     'Uitgebreide levensverzekering met opbouwwaarde',
     45.00, 300000, 0,
     '{"age_factor": {"18-30": 0.8, "31-45": 1.0, "46-60": 1.5, "61-75": 2.5}, "smoker_surcharge": 1.5, "investment_component": true}',
     'active', '2024-01-01'),

    (2, 'AEG-HEALTH-001', 'Zorgverzekering Basis', 'health',
     'Basiszorgverzekering conform overheid',
     128.50, 0, 385,
     '{"mandatory": true, "dental_addon": 8.50, "physio_addon": 12.00}',
     'active', '2024-01-01'),

    (2, 'AEG-REIS-001', 'Reisverzekering Wereld', 'travel',
     'Wereldwijde reisverzekering voor vakantie en zakenreizen',
     6.50, 50000, 50,
     '{"region_factor": {"europe": 1.0, "world": 1.5}, "winter_sports_addon": 3.00, "annual": true}',
     'active', '2024-01-01');

-- Allianz products
INSERT INTO products (insurer_id, product_code, name, product_type, description, base_premium, coverage_amount, deductible, rules_json, status, effective_date)
VALUES
    (3, 'ALZ-LIAB-001', 'Aansprakelijkheidsverzekering Particulier', 'liability',
     'Bescherming tegen schade die u per ongeluk aan anderen veroorzaakt',
     4.95, 1250000, 0,
     '{"family_size_factor": {"single": 1.0, "couple": 1.3, "family": 1.5}, "pets_addon": 1.50}',
     'active', '2024-01-01'),

    (3, 'ALZ-PROP-001', 'Opstalverzekering Comfort', 'property',
     'Complete verzekering voor uw woning en bijgebouwen',
     38.90, 400000, 200,
     '{"construction_type": {"brick": 1.0, "wood": 1.4, "concrete": 0.95}, "solar_panels_addon": 5.00, "garden_structure_addon": 3.50}',
     'active', '2024-01-01'),

    (3, 'ALZ-AUTO-001', 'Motorverzekering WA+', 'auto',
     'WA-verzekering met beperkt casco dekking',
     55.00, 2500000, 300,
     '{"age_driver_factor": {"18-24": 1.9, "25-34": 1.15, "35-54": 1.0, "55+": 1.05}, "claim_free_years": {"0": 1.6, "1-3": 1.2, "4-7": 1.0, "8+": 0.70}}',
     'active', '2024-01-01');

-- ASR products
INSERT INTO products (insurer_id, product_code, name, product_type, description, base_premium, coverage_amount, deductible, rules_json, status, effective_date)
VALUES
    (4, 'ASR-WOZ-001', 'Woonverzekering All-in-One', 'property',
     'Gecombineerde woonhuis- en inboedelverzekering',
     52.00, 600000, 200,
     '{"combined_discount": 0.90, "smart_home_discount": 0.95, "alarm_discount": 0.92}',
     'active', '2024-01-01'),

    (4, 'ASR-HEALTH-001', 'Zorgverzekering Compleet', 'health',
     'Basiszorg aangevuld met uitgebreide aanvullende dekking',
     165.00, 0, 385,
     '{"mandatory_base": 128.50, "dental_full": true, "physio_sessions": 18, "alternative_medicine": true}',
     'active', '2024-01-01'),

    (4, 'ASR-REIS-001', 'Doorlopende Reisverzekering', 'travel',
     'Doorlopende reisverzekering voor het hele gezin',
     9.75, 75000, 75,
     '{"family_coverage": true, "luggage_cover": 3000, "medical_repatriation": true, "cancel_coverage": true}',
     'active', '2024-03-01'),

    (4, 'ASR-LIAB-001', 'AVP Gezinspolis', 'liability',
     'Aansprakelijkheidsverzekering voor het hele gezin',
     5.50, 2500000, 0,
     '{"family_size_factor": {"single": 0.7, "couple": 1.0, "family": 1.0}, "home_office_addon": 2.00}',
     'active', '2024-01-01');

-- NN Group products
INSERT INTO products (insurer_id, product_code, name, product_type, description, base_premium, coverage_amount, deductible, rules_json, status, effective_date)
VALUES
    (5, 'NNG-LIFE-001', 'Overlijdensrisicoverzekering Flex', 'life',
     'Flexibele ORV met dalende of gelijkblijvende dekking',
     22.00, 200000, 0,
     '{"coverage_type": ["level", "decreasing"], "age_factor": {"18-30": 0.75, "31-45": 1.0, "46-60": 1.6, "61-75": 2.8}, "mortgage_linked": true}',
     'active', '2024-01-01'),

    (5, 'NNG-PENSIOEN-001', 'Pensioenplan Individueel', 'life',
     'Individueel pensioenspaarplan met fiscaal voordeel',
     150.00, 500000, 0,
     '{"tax_benefit": true, "retirement_age": [60, 62, 65, 67], "investment_profiles": ["defensive", "neutral", "offensive"]}',
     'active', '2024-01-01');

-- Nationale-Nederlanden products
INSERT INTO products (insurer_id, product_code, name, product_type, description, base_premium, coverage_amount, deductible, rules_json, status, effective_date)
VALUES
    (6, 'NAT-AUTO-001', 'Auto Compleet Verzekering', 'auto',
     'Uitgebreide autoverzekering met pechhulp en vervangend vervoer',
     72.00, 2500000, 250,
     '{"roadside_assistance": true, "replacement_vehicle": true, "new_for_old": {"max_age_years": 3}, "claim_free_years": {"0": 1.5, "1-3": 1.15, "4-7": 1.0, "8+": 0.65}}',
     'active', '2024-01-01'),

    (6, 'NAT-WOZ-001', 'Woonpakket Basis', 'property',
     'Basispakket voor opstal en inboedel met flexibele dekking',
     32.00, 300000, 175,
     '{"package_discount": 0.92, "flood_zone_surcharge": {"low": 1.0, "medium": 1.15, "high": 1.35}}',
     'active', '2024-01-01'),

    (6, 'NAT-HEALTH-001', 'Zorgverzekering Direct', 'health',
     'Basiszorgverzekering met snelle declaratieverwerking',
     131.00, 0, 385,
     '{"mandatory": true, "online_discount": 0.98, "dental_basic": 5.50, "physio_basic": 9.00}',
     'active', '2024-01-01');

-- ============================================================
-- POLICIES (sample customer data - fictional)
-- ============================================================
INSERT INTO policies (product_id, policy_number, customer_name, customer_email, customer_phone, date_of_birth, address, postcode, start_date, end_date, premium_amount, payment_freq, status)
VALUES
    -- Achmea policies
    (1, 'POL-2024-00001', 'Jan de Vries', 'j.devries@email.nl', '06-12345678', '1985-03-15', 'Keizersgracht 123', '1015 CJ', '2024-01-15', '2025-01-15', 28.05, 'monthly', 'active'),
    (2, 'POL-2024-00002', 'Marie van der Berg', 'm.vdberg@email.nl', '06-23456789', '1978-07-22', 'Prinsengracht 456', '1017 KL', '2024-02-01', '2025-02-01', 47.03, 'monthly', 'active'),
    (4, 'POL-2024-00003', 'Pieter Jansen', 'p.jansen@email.nl', '06-34567890', '1992-11-08', 'Damrak 78', '1012 LN', '2024-01-01', '2025-01-01', 42.00, 'monthly', 'active'),
    (5, 'POL-2024-00004', 'Sanne Bakker', 's.bakker@email.nl', '06-45678901', '1990-05-30', 'Herengracht 234', '1016 BT', '2024-03-01', '2025-03-01', 102.00, 'monthly', 'active'),
    (3, 'POL-2024-00005', 'Willem Smit', 'w.smit@email.nl', '06-56789012', '1995-09-12', 'Singel 567', '1012 VK', '2024-01-15', '2025-01-15', 13.43, 'monthly', 'active'),

    -- Aegon policies
    (6, 'POL-2024-00006', 'Anna de Jong', 'a.dejong@email.nl', '06-67890123', '1982-01-25', 'Coolsingel 89', '3012 AE', '2024-02-15', '2044-02-15', 18.90, 'monthly', 'active'),
    (8, 'POL-2024-00007', 'Kees Visser', 'k.visser@email.nl', '06-78901234', '1975-08-14', 'Lijnbaan 45', '3012 EL', '2024-01-01', '2025-01-01', 128.50, 'monthly', 'active'),
    (9, 'POL-2024-00008', 'Lisa Mulder', 'l.mulder@email.nl', '06-89012345', '1988-12-03', 'Stadhuisplein 12', '3012 AR', '2024-04-01', '2025-04-01', 6.50, 'monthly', 'active'),

    -- Allianz policies
    (10, 'POL-2024-00009', 'Thomas Bos', 't.bos@email.nl', '06-90123456', '1993-04-18', 'Museumplein 7', '1071 DJ', '2024-01-01', '2025-01-01', 7.43, 'monthly', 'active'),
    (11, 'POL-2024-00010', 'Sophie Dekker', 's.dekker@email.nl', '06-01234567', '1970-06-09', 'Vondelstraat 33', '1054 GE', '2024-02-01', '2025-02-01', 42.68, 'monthly', 'active'),
    (12, 'POL-2024-00011', 'Lucas Hendriks', 'l.hendriks@email.nl', '06-11223344', '1987-02-28', 'Apollolaan 99', '1077 AV', '2024-03-15', '2025-03-15', 55.00, 'monthly', 'active'),

    -- ASR policies
    (13, 'POL-2024-00012', 'Eva Willems', 'e.willems@email.nl', '06-22334455', '1991-10-20', 'Maliebaan 55', '3581 CD', '2024-01-01', '2025-01-01', 46.80, 'monthly', 'active'),
    (14, 'POL-2024-00013', 'Daan van Dijk', 'd.vandijk@email.nl', '06-33445566', '1965-03-07', 'Oudegracht 123', '3511 AE', '2024-02-01', '2025-02-01', 165.00, 'monthly', 'active'),
    (15, 'POL-2024-00014', 'Iris Peters', 'i.peters@email.nl', '06-44556677', '1998-08-11', 'Vredenburg 40', '3511 BD', '2024-05-01', '2025-05-01', 14.63, 'monthly', 'active'),

    -- NN Group policies
    (17, 'POL-2024-00015', 'Bram van Leeuwen', 'b.vleeuwen@email.nl', '06-55667788', '1980-12-01', 'Spui 70', '2511 BT', '2024-01-01', '2054-01-01', 26.40, 'monthly', 'active'),
    (18, 'POL-2024-00016', 'Rosa Meijer', 'r.meijer@email.nl', '06-66778899', '1972-05-16', 'Lange Voorhout 8', '2514 ED', '2024-03-01', '2054-03-01', 150.00, 'monthly', 'active'),

    -- Nationale-Nederlanden policies
    (19, 'POL-2024-00017', 'Thijs de Graaf', 't.degraaf@email.nl', '06-77889900', '1986-09-25', 'Blaak 16', '3011 TA', '2024-01-15', '2025-01-15', 46.80, 'monthly', 'active'),
    (20, 'POL-2024-00018', 'Fleur Kok', 'f.kok@email.nl', '06-88990011', '1994-01-30', 'Witte de Withstraat 55', '3012 BN', '2024-02-01', '2025-02-01', 29.44, 'monthly', 'active'),
    (21, 'POL-2024-00019', 'Sem van der Linden', 's.vdlinden@email.nl', '06-99001122', '1983-07-19', 'Meent 100', '3011 JR', '2024-04-01', '2025-04-01', 131.00, 'monthly', 'active'),

    -- Some expired/cancelled for variety
    (1, 'POL-2023-00001', 'Karel Brouwer', 'k.brouwer@email.nl', '06-10203040', '1960-11-05', 'Reguliersgracht 12', '1017 LR', '2023-01-01', '2024-01-01', 30.15, 'monthly', 'expired'),
    (6, 'POL-2023-00002', 'Nina van Houten', 'n.vhouten@email.nl', '06-20304050', '1989-04-14', 'Weesperstraat 88', '1018 DN', '2023-06-01', '2024-06-01', 15.75, 'yearly', 'cancelled');

-- ============================================================
-- CLAIMS
-- ============================================================
INSERT INTO claims (policy_id, claim_number, claim_date, reported_date, amount, approved_amount, status, category, description, assessor_notes)
VALUES
    (1, 'CLM-2024-00001', '2024-03-10', '2024-03-11', 4500.00, 4250.00, 'paid', 'storm_damage',
     'Dakschade door storm Pia, meerdere dakpannen verplaatst en gootafvoer beschadigd',
     'Schade bevestigd door onafhankelijke taxateur. Eigen risico van 250 euro afgetrokken.'),

    (2, 'CLM-2024-00002', '2024-04-05', '2024-04-05', 12000.00, NULL, 'under_review', 'water_damage',
     'Waterschade door gesprongen leiding in badkamer, vloer en muren beschadigd',
     'Loodgieter rapport ontvangen. Wachten op taxatierapport.'),

    (3, 'CLM-2024-00003', '2024-02-20', '2024-02-21', 2800.00, 2800.00, 'paid', 'accident',
     'Aanrijding op kruising, schade aan linkervoor bumper en koplamp',
     'Politierapport aanwezig. Tegenpartij aansprakelijk gesteld.'),

    (4, 'CLM-2024-00004', '2024-05-15', '2024-05-16', 45000.00, NULL, 'submitted', 'theft',
     'Volledig voertuig gestolen uit parkeergarage, camerabewaking beschikbaar',
     NULL),

    (9, 'CLM-2024-00005', '2024-03-01', '2024-03-02', 850.00, 850.00, 'paid', 'liability',
     'Per ongeluk vaas van buurman gebroken tijdens verhuizing',
     'Factuur van antieke vaas ontvangen en goedgekeurd.'),

    (10, 'CLM-2024-00006', '2024-04-20', '2024-04-22', 8500.00, 7200.00, 'approved', 'fire',
     'Keukenbrand door kortsluiting in vaatwasser, keukenkasten beschadigd',
     'Brandweerrapport beschikbaar. Gedeeltelijke vervanging nodig.'),

    (12, 'CLM-2024-00007', '2024-05-01', '2024-05-02', 3200.00, NULL, 'under_review', 'theft',
     'Inbraak in auto, laptop en navigatiesysteem gestolen',
     'Aangifte bij politie gedaan. Wachten op bevestiging verzekeringstakst.'),

    (13, 'CLM-2024-00008', '2024-02-14', '2024-02-15', 1500.00, 1300.00, 'paid', 'water_damage',
     'Lekkage wasmachine heeft laminaatvloer beschadigd',
     'Eigen risico 200 euro afgetrokken. Reparatie goedgekeurd.'),

    (17, 'CLM-2024-00009', '2024-06-01', '2024-06-02', 950.00, NULL, 'submitted', 'accident',
     'Fietser aangereden bij rechts afslaan, medische kosten en fietsreparatie',
     NULL),

    (19, 'CLM-2024-00010', '2024-04-10', '2024-04-11', 5600.00, 5350.00, 'paid', 'storm_damage',
     'Stormschade aan dak en schoorsteen, noodreparatie uitgevoerd',
     'Noodreparatie vergoed. Definitieve reparatie gepland. Eigen risico 250 euro.'),

    (7, 'CLM-2024-00011', '2024-03-25', '2024-03-26', 320.00, 320.00, 'paid', 'medical',
     'Spoedbezoek tandarts in het buitenland tijdens vakantie',
     'Vergoed onder basisverzekering buitenlandclausule.'),

    (14, 'CLM-2024-00012', '2024-05-20', '2024-05-21', 750.00, 0, 'rejected', 'medical',
     'Alternatieve behandeling (acupunctuur) niet vergoed onder basispakket',
     'Behandeling valt niet onder basisverzekering. Klant geadviseerd aanvullende verzekering af te sluiten.');

-- ============================================================
-- SYNC LOGS
-- ============================================================
INSERT INTO sync_logs (insurer_id, sync_time, sync_type, status, records_processed, records_created, records_updated, records_failed, errors, duration_ms)
VALUES
    (1, NOW() - INTERVAL '2 hours', 'full', 'success', 5, 0, 2, 0, NULL, 1250),
    (1, NOW() - INTERVAL '26 hours', 'full', 'success', 5, 1, 1, 0, NULL, 1100),
    (2, NOW() - INTERVAL '4 hours', 'full', 'success', 4, 0, 0, 0, NULL, 2100),
    (2, NOW() - INTERVAL '28 hours', 'full', 'success', 4, 0, 1, 0, NULL, 1950),
    (3, NOW() - INTERVAL '1 hour', 'incremental', 'success', 3, 0, 1, 0, NULL, 850),
    (4, NOW() - INTERVAL '3 hours', 'full', 'success', 4, 0, 0, 0, NULL, 1400),
    (5, NOW() - INTERVAL '48 hours', 'full', 'failed', 0, 0, 0, 2, 'Connection timeout: API endpoint niet bereikbaar', 30000),
    (5, NOW() - INTERVAL '72 hours', 'full', 'success', 2, 2, 0, 0, NULL, 3200),
    (6, NOW() - INTERVAL '6 hours', 'full', 'success', 3, 0, 0, 0, NULL, 1050),
    (6, NOW() - INTERVAL '30 hours', 'full', 'partial', 3, 0, 1, 1, 'Validation error: product NAT-HEALTH-002 missing required field coverage_amount', 1800);
