from ipmi_temperature_control.smartctl import ExitStatus

def test_with_10000000_should_return_true():
    assert ExitStatus(int('10000000', 2)).has_test_errors() == True

def test_with_00000001_should_return_false():
    assert ExitStatus(int('00000001', 2)).has_test_errors() == False

def test_with_11111111_should_return_false():
    assert ExitStatus(int('11111111', 2)).has_test_errors() == True

def test_with_01111111_should_return_false():
    assert ExitStatus(int('01111111', 2)).has_test_errors() == False