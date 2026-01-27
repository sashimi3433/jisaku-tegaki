import click
import os
from utils.template import create_template
from processor.extractor import CharacterExtractor
from font_builder.builder import FontBuilderWrapper

DEFAULT_CHARS = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"

@click.group()
def cli():
    """自作手書きフォント作成ツール"""
    pass

@cli.command()
@click.option("--output", "-o", default="template.png", help="出力ファイル名")
@click.option("--chars", "-c", default=DEFAULT_CHARS, help="対象とする文字（文字列）")
def generate_template(output, chars):
    """書き込み用テンプレート画像を生成します"""
    click.echo(f"Generating template with {len(chars)} characters...")
    create_template(output_path=output, chars=chars)
    click.echo(f"Done! Please write characters in {output} and scan it.")

@cli.command()
@click.argument("image_path")
@click.option("--output", "-o", default="myfont.ttf", help="出力フォント名 (.ttf)")
@click.option("--name", "-n", default="MyHandwriting", help="フォント名")
@click.option("--chars", "-c", default=DEFAULT_CHARS, help="対象とする文字（文字列）")
def build(image_path, output, name, chars):
    """スキャン画像からフォントを生成します"""
    if not os.path.exists(image_path):
        click.echo(f"Error: Image {image_path} not found.", err=True)
        return

    click.echo("Extracting characters...")
    extractor = CharacterExtractor()
    extracted_paths = extractor.process(image_path)
    
    click.echo(f"Extracted {len(extracted_paths)} character images.")
    
    # Map extracted images to characters
    # Note: extractor saves as char_y_x.png
    char_data = []
    char_list = list(chars)
    
    for y in range(10): # grid size is 10x10 by default
        for x in range(10):
            idx = y * 10 + x
            if idx >= len(char_list):
                break
            
            img_path = f"extracted/char_{y}_{x}.png"
            if os.path.exists(img_path):
                char_data.append({
                    'char': char_list[idx],
                    'image_path': img_path
                })
    
    if not char_data:
        click.echo("Error: No characters extracted. Check if markers are visible.", err=True)
        return

    click.echo(f"Building font '{name}' with {len(char_data)} glyphs...")
    builder = FontBuilderWrapper(font_name=name)
    builder.build(char_data, output_path=output)
    click.echo(f"Success! Font saved to {output}")

if __name__ == "__main__":
    cli()
