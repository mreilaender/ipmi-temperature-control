from ipmi_temperature_control.smartctl import ExitStatus

def test_with_00000001_should_return_true():
    assert ExitStatus(int('00000001', 2)).is_cli_parse_error() == True

def test_with_10000000_should_return_false():
    assert ExitStatus(int('10000000', 2)).is_cli_parse_error() == False

def test_with_10000001_should_return_true():
    assert ExitStatus(int('10000001', 2)).is_cli_parse_error() == True

def test_with_11111110_should_return_false():
    assert ExitStatus(int('11111110', 2)).is_cli_parse_error() == False