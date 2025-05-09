from ipmi_temperature_control.smartctl import ExitStatus

def test_with_00001000_should_return_true():
    assert ExitStatus(int('00001000', 2)).is_disk_failing() == True

def test_with_00010000_should_return_false():
    assert ExitStatus(int('00010000', 2)).is_disk_failing() == False

def test_with_11111111_should_return_false():
    assert ExitStatus(int('11111111', 2)).is_disk_failing() == True

def test_with_11110111_should_return_false():
    assert ExitStatus(int('11110111', 2)).is_disk_failing() == False