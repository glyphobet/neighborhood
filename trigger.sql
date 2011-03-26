DROP TRIGGER insert_hood_id_trigger ON location;
DROP TRIGGER update_hood_id_trigger ON location;

DROP FUNCTION set_hood_id ();

create function set_hood_id ()
  returns trigger as '
  DECLARE 
      hoods RECORD;
  DECLARE
      hoodavg RECORD;
  DECLARE
      hoodcount RECORD;
  BEGIN 
      SELECT INTO hoodavg avg(total)/10 AS total FROM
          (SELECT count(id) AS total FROM location WHERE hood_id IS NOT NULL GROUP BY hood_id) AS l1;

      SELECT INTO hoods id, name 
          from neighborhood
      WHERE
          (lower(name) = lower(new.hood)) OR (name IS NULL AND new.hood IS NULL);

      IF NOT FOUND THEN
	  SELECT INTO hoodcount COUNT(id) 
	      FROM location WHERE lower(hood) = lower(new.hood);
	  IF (hoodcount.count >= hoodavg.total) OR (hoodavg.total IS NULL) THEN
              INSERT INTO neighborhood (id, name) VALUES (nextval(''hood_seq''), new.hood);
              SELECT INTO hoods id, name 
                  from neighborhood
              WHERE
                  lower(name) = lower(new.hood);
	      UPDATE location SET hood_id = hoods.id WHERE lower(hood) = lower(hoods.name);
	  END IF;
      END IF;

      SELECT INTO hoods id, name 
          from neighborhood
      WHERE
          lower(name) = lower(new.hood);

      IF FOUND THEN
          new.hood_id := hoods.id;
      END IF;

      RETURN new;
  END;
' language 'plpgsql';


CREATE TRIGGER insert_hood_id_trigger BEFORE INSERT ON location 
	FOR EACH ROW EXECUTE PROCEDURE set_hood_id();

CREATE TRIGGER update_hood_id_trigger BEFORE UPDATE ON location 
	FOR EACH ROW EXECUTE PROCEDURE set_hood_id();
