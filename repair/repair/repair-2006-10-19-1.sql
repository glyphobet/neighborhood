BEGIN;

UPDATE location set hood_id=22 where lower(hood)='bernal heights'    ;
UPDATE location set hood_id=19 where lower(hood)='financial district';
UPDATE location set hood_id=26 where lower(hood)='glen park'         ;  
UPDATE location set hood_id=24 where lower(hood)='hayes valley'      ;
UPDATE location set hood_id=4  where lower(hood)='inner richmond'    ;
UPDATE location set hood_id=15 where lower(hood)='lower haight'      ;
UPDATE location set hood_id=29 where lower(hood)='lower nob hill'    ;
UPDATE location set hood_id=1  where lower(hood)='mission district'  ;
UPDATE location set hood_id=14 where lower(hood)='nob hill'          ;
UPDATE location set hood_id=6  where lower(hood)='noe valley'        ;
UPDATE location set hood_id=3  where lower(hood)='pacific heights'   ;
UPDATE location set hood_id=25 where lower(hood)='potrero hill'      ;
UPDATE location set hood_id=13 where lower(hood)='russian hill'      ;

DROP TRIGGER update_hood_id_trigger ON location;

DELETE FROM neighborhood WHERE id = 61;
DELETE FROM neighborhood WHERE id = 62;

UPDATE location SET hood_id = NULL WHERE hood_id = 61;
UPDATE location SET hood_id = NULL WHERE hood_id = 62;

CREATE TRIGGER update_hood_id_trigger
    BEFORE UPDATE ON "location"
    FOR EACH ROW
    EXECUTE PROCEDURE set_hood_id();
