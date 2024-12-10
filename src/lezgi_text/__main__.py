import argparse
from pathlib import Path

from tqdm.auto import tqdm

from lezgi_text.parsers import (
    parse_lezgi_gazet,
    parse_tsiyi_dunya,
    parse_erenlardin_ses,
    parse_dagdin_bulah,
    parse_samurdin_ses,
    parse_cure_habar,
    parse_lit_dag,
    parse_alam
)
from lezgi_text.scrapers import (
    scrap_lezgi_gazet,
    scrap_tsiyi_dunya,
    scrap_erenlardin_ses,
    scrap_dagdin_bulah,
    scrap_samurdin_ses,
    scrap_cure_habar,
    scrap_lit_dag,
    scrap_alam
)


def main():
    source = {
        "lezgi_gazet": {
            "scrap_func": scrap_lezgi_gazet,
            "parse_func": parse_lezgi_gazet,
        },
        "tsiyi_dunya": {
            "scrap_func": scrap_tsiyi_dunya,
            "parse_func": parse_tsiyi_dunya,
        },
        "erenlardin_ses": {
            "scrap_func": scrap_erenlardin_ses,
            "parse_func": parse_erenlardin_ses,
        },
        "dagdin_bulah": {
            "scrap_func": scrap_dagdin_bulah,
            "parse_func": parse_dagdin_bulah,
        },
        "samurdin_ses": {
            "scrap_func": scrap_samurdin_ses,
            "parse_func": parse_samurdin_ses,
        },
        "cure_habar": {
            "scrap_func": scrap_cure_habar,
            "parse_func": parse_cure_habar,
        },
        "lit_dag": {
            "scrap_func": scrap_lit_dag,
            "parse_func": parse_lit_dag,
        },
        "alam": {
            "scrap_func": scrap_alam,
            "parse_func": parse_alam,
        },
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["scrap", "parse"])
    parser.add_argument("source_name", choices=source.keys())
    parser.add_argument("-o", "--output_dir")
    parser.add_argument("-i", "--input_dir")
    args = parser.parse_args()
    
    if args.command == "scrap":
        source[args.source_name]["scrap_func"](args.output_dir)
    elif args.command == "parse":
        if not args.input_dir:
            args.input_dir = f"{args.source_name}_pdf"

        output = list()
        for pdf_path in tqdm(sorted(Path(args.input_dir).glob("*.pdf"))):
            accepted, rejected, rejection_reason = source[args.source_name]["parse_func"](pdf_path)
            output.extend(accepted)

        Path(f"./{args.source_name}.txt").write_text('\n'.join(output))


if __name__ == "__main__":
    main()