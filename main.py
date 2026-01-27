import click
import os
from utils.template import create_template
from processor.extractor import CharacterExtractor
from font_builder.builder import FontBuilderWrapper

CHAR_SETS = {
    "hiragana": "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん",
    "katakana": "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン",
    "alphabet": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "number": "0123456789",
    "symbol": "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~",
}
# すべてを統合するショートカット
CHAR_SETS["basic"] = CHAR_SETS["hiragana"] + CHAR_SETS["katakana"] + CHAR_SETS["alphabet"] + CHAR_SETS["number"] + CHAR_SETS["symbol"]

def resolve_chars(chars_input):
    if not chars_input:
        return CHAR_SETS["hiragana"]
    
    # カンマ区切りで複数のプリセットを連結できるようにする (例: "hiragana,number")
    parts = chars_input.split(",")
    resolved = ""
    for p in parts:
        p = p.strip()
        if p in CHAR_SETS:
            resolved += CHAR_SETS[p]
        else:
            resolved += p # プリセット名でなければそのまま文字として扱う
    return resolved

DEFAULT_CHARS = "hiragana"

@click.group()
def cli():
    """自作手書きフォント作成ツール"""
    pass

@cli.command()
@click.option("--output", "-o", default="template.png", help="出力ファイル名")
@click.option("--chars", "-c", default=DEFAULT_CHARS, help="対象とする文字（文字列またはプリセット名）")
def generate_template(output, chars):
    """書き込み用テンプレート画像を生成します"""
    resolved_chars = resolve_chars(chars)
    click.echo(f"Generating template with {len(resolved_chars)} characters...")
    create_template(output_path=output, chars=resolved_chars)
    click.echo(f"Done! Please write characters in {output} and scan it.")

@cli.command()
@click.argument("image_paths", nargs=-1)
@click.option("--output", "-o", default="myfont.ttf", help="出力フォント名 (.ttf)")
@click.option("--name", "-n", default="MyHandwriting", help="フォント名")
@click.option("--chars", "-c", default=DEFAULT_CHARS, help="対象とする文字（文字列またはプリセット名）")
def build(image_paths, output, name, chars):
    """スキャン画像（複数可）からフォントを生成します"""
    if not image_paths:
        click.echo("Error: Please provide at least one scan image path.", err=True)
        return

    resolved_chars = resolve_chars(chars)
    char_list = list(resolved_chars)
    char_data = []
    extractor = CharacterExtractor()

    for p, image_path in enumerate(image_paths):
        if not os.path.exists(image_path):
            click.echo(f"Warning: Image {image_path} not found. Skipping.", err=True)
            continue

        click.echo(f"Processing {image_path} (Page {p+1})...")
        extracted_paths = extractor.process(image_path, page=p)
        click.echo(f"  Extracted {len(extracted_paths)} characters from Page {p+1}.")

        # Map current page characters
        # chars_per_page is 100 (10x10)
        chars_per_page = 100
        for y in range(10):
            for x in range(10):
                idx = p * chars_per_page + y * 10 + x
                if idx >= len(char_list):
                    break
                
                img_path = f"extracted/char_{p}_{y}_{x}.png"
                if os.path.exists(img_path):
                    char_data.append({
                        'char': char_list[idx],
                        'image_path': img_path
                    })
    
    if not char_data:
        click.echo("Error: No characters extracted. Check images and markers.", err=True)
        return

    click.echo(f"Building font '{name}' with {len(char_data)} glyphs...")
    builder = FontBuilderWrapper(font_name=name)
    builder.build(char_data, output_path=output)
    click.echo(f"Success! Font saved to {output}")

if __name__ == "__main__":
    cli()
