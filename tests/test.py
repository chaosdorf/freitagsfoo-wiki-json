from pathlib import Path
from nose.tools import eq_
import json
import freitagsfoo


class FakePage:
    def __init__(self: "FakePage", text: str) -> None:
        self.wikitext = text
    
    def text(self: "FakePage", section: int = 0) -> str:
        # TODO: section??
        return self.wikitext


def for_file(wikitext_file: Path) -> None:
    json_file = wikitext_file.with_suffix(".json")
    expected_data = json.loads(json_file.read_text())
    fake_page = FakePage(wikitext_file.read_text())
    eq_(freitagsfoo.parse_page(fake_page, None), expected_data)


def test_files():
    p = Path(__file__).absolute().parent  # the tests folder
    for file in p.iterdir():
        if file.suffix == ".wikitext":
            assert file.with_suffix(".json").exists()
            yield for_file, file
