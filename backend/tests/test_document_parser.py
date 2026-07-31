from pathlib import Path

import pytest

from app.services.document_parser import extract_text


FIXTURES = Path(__file__).parent / "fixtures"


def test_extract_docx():
    data = (FIXTURES / "体检报告样例.docx").read_bytes()
    text = extract_text("体检报告样例.docx", data)
    assert "空腹血糖：7.2 mmol/L" in text
    assert "血压 138/88" in text
    assert "总胆固醇：5.8" in text
    assert "项目" in text  # 表格内容也能提取
    assert "参考范围" in text


def test_extract_pdf():
    data = (FIXTURES / "体检报告样例.pdf").read_bytes()
    text = extract_text("体检报告样例.pdf", data)
    assert "空腹血糖：6.8 mmol/L" in text
    assert "血压 145/92" in text


def test_unsupported_extension():
    with pytest.raises(ValueError):
        extract_text("报告.txt", b"hello")


def test_empty_file():
    with pytest.raises(ValueError):
        extract_text("报告.pdf", b"")


def test_oversize_file():
    with pytest.raises(ValueError):
        extract_text("报告.pdf", b"x" * (10 * 1024 * 1024 + 1))
