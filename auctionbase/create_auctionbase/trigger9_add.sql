-- description: Constraint 11

PRAGMA foreign_keys = ON;

drop trigger if exists trigger6;

create trigger trigger9
    before insert on Bids
    for each row when (NEW.Amount > (Select i.Buy_Price from Items i where NEW.ItemID = i.ItemID))
    begin
        SELECT raise(rollback, ‘Trigger9_Failed’);
    end;
