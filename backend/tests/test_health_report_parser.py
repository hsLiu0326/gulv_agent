from app.services.health_report_parser import HealthReportParser


SAMPLE = (
    "空腹血糖：7.2 mmol/L\n"
    "血压 138/88 mmHg\n"
    "血尿酸：420 μmol/L\n"
    "总胆固醇：5.8 mmol/L\n"
    "甘油三酯：1.9 mmol/L"
)


def test_regex_parse():
    result = HealthReportParser()._regex_parse(SAMPLE)
    assert result["blood_glucose"] == 7.2
    assert result["blood_pressure_systolic"] == 138
    assert result["blood_pressure_diastolic"] == 88
    assert result["uric_acid"] == 420.0
    assert result["cholesterol"] == 5.8
    assert result["triglycerides"] == 1.9


def test_parse_without_ai(monkeypatch):
    parser = HealthReportParser()
    monkeypatch.setattr(parser, "_ai_parse", lambda content: None)
    result = parser.parse(SAMPLE)
    assert result["blood_glucose"] == 7.2
    assert result["parse_method"] == "regex"


def test_parse_missing_indicators():
    result = HealthReportParser()._regex_parse("今天天气不错")
    assert result["blood_glucose"] is None
    assert result["blood_pressure_systolic"] is None
    assert result["cholesterol"] is None
