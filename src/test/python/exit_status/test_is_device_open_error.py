from ipmi_temperature_control.smartctl import ExitStatus

def test_with_00001010_should_return_true():
    assert ExitStatus(int('00001010', 2)).is_device_open_error() == True

def test_with_00000000_should_return_false():
    assert ExitStatus(int('0000', 2)).is_device_open_error() == False

def test_with_00000001_should_return_false():
    assert ExitStatus(int('0001', 2)).is_device_open_error() == False

def test_with_00001111_should_return_true():
    assert ExitStatus(int('00001111', 2)).is_device_open_error() == True

def test_with_01000000_should_return_false():
    assert ExitStatus(int('01000000', 2)).is_device_open_error() == False

def test_with_00000010_should_return_true():
    assert ExitStatus(int('00000010', 2)).is_device_open_error() == True

