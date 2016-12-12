from experiment_server.models.operators import Operator

def get_valid_types():
    return ["boolean", "string", "integer", "float"]

def get_operators():
    if Operator.query().count == 0:
        op1 = Operator(id=1, math_value='=', human_value='equals')
        op2 = Operator(id=2, math_value='<=', human_value='less or equal than')
        op3 = Operator(id=3, math_value='<', human_value='less than')
        op4 = Operator(id=4, math_value='>=', human_value='greater or equal than')
        op5 = Operator(id=5, math_value='>', human_value='greater than')
        op6 = Operator(id=6, math_value='!=', human_value='not equal')
        op7 = Operator(id=7, math_value='[]', human_value='inclusive')
        op8 = Operator(id=8, math_value='()', human_value='exclusive')
        op9 = Operator(id=9, math_value='def', human_value='must define')
        op10 = Operator(id=10, math_value='ndef', human_value='must not define')

        Operator.save(op1)
        Operator.save(op2)
        Operator.save(op3)
        Operator.save(op4)
        Operator.save(op5)
        Operator.save(op6)
        Operator.save(op7)
        Operator.save(op8)
        Operator.save(op9)
        Operator.save(op10)

    return Operator.all()

def is_valid_type_operator(type, operator):
    if operator is None:
        return True
    if type == "boolean" or type == "string":
        return operator.id == 1 or operator.id == 6 or operator.id == 9 or operator.id == 10

    return type == "integer" or type == "float"

def is_valid_type_value(type, value):
    if value is None:
        return True

    try:
        if type == "boolean":
            bool(value)
        elif type == "string":
            str(value)
        elif type == "integer":
            int(value)
        elif type == "float":
            float(value)
    except ValueError as e:
        return False

    return True

def is_valid_type_values(type, operator, values):
    if operator is not None and (operator.id == 7 or operator.id == 8) and (len(values) < 2 or values[1] is None):
        return False

    for value in values:
        if not is_valid_type_value(type, value):
            return False

    return True

