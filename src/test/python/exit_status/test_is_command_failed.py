from ipmi_temperature_control.smartctl import ExitStatus

def test_with_00000100_should_return_true():
    assert ExitStatus(int('00000100', 2)).is_command_failed() == True

def test_with_00100000_should_return_false():
    assert ExitStatus(int('00100000', 2)).is_command_failed() == False

def test_with_11111111_should_return_false():
    assert ExitStatus(int('11111111', 2)).is_command_failed() == True

def test_with_11111011_should_return_false():
    assert ExitStatus(int('11111011', 2)).is_command_failed() == False