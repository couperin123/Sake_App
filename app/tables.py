from flask_table import Table, Col

class Results(Table):
    index = Col('index',show=False)
    Sake_name = Col('Sake_name(Meigara)')
    Sake_Product_Name = Col('Sake_Product_Name')
    Type = Col('Type')
    SMV = Col('SMV')
    Acidity = Col('Acidity')
    Amakara = Col('Amakara')
    Notan = Col('Notan')
    ABV = Col('ABV')
