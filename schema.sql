--
-- PostgreSQL database dump
--

SET client_encoding = 'UNICODE';
SET check_function_bodies = false;

SET SESSION AUTHORIZATION 'postgres';

SET search_path = public, pg_catalog;

--
-- TOC entry 13 (OID 4538702)
-- Name: plpgsql_call_handler(); Type: FUNC PROCEDURAL LANGUAGE; Schema: public; Owner: postgres
--

CREATE FUNCTION plpgsql_call_handler() RETURNS language_handler
    AS '$libdir/plpgsql', 'plpgsql_call_handler'
    LANGUAGE c;


SET SESSION AUTHORIZATION DEFAULT;

--
-- TOC entry 11 (OID 4538703)
-- Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: public; Owner: 
--

CREATE TRUSTED PROCEDURAL LANGUAGE plpgsql HANDLER plpgsql_call_handler;


SET SESSION AUTHORIZATION 'postgres';

--
-- TOC entry 4 (OID 2200)
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


SET SESSION AUTHORIZATION 'hood';

--
-- TOC entry 5 (OID 4550109)
-- Name: loc_seq; Type: SEQUENCE; Schema: public; Owner: hood
--

CREATE SEQUENCE loc_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 6 (OID 4550111)
-- Name: hood_seq; Type: SEQUENCE; Schema: public; Owner: hood
--

CREATE SEQUENCE hood_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 14 (OID 4550113)
-- Name: set_updated(); Type: FUNCTION; Schema: public; Owner: hood
--

CREATE FUNCTION set_updated() RETURNS "trigger"
    AS '
  begin
    if not new.updated = CURRENT_TIMESTAMP then
      new.updated        := CURRENT_TIMESTAMP;
    end if;

    return new;
  end;
'
    LANGUAGE plpgsql;


--
-- TOC entry 7 (OID 4550115)
-- Name: location; Type: TABLE; Schema: public; Owner: hood
--

CREATE TABLE "location" (
    id bigint NOT NULL,
    created timestamp with time zone DEFAULT ('now'::text)::timestamp(6) with time zone,
    updated timestamp with time zone DEFAULT ('now'::text)::timestamp(6) with time zone,
    url character varying(256),
    hood character varying(256),
    source integer,
    hood_id integer,
    loc character varying(256),
    lat double precision,
    long double precision
);


--
-- TOC entry 8 (OID 4550124)
-- Name: neighborhood; Type: TABLE; Schema: public; Owner: hood
--

CREATE TABLE neighborhood (
    id bigint NOT NULL,
    name character varying(256)
);


--
-- TOC entry 12 (OID 10307228)
-- Name: set_hood_id(); Type: FUNCTION; Schema: public; Owner: hood
--

CREATE FUNCTION set_hood_id() RETURNS "trigger"
    AS '
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
'
    LANGUAGE plpgsql;


--
-- TOC entry 9 (OID 4550122)
-- Name: location_pkey; Type: CONSTRAINT; Schema: public; Owner: hood
--

ALTER TABLE ONLY "location"
    ADD CONSTRAINT location_pkey PRIMARY KEY (id);


--
-- TOC entry 10 (OID 4550126)
-- Name: neighborhood_pkey; Type: CONSTRAINT; Schema: public; Owner: hood
--

ALTER TABLE ONLY neighborhood
    ADD CONSTRAINT neighborhood_pkey PRIMARY KEY (id);


--
-- TOC entry 16 (OID 4550128)
-- Name: set_updated_trigger; Type: TRIGGER; Schema: public; Owner: hood
--

CREATE TRIGGER set_updated_trigger
    BEFORE UPDATE ON "location"
    FOR EACH ROW
    EXECUTE PROCEDURE set_updated();


--
-- TOC entry 15 (OID 10307229)
-- Name: insert_hood_id_trigger; Type: TRIGGER; Schema: public; Owner: hood
--

CREATE TRIGGER insert_hood_id_trigger
    BEFORE INSERT ON "location"
    FOR EACH ROW
    EXECUTE PROCEDURE set_hood_id();


--
-- TOC entry 17 (OID 25641409)
-- Name: update_hood_id_trigger; Type: TRIGGER; Schema: public; Owner: hood
--

CREATE TRIGGER update_hood_id_trigger
    BEFORE UPDATE ON "location"
    FOR EACH ROW
    EXECUTE PROCEDURE set_hood_id();


SET SESSION AUTHORIZATION 'postgres';

--
-- TOC entry 3 (OID 2200)
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'Standard public schema';


