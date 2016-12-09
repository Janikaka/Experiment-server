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

def is_valid_type_operator(type, operator_id):
    if type == "boolean" or type == "string":
        return operator_id == 1 or operator_id == 6 or operator_id == 9 or operator_id == 10

    return type == "integer" or type == "float"

def is_valid_type_value(type, value):
    if value is None:
        return True

    if type == "boolean":
        return isinstance(bool(value), bool)
    elif type == "string":
        return isinstance(value, str)
    elif type == "integer":
        return isinstance(int(value), int)
    elif type == "float":
        return isinstance(float(value), float)
    return False

def is_valid_type_values(type, operator_id, values):
    if (operator_id == 7 or operator_id == 8) and (len(values) < 2 or values[1] is None):
        return False

    for value in values:
        if not is_valid_type_value(type, value):
            return False

    return True

