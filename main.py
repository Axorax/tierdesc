import re
import os
import sys
import csv
import yaml
import toml
import json
import textwrap
import pyperclip
from colorama import init, Fore, Style

init(autoreset=True)

def load_tiers(file_path):
    tiers = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            current_tier, tier_data = None, []
            for line in map(str.strip, f):
                if "$" in line:
                    if current_tier:
                        tiers[current_tier] = (tier_data, price)
                    current_tier, price = line.split()[0].lower(), re.search(r"\d[\d,]*(\.\d+)?\s*\$", line).group(0)
                    tier_data = []
                elif line:
                    tier_data.append(line)
            if current_tier:
                tiers[current_tier] = (tier_data, price)
    except FileNotFoundError:
        print(f"{Fore.RED}File '{file_path}' not found!{Style.RESET_ALL}")
        sys.exit(1)
    return tiers

def cascade(tiers):
    tier_keys = list(tiers.keys())
    for i in range(1, len(tier_keys)):
        higher_tier = tier_keys[i]
        lower_tier_benefits = tiers[tier_keys[i - 1]][0]
        tiers[higher_tier] = (
            lower_tier_benefits + tiers[higher_tier][0],
            tiers[higher_tier][1],
        )

def cascade_reverse(tiers):
    tier_keys = list(tiers.keys())
    for i in range(len(tier_keys) - 1, -1, -1):
        current_benefits = list(tiers[tier_keys[i]][0])
        for j in range(i - 1, -1, -1):
            current_benefits.extend(tiers[tier_keys[j]][0])
        tiers[tier_keys[i]] = (current_benefits, tiers[tier_keys[i]][1])

def tier_info(tiers, selected_tier, copy_to_clipboard, output_file):
    selected_tier = selected_tier.lower()
    tier_data = tiers.get(selected_tier)

    if not tier_data:
        print(f"{Fore.RED}Tier '{selected_tier}' not found!{Style.RESET_ALL}")
        return

    output = "\n".join(tier_data[0])

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"{Fore.GREEN}Output written to '{output_file}'.{Style.RESET_ALL}")
    else:
        print(output)

    if copy_to_clipboard:
        pyperclip.copy(output)
        print(f"{Fore.GREEN}Content copied to clipboard.{Style.RESET_ALL}")

def all_tiers(tiers, copy_to_clipboard, output_file):
    output = "\n".join(
        f"{tier.capitalize()} {price}\n" + "\n".join(benefits) + "\n"
        for tier, (benefits, price) in tiers.items()
    )

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"{Fore.GREEN}Output written to '{output_file}'.{Style.RESET_ALL}")
    else:
        print(output)

    if copy_to_clipboard:
        pyperclip.copy(output)
        print(f"{Fore.GREEN}Content copied to clipboard.{Style.RESET_ALL}")

def export_tiers(tiers, format_type, output_file):
    export_formats = {
        "json": lambda: json.dump(tiers, open(output_file, "w", encoding="utf-8"), indent=4),
        "csv": lambda: write_csv(tiers, output_file),
        "markdown": lambda: write_markdown(tiers, output_file),
        "html": lambda: write_html(tiers, output_file),
        "xml": lambda: write_xml(tiers, output_file),
        "yaml": lambda: yaml.dump(tiers, open(output_file, "w", encoding="utf-8")),
        "toml": lambda: toml.dump(tiers, open(output_file, "w", encoding="utf-8")),
        "latex": lambda: write_latex(tiers, output_file),
        "rss": lambda: write_rss(tiers, output_file),
        "asciidoc": lambda: write_asciidoc(tiers, output_file),
        "odt": lambda: write_odt(tiers, output_file),
        "turtle": lambda: write_turtle(tiers, output_file),
    }
    
    if format_type in export_formats:
        export_formats[format_type]()
        print(f"{Fore.GREEN}Exported to '{output_file}' in {format_type.upper()} format.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Unsupported export format: '{format_type}'.{Style.RESET_ALL}")

def write_csv(tiers, output_file):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Tier", "Price", "Benefit"])
        for tier, (benefits, price) in tiers.items():
            writer.writerows([[tier.capitalize(), price, benefit] for benefit in benefits])

