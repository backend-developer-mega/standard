--Metodo para hallar el iva retenido o percibido
CREATE OR REPLACE FUNCTION iva(yo integer,entidad integer,doc integer, tipo integer)
RETURNS numeric AS
$BODY$
declare gcyo boolean;
declare gcent boolean;
declare ivaf numeric(12,2);
begin
/*verifico el tipo de operación y determino si procede o no*/
select granc into gcyo from res_partner where id = yo;
select granc into gcent from res_partner where id = entidad;
select (amount_untaxed*0.01) into ivaf from account_invoice where id = doc;
--si yo no soy granc, el proveedor si lo es y el tipo es 1

if gcyo is null then
gcyo = false;
end if;
if gcent is null then
gcent = false;
end if;
if (gcyo = false and gcent = true and tipo = 1) then
return ivaf;
end if;

if (gcyo = true and gcent = false and tipo = 2) then
return ivaf;
end if;

return 0.00;
end;
$BODY$
LANGUAGE plpgsql VOLATILE;

--Metodo para hallar las compras exentas segun su naturaleza: Internas o Importaciones
CREATE OR REPLACE FUNCTION exentas(yo integer,entidad integer,doc integer, tipo int)
RETURNS numeric AS
$BODY$
declare pais_yo text;
declare pais_ent text;
declare monto numeric(12,2);
begin
select rc.name into pais_yo from res_partner rp, res_country rc where rp.country_id = rc.id AND rp.id = yo;
select rc.name into pais_ent from res_partner rp, res_country rc where rp.country_id = rc.id AND rp.id = entidad;
monto = COALESCE((select sum(price_subtotal) from account_invoice_line ail where ail.invoice_id = doc and tipov = 'exento'),0);

--Si son iguales eso me quiere decir que se trata de una compra local
--Y si se cumple esa condicion y el tipo es 1, retorno el valor porque ando buscando las compras locales
if pais_yo = pais_ent and tipo = 1 then
	return monto;
end if;

--Si no son iguales eso me quiere decir que se trata de una importación, y si el tipo es 2 retorno el valor
if pais_yo != pais_ent and tipo = 2 then
	return monto;
end if;

return 0.00;
end;
$BODY$
LANGUAGE plpgsql VOLATILE;

--Metodo para hallar las compras gravadas segun su naturaleza: Internas, Importaciones o Credito Fiscal
CREATE OR REPLACE FUNCTION gravadas(yo integer,entidad integer,doc integer, tipo int)
RETURNS numeric AS
$BODY$
declare pais_yo text;
declare pais_ent text;
declare monto numeric(12,2);
begin
select rc.name into pais_yo from res_partner rp, res_country rc where rp.country_id = rc.id AND rp.id = yo;
select rc.name into pais_ent from res_partner rp, res_country rc where rp.country_id = rc.id AND rp.id = entidad;
monto = COALESCE((select sum(price_subtotal) from account_invoice_line ail where ail.invoice_id = doc and tipov = 'gravado'),0);

--Si son iguales eso me quiere decir que se trata de una compra local
--Y si se cumple esa condicion y el tipo es 1, retorno el valor porque ando buscando las compras locales
if pais_yo = pais_ent and tipo = 1 then
	return monto;
end if;

--Si no son iguales eso me quiere decir que se trata de una importación, y si el tipo es 2 retorno el valor
if pais_yo != pais_ent and tipo = 2 then
	return monto;
end if;

return 0.00;
end;
$BODY$
LANGUAGE plpgsql VOLATILE;

--Metodo para hallar las compras gravadas segun su naturaleza: Internas, Importaciones o Credito Fiscal
CREATE OR REPLACE FUNCTION imp_fiscal(doc integer)
RETURNS numeric AS
$BODY$
declare monto numeric(12,2);
declare iva numeric(12,2);
begin
monto = COALESCE((select sum(price_subtotal) from account_invoice_line ail where ail.invoice_id = doc and tipov = 'gravado'),0);
iva = monto*0.13;
return iva;
end;
$BODY$
LANGUAGE plpgsql VOLATILE;
--Actualizo la tabla de ir_model_data para permitir la modificacion de ciertos registros
update ir_model_data set noupdate=false where name = 'mail_template_data_notification_email_account_invoice';
update ir_model_data set noupdate=false where name = 'USD';
update ir_model_data set noupdate=false where name = 'account_payment_term_immediate';
update ir_model_data set noupdate=false where name = 'account_payment_term_15days';
update ir_model_data set noupdate=false where name = 'account_payment_term_net';