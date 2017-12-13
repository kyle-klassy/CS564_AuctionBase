-- description: Constraint 12

PRAGMA foreign_keys = ON;

drop trigger if exists trigger9;

create trigger trigger9
    before insert on Bids
    for each row when (Select i.Currently from Items i where NEW.ItemID = i.ItemID and i.Currently >= i.Buy_Price) 
    begin
        SELECT raise(rollback, ‘Trigger9_Failed’);
    end;