def write_markdown(tiers, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        for tier, (benefits, price) in tiers.items():
            f.write(f"## {tier.capitalize()} {price}\n" + "".join(f"- {benefit}\n" for benefit in benefits) + "\n")

def write_html(tiers, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("<html><body>\n" + "".join(
            f"<h2>{tier.capitalize()} {price}</h2><ul>" + "".join(f"<li>{benefit}</li>" for benefit in benefits) + "</ul>\n"
            for tier, (benefits, price) in tiers.items()) + "</body></html>\n")

def write_xml(tiers, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("<tiers>\n" + "".join(
            f'  <tier name="{tier.capitalize()}" price="{price}">' + "".join(
                f"<benefit>{benefit}</benefit>" for benefit in benefits) + "</tier>\n"
            for tier, (benefits, price) in tiers.items()) + "</tiers>\n")

def write_latex(tiers, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\\documentclass{article}\n\\begin{document}\n" + "".join(
            f"\\section*{{{tier.capitalize()} {price}}}\n\\begin{{itemize}}\n" + "".join(
                f"\\item {benefit}\n" for benefit in benefits) + "\\end{itemize}\n"
            for tier, (benefits, price) in tiers.items()) + "\\end{document}\n")

def write_rss(tiers, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("<?xml version='1.0' encoding='UTF-8' ?>\n<rss version='2.0'><channel>\n"
                "<title>Patreon Tiers</title>\n<link>http://example.com</link>\n"
                "<description>Patreon Tiers Description</description>\n" + "".join(
            f"<item><title>{tier.capitalize()} {price}</title><description>\n" + "".join(
                f"{benefit}<br />\n" for benefit in benefits) + "</description></item>\n"
            for tier, (benefits, price) in tiers.items()) + "</channel></rss>\n")

def write_asciidoc(tiers, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("".join(f"== {tier.capitalize()} {price}\n" + "".join(
            f"- {benefit}\n" for benefit in benefits) + "\n" for tier, (benefits, price) in tiers.items()))

def write_odt(tiers, output_file):
    from odf.opendocument import OpenDocumentText
    from odf.text import P, H
    doc = OpenDocumentText()
    for tier, (benefits, price) in tiers.items():
        doc.text.addElement(H(outlinelevel=1, text=f"{tier.capitalize()} {price}"))
        for benefit in benefits:
            doc.text.addElement(P(text=benefit))
    doc.save(output_file)

def write_turtle(tiers, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("@prefix ex: <http://example.org/> .\n" + "".join(
            f"ex:{tier.capitalize()} a ex:Tier ;\n    ex:price \"{price}\" ;\n" + "".join(
                f"    ex:benefit \"{benefit}\" ;\n" for benefit in benefits) + " .\n\n"
            for tier, (benefits, price) in tiers.items()))

def show_help():
    help_text = (
        f"{Fore.CYAN}Usage: python main.py <tier_name> [options]{Style.RESET_ALL}\n\n"
        f"{Fore.YELLOW}Options:{Style.RESET_ALL}\n"
        "  -h, --help           Show this help message and exit\n"
        "  -i, --input <file>   Specify the input file (default: tiers.txt)\n"
        "  -t, --tiers          List available tiers and prices\n"
        "  -b, --benefits       List all unique benefits across tiers\n"
        "  -a, --all            Output all tiers with benefits\n"
        "  -r, --reverse        List benefits in reverse order (higher tier benefits appear first)\n"
        "  -c, --copy           Copy output to clipboard\n"
        "  -o, --output <file>  Specify a file to write output (default: output.txt)\n"
        "  -e, --export <fmt>   Export all tiers to different format (json, csv, markdown, html, xml, yaml, toml, turtle, latex, rss, asciidoc, odt)\n"
    )

    terminal_width = 80
    try:
        terminal_width = os.get_terminal_size().columns
    except OSError:
        pass

    for line in help_text.splitlines():
        print("\n".join(textwrap.wrap(line, width=terminal_width)))

def main():
    input_file = "tiers.txt"
    output_file = None
    args = sys.argv[1:]

    if not args or any(arg in args for arg in ("--help", "-h")):
        show_help()
        return

    if "-i" in args or "--input" in args:
        input_index = args.index("-i") if "-i" in args else args.index("--input")
        input_file = args[input_index + 1]

    tiers = load_tiers(input_file)
    copy_to_clipboard = "-c" in args or "--copy" in args
    output_file = args[args.index("-o") + 1] if ("-o" in args or "--output" in args) else "output.txt"

    cascade_reverse(tiers) if ("-r" in args or "--reverse" in args) else cascade(tiers)

    if "-t" in args or "--tiers" in args:
        table = ""
        for tier, (benefits, price) in tiers.items():
            table += f"{tier.capitalize():<15} {price:<10}\n"
        print(f"{Fore.CYAN}{table}{Style.RESET_ALL}")
        if copy_to_clipboard:
            pyperclip.copy(table)
        if ("-o" in args or "--output" in args):
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(table)
        return

    if "-b" in args or "--benefits" in args:
        benefits = "\n".join({benefit for tier in tiers.values() for benefit in tier[0]})
        print(benefits)
        if copy_to_clipboard:
            pyperclip.copy(benefits)
        if ("-o" in args or "--output" in args):
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(benefits)
        return

    if "-a" in args or "--all" in args:
        all_tiers(tiers, copy_to_clipboard, output_file)
        return

    if "-e" in args or "--export" in args:
        format_type = args[args.index("--export") + 1] if "--export" in args else args[args.index("-e") + 1]
        export_tiers(tiers, format_type, output_file)
        return
    
    if "--logo" in args:
        return print("""
       %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#       
    @%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#%#    
   %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%   
  @%%%%%%%%%%%%%%%%%%%%%%#*+*#%%%%%%%%%%%%%%%%%%%%%#%  
  @%%%%%%%%%%%%%%%%%%%#=:::::::=#%%%%%%%%%%%%%%%%%%%%  
  @%%%%%%%%%%%%%%%%%#=:::::::::::=#%%%%%%%%%%%%%%%%%%  
  %%%%%%%%%%%%%#**+=::::::=*=::::::=+**##%%%%%%%%%%%%  
  @%%%%%%%%#+:::::::::::=#%%%#=:::::::::::=#%%%%%%%%%  
  @%%%%%%%+:::::::::::=#%%%%%%%*-:::::::::::=#%%%%%%%  
  @%%%%%%=:::::=+*###%%%%%%%%%%%%%##**+=:::::=#%%%%%%  
  %%%%%%#:::::#%%%%%%%%%%%%%%%%%%%%%%%%%*:::::*%%%%%%  
  %%%%%%+::::+%%%%%##%%%%%%%%#*****#%%%%%=::::+%%%%%%  
  %%%%%%+::::*%%%#-:::=%%%%+::::::::-#%%%+::::+%%%%%%  
  %%%%%%+::::*%%%#-:::=%%%%+::::::::-#%%%+::::+%%%%%%  
  @%%%%%+::::*%%%%%##%%%%%%%%#######%%%%%+::::+%%%%%%  
  %%%%%%+::::*%%%%%%%%%%%%%%%%%%%%%%%%%%%+::::+%%%%%%  
  %%%%%%+::::*%%%%#***%%%%%%#*+++++*%%%%%+::::+%%%%%%  
  %%%%%%+::::*%%%#-:::-%%%%+::::::::-#%%%+::::+%%%%%%  
  @%%%%%+::::*%%%%=:::+%%%%*::::::::=%%%%+::::+%%%%%%  
  @%%%%%+::::=%%%%%%#%%%%%%%%######%%%%%%=::::*%%%%%%  
  %%%%%%#:::::*%%%%%%%%%%%%%%%%%%%%%%%%%*::::-#%%%%%%  
  @%%%%%%+:::::-=+*******************+=-:::::+%%%%%%%  
  @%%%%%%%+:::::::::::::::::::::::::::::::::+%%%%%%%%  
  @%%%%%%%%%+:::::::::::::::::::::::::::::*%%%%%%%%%%  
  %%%%%%%%%%%%%%##*******************#%%%%%%%%%%%%%%%  
   @%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%   
    @%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
       @%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@       
""")

    selected_tier = args[0]
    if not ("-o" in args or "--output" in args):
        output_file = None
    tier_info(tiers, selected_tier, copy_to_clipboard, output_file)

if __name__ == "__main__":
    main()
