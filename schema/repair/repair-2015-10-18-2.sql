BEGIN;
UPDATE location SET hood='lower pac hts' WHERE lower(hood)='lower pac heights';
UPDATE location SET hood='lower pac hts' WHERE lower(hood)='lower pacific heights';
UPDATE location SET hood='lower pac hts' WHERE lower(hood)='lower pac height';

UPDATE location SET hood='lower pac hts' WHERE lower(hood)='lower pac heights ';
UPDATE location SET hood='lower pac hts' WHERE lower(hood)='lower pacific heights ';

-- delete Treasure Island
UPDATE location SET hood_id = NULL WHERE hood_id = 58;
DELETE FROM neighborhood WHERE id = 58;

-- delete Sunset District
UPDATE location SET hood_id = NULL WHERE hood_id = 60;
DELETE FROM neighborhood WHERE id = 60;

-- add new hood Duboce Triangle
INSERT INTO neighborhood (id, name) VALUES
    (nextval('hood_seq'), 'duboce triangle' )
;
UPDATE location SET hood=hood WHERE lower(hood)='duboce triangle';

COMMIT;