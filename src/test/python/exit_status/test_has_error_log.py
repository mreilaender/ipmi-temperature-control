from ipmi_temperature_control.smartctl import ExitStatus

def test_with_00100000_should_return_true():
    assert ExitStatus(int('01000000', 2)).has_error_log() == True

def test_with_00000010_should_return_false():
    assert ExitStatus(int('00000010', 2)).has_error_log() == False

def test_with_11111111_should_return_false():
    assert ExitStatus(int('11111111', 2)).has_error_log() == True

def test_with_11011111_should_return_false():
    assert ExitStatus(int('10111111', 2)).has_error_log() == False