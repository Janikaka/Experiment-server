from experiment_server.models import (Configuration, ConfigurationKey, ExclusionConstraint, Operator, RangeConstraint)
import _operator

"""
Tools, helper-functions and validations which are used in multiple views
"""
# TODO: Return descriptive error messages on failure, so it can be passed from backend to frontend


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
    """
    Validates type that it can be used with given operator
    :param type: Type to be validated
    :param operator: Operator to be used with given type
    :return: is type valid with given operator
    """
    if operator is None:
        # Some tests get broken, since operator is not always set in them.
        return True
    if type == "boolean" or type == "string":
        return operator.id == 1 or operator.id == 6 or operator.id == 9 or operator.id == 10

    return type == "integer" or type == "float"

def is_valid_type_value(type, value):
    """
    Validates value's type to be equal with given type
    :param type: Desired type
    :param value: Value to be validated. Can be None since ExclusionConstraint can hold None values
    :return: Is value Valid to given Type
    """
    if value is None:
        return True

    try:
        if type == "boolean":
            bool(value)
            if (isinstance(value, str) or value > 1 or value < 0):
                raise ValueError("If integer is something else besides 0 or 1,",
                                 " it will not be considered as boolean in this case.")
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
    """
    Validates multiple values' type and operators.
    :param type: Desired Type
    :param operator: Desired Operator
    :param values: Value to be validated
    :return: Are given values Valid
    """
    if operator is not None and (operator.id == 7 or operator.id == 8) and (len(values) < 2 or values[1] is None):
        return False

    for value in values:
        if not is_valid_type_value(type, value):
            return False

    return True


def get_value_as_correct_type(value, type):
    if value is None:
        return None
    if type == "string":
        return str(value)
    elif type == "integer":
        return int(value)
    elif type == "float":
        return float(value)
    elif type == "boolean":
        return bool(value)

def evaluate_value_operator(operator, given_value, value1, value2):
    """
    Validates given_value by comparing it with operator to value1 and value 2. If operator with id less than 6 is given,
     only value1 is needed. Expects values to be in correct type.
    :param operator:
    :param given_value:
    :param value1:
    :param value2:
    :return:
    """
    ops = {'=': _operator.eq,
           '<=': _operator.le,
           '<': _operator.lt,
           '>=': _operator.ge,
           '>': _operator.gt,
           '!=': _operator.ne,
           }

    if operator.math_value == '[]' or operator.math_value == '()':
        if value1 is None or value2 is None:
            return False
        if operator.math_value == '[]':
            return value1 <= given_value <= value2
        elif operator.math_value == '()':
            return value1 < given_value < value2
    elif operator.math_value == 'def':
        return given_value is not None
    elif operator.math_value == 'ndef':
        return given_value is None
    elif operator.math_value is not None:
        return ops[operator.math_value](given_value, value1)

    return False


def is_in_range(configkey, value):
    """
    Checks RangeConstraints on given value. Assumes that Application- and ConfigurationKey-connection is already
    checked.
    :param configkey: Given ConfigurationKey
    :param value: Value to validate
    :return: Is given value approved by RangeConstraints
    """
    rangeconstraints = RangeConstraint.query().join(ConfigurationKey).filter(ConfigurationKey.id == configkey.id)

    for rc in rangeconstraints:
        if not evaluate_value_operator(Operator.get(rc.operator_id), get_value_as_correct_type(value, configkey.type),
                                       get_value_as_correct_type(rc.value, configkey.type), None):
            return False

    return True


def evaluate_exclusion(exclusion, ckey_a, ckey_b, config_a, config_b):
    """
    Helper function for @is_valid_exclusion
    :param exclusion: ExclusionConstraint to check
    :param ckey_a: first ConfigurationKey
    :param ckey_b: Second ConfigurationKey
    :param config_a: First Configuration
    :param config_b: Second Configuration
    :return: is ExclusionConstraint fulfilled
    """
    if config_a is None or config_b is None:
        return True  # Either of values is not set. Nothing to validate

    op_a = Operator.get(exclusion.first_operator_id)
    type_a = ckey_a.type
    value_a = get_value_as_correct_type(config_a.value, type_a)
    argument_a = evaluate_value_operator(op_a, value_a, exclusion.first_value_a, exclusion.first_value_b)

    op_b = Operator.get(exclusion.second_operator_id)
    type_b = ckey_b.type
    value_b = get_value_as_correct_type(config_b.value, type_b)
    argument_b = evaluate_value_operator(op_b, value_b, exclusion.second_value_a, exclusion.second_value_b)

    if not (not argument_a or argument_b):
        return False  # ExclusionConstraint is violated


def is_valid_exclusion(configkey, configuration):
    """
    Checks ExclusionConstraints on given value. It checks logical argument "not A or B", where given configuration is in
    B. This means that if A is defined and true, B can not be false. Given Configuration is validated in places of A and
    B.
    :param configkey: ConfigurationKey which is checked if it is as second or first ConfigurationKey in any
    ExclusionConstraint
    :param configuration: Configuration which is being validated
    :return: is given configuration allowed by exclusion constraints.
    """
    exclusions_conf_as_a = ExclusionConstraint.query() \
        .join(ConfigurationKey, ConfigurationKey.id == ExclusionConstraint.first_configurationkey_id) \
        .filter(ConfigurationKey.id == configkey.id).all()
    exclusions_conf_as_b = ExclusionConstraint.query()\
        .join(ConfigurationKey, ConfigurationKey.id == ExclusionConstraint.second_configurationkey_id)\
        .filter(ConfigurationKey.id == configkey.id).all()

    for exc in exclusions_conf_as_a:
        ck_b = ConfigurationKey.get(exc.second_configurationkey_id)

        config_b = Configuration().query().filter(Configuration.experimentgroup_id == configuration.experimentgroup_id,
                                                  Configuration.key == ck_b.name).one_or_none()

        if not evaluate_exclusion(exc, configkey, ck_b, configuration, config_b):
            return False

    for exc in exclusions_conf_as_b:
        ck_a = ConfigurationKey.get(exc.first_configurationkey_id)

        config_a = Configuration().query().filter(Configuration.experimentgroup_id == configuration.experimentgroup_id,
                                                 Configuration.key == ck_a.name).one_or_none()

        if not evaluate_exclusion(exc, ck_a, configkey, config_a, configuration):
            return False

    return True  # No ExclusionConstraints set or configuration is valid on all ExclusionConstraints

