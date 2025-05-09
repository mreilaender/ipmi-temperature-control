from ipmi_temperature_control.smartctl import ExitStatus

def test_with_00100000_should_return_true():
    assert ExitStatus(int('00100000', 2)).is_threshold_reached() == True

def test_with_00000100_should_return_false():
    assert ExitStatus(int('00000100', 2)).is_threshold_reached() == False

def test_with_11111111_should_return_false():
    assert ExitStatus(int('11111111', 2)).is_threshold_reached() == True

def test_with_11011111_should_return_false():
    assert ExitStatus(int('11011111', 2)).is_threshold_reached() == False