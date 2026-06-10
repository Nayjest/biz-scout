"""Entry point: ``python -m biz_scout`` launches the Streamlit UI."""

from pathlib import Path

from streamlit.web import bootstrap as streamlit_bootstrap

from .bootstrap import bootstrap


def main() -> None:
    bootstrap()
    ui = Path(__file__).with_name("ui.py")
    streamlit_bootstrap.run(str(ui), is_hello=False, args=[], flag_options={})


if __name__ == "__main__":
    main()
