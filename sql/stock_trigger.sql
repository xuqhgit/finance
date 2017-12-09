/*
stock new trigger
*/
drop trigger stock_new_temp_trigger;
DELIMITER $$
create trigger stock_new_temp_trigger
	after insert on stock_new_temp
	for each row 
	BEGIN 
	declare v_1 int(2);
	declare v_2 int(2);
	set v_1=0;
	set v_2=0;
	select count(*) into v_1 from stock_new where code = new.code;
	IF v_1=0 THEN
		insert into stock_new select * from stock_new_temp where code = new.code;
		insert into stock(code,name,type,create_time) values(new.code,new.name,new.type,now());
	ELSEIF v_1=1 THEN
		select count(*) into v_2 from stock_new where code = new.code and high_count<new.high_count;
		IF v_2=1 THEN
			update stock_new set public_pe=new.public_pe,public_date=new.public_date,
				income=new.income,high_count=new.high_count,update_time=now() where code=new.code;
		END IF;
	END IF;
END$$

-- /*
-- stock block trigger
--  */
--  DROP  trigger stock_plate_temp_trigger;
--  DELIMITER $$
--  create trigger stock_plate_temp_trigger
--   after insert on stock_plate_temp
--   for each row
--   BEGIN
--   DECLARE v_1 int(2);
--   set v_1=0;
--   select count(*) into v_1 from stock_plate where sc
