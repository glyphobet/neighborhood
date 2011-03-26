-- repair neighborhoods for 2005-06-12
BEGIN;
DROP TRIGGER update_hood_id_trigger ON location;
DELETE FROM neighborhood WHERE id = 56;
DELETE FROM neighborhood WHERE id = 57;
DELETE FROM neighborhood WHERE id = 59;
UPDATE location SET hood_id = NULL WHERE hood_id = 20;
UPDATE location SET hood_id = NULL WHERE hood_id = 30;
UPDATE location SET hood_id = NULL WHERE hood_id = 36;
UPDATE location SET hood_id = NULL WHERE hood_id = 56;
UPDATE location SET hood_id = NULL WHERE hood_id = 57;
UPDATE location SET hood_id = NULL WHERE hood_id = 59;
SELECT count(hood_id), hood from location where hood_id is not null group by hood order by count desc;
COMMIT;