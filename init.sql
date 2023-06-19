CREATE SCHEMA info;
CREATE SCHEMA etl;


CREATE FUNCTION time_subtype_diff(x time, y time) RETURNS float8 AS
'SELECT EXTRACT(EPOCH FROM (x - y))' LANGUAGE sql STRICT IMMUTABLE;


CREATE TYPE timerange AS RANGE (
    subtype = time,
    subtype_diff = time_subtype_diff
);

CREATE TYPE commercial_network AS ENUM('Magnit', 'Pyaterka');

CREATE TABLE info.shops
(
    id text COLLATE pg_catalog."default" NOT NULL,
    network commercial_network NOT NULL,
    working_hours timerange NOT NULL,
    address text COLLATE pg_catalog."default" NOT NULL,
    "position" geometry NOT NULL,
    CONSTRAINT shops_pkey PRIMARY KEY (id)
);

CREATE TABLE etl.load_service_table
(
    item_name text NOT NULL,
    item_id text ,
    shop_id text NOT NULL,
    discount_start_date date NOT NULL,
    discount_end_date date NOT NULL,
    item_price integer NOT NULL,
    item_discount_price integer NOT NULL
);

ALTER TABLE etl.load_service_table SET UNLOGGED;


create table info.items(
	item_id bigint primary key,
	item_name text not null
);


create table info.prices(
	id bigint primary key,
	discount_effective_date timerange null,
    discount_price numeric null,
    price numeric not null
);

create table info.shop_x_item(
	shop_id text not null,
	item_id bigint not null,
	price_id text not null,
	CONSTRAINT fk_shop FOREIGN KEY(shop_id) REFERENCES info.shops(id),
	CONSTRAINT fk_item FOREIGN KEY(item_id) REFERENCES info.items(item_id)
);


CREATE SEQUENCE etl.item_rk_generator;

create user py_load_agent with nosuperuser encrypted password 'dummy_password';

GRANT CONNECT ON DATABASE cheap_shopping TO py_load_agent;
GRANT USAGE ON SCHEMA info TO py_load_agent;
GRANT USAGE ON SCHEMA etl TO py_load_agent;
GRANT select,insert ON ALL TABLES IN SCHEMA etl TO py_load_agent;
GRANT select,insert ON TABLE shops IN SCHEMA info TO py_load_agent;
GRANT select,insert ON TABLE shop_x_item IN SCHEMA info TO py_load_agent; 
GRANT select,insert,update ON TABLE prices IN SCHEMA info TO py_load_agent;




CREATE VIEW etl.get_unique_items AS 
select distinct item_name from etl.load_service_table;

create or replace procedure etl.get_items_rk()
language plpgsql
as $$
begin
  raise info 'START CREATING TABLE ITEMS_WITH_RK , SERVER TIME %', now();
  truncate table etl.items_with_rk;
  insert into etl.items_with_rk(item_name,item_id) 
   SELECT t.item_name,coalesce(t1.item_id,nextval('etl.item_rk_generator')) as item_id
   from etl.get_unique_items t
    left join info.items t1 on t.item_name = t1.item_name;
	raise info 'TABLE ITEMS_WITH_RK CREATED SUCCESEFULLY, SERVER TIME %', now();
end; $$

CREATE or replace VIEW etl.src_with_items_id AS 
SELECT distinct t.item_name, t1.item_id,t.shop_id,t.discount_start_date,t.discount_end_date,t.item_price,t.item_discount_price
  FROM etl.load_service_table t
  left join etl.items_with_rk t1 on t.item_name = t1.item_name


  create or replace procedure etl.load_from_src_to_target()
language plpgsql
as $$
declare 
 max_item_rk bigint;
 n bigint;
begin

  call etl.get_items_rk();

  max_item_rk := coalesce((select max(item_id) from info.items),0);
  raise info 'MAX ITEM_RK IN ITEMS IS % , ALL RK > % WILL BE ADDED TO ITEMS, SERVER TIME %',max_item_rk, max_item_rk ,now();
  raise info 'START INSERTING NEW ITEMS, SERVER TIME %', now();
    
   INSERT INTO info.items (item_name, item_id)
   SELECT item_name, item_id
   FROM etl.items_with_rk
   where item_id > max_item_rk;
   
  get diagnostics n = row_count;
  raise info 'NEW ITEMS ADDED , AMOUNT: %, SERVER TIME %',n ,now();
  
  raise info 'START INSERTING NEW ITEMS PRICES, SERVER TIME %', now();
  
  INSERT INTO info.prices (id,price ,discount_price,discount_effective_date)
   SELECT distinct shop_id || '_' || item_id ,item_price, item_discount_price,daterange(discount_start_date,discount_end_date,'[]')
   FROM etl.src_with_items_id
   where item_id > max_item_rk;
  
  get diagnostics n = row_count;
  raise info 'NEW ITEMS PRICES ADDED , AMOUNT: %, SERVER TIME %',n ,now();
  
  raise info 'UPDATE EXISTING PRICES, SERVER TIME %',now();
  update info.prices set price = t1.item_price , 
 discount_price = t1.item_discount_price , 
 discount_effective_date = daterange(t1.discount_start_date,t1.discount_end_date,'[]')
  FROM (SELECT b1.price_id,item_price, item_discount_price,discount_start_date,discount_end_date
      FROM  etl.src_with_items_id b 
	  join info.shop_x_item b1 using (item_id,shop_id)) AS t1
  WHERE info.prices.id = t1.price_id;
  
  get diagnostics n = row_count;
  raise info 'EXISTING PRICES UPDATED,AMOUNT: % ,SERVER TIME %',n,now();
  
  raise info 'INSERT NEW ROWS INTO SHOP_X_ITEM,SERVER TIME %',now();
  
  INSERT INTO info.shop_x_item (shop_id,item_id,price_id )
   SELECT shop_id,item_id,shop_id || '_' || item_id
   FROM etl.src_with_items_id
   where item_id > max_item_rk;  
  
  get diagnostics n = row_count;
  raise info 'NEW ROWS INTO SHOP_X_ITEM ADDED,AMOUNT: % ,SERVER TIME %',n,now();
  raise info 'DONE';
end; $$


create or replace function get_possible_goods(user_location geometry(Point,4326),search_raduis numeric,goods text)
returns table(shop_location text,
						 item text,
			             item_id bigint,
						  item_price decimal)
as $$   
 with nearest_shop as(
	   select s.id,s.address from info.shops s
      where st_distance(s.location::geography,user_location::geography) / 1000 < search_raduis
     and s.working_hours @> current_time::time
   )
   select s.address,item_name,i.item_id,coalesce(p.discount_price,p.price)
   from info.items i
   join info.shop_x_item x using(item_id)
   join nearest_shop s on x.shop_id = s.id
   join info.prices p on p.id = s.id || '_' || i.item_id
   where to_tsvector(item_name) @@ to_tsquery(goods);  
$$ LANGUAGE sql;