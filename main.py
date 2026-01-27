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

def load_kanken_sets():
    csv_path = "漢検漢字辞典漢字.csv"
    if not os.path.exists(csv_path):
        import urllib.request
        import ssl
        url = "https://raw.githubusercontent.com/mimneko/kanji-data/main/%E6%BC%A2%E6%A4%9C%E6%BC%A2%E5%AD%97%E8%BE%9E%E5%85%B8%E6%BC%A2%E5%AD%97.csv"
        print(f"Downloading Kanken CSV from {url}...")
        try:
            # SSL証明書のエラーを回避するための設定
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(url, context=context) as response, open(csv_path, 'wb') as out_file:
                out_file.write(response.read())
            print("Download complete.")
        except Exception as e:
            print(f"Warning: Could not download Kanken CSV: {e}")
            return
    
    import csv
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # 漢検級 -> 文字リスト の辞書
            grade_map = {}
            for row in reader:
                grade = row.get("漢検級")
                char = row.get("漢字テキスト")
                if grade and char:
                    # 級名を識別しやすい形式に変換 (例: "準1級" -> "j1", "10級" -> "10")
                    g_key = grade.replace("級", "")
                    if "準" in g_key:
                        g_key = "j" + g_key.replace("準", "")
                    
                    if g_key not in grade_map:
                        grade_map[g_key] = ""
                    # 既に登録されている文字は避ける（異体字などで重複があるため）
                    if char not in grade_map[g_key]:
                        grade_map[g_key] += char
            
            # 各級をプリセットとして登録 (例: kanken_1, kanken_j1, kanken_2, ...)
            for g_key, chars in grade_map.items():
                preset_name = f"kanken_{g_key}"
                CHAR_SETS[preset_name] = chars
    except Exception as e:
        print(f"Warning: Could not load Kanken CSV: {e}")

# 初期化時に漢検セットをロード
load_kanken_sets()

def resolve_char_groups(chars_input):
    if not chars_input:
        chars_input = DEFAULT_CHARS
    
    parts = chars_input.split(",")
    result_groups = []
    
    # 展開用カテゴリリスト
    BASIC_CATS = ["hiragana", "katakana", "alphabet", "number", "symbol"]
    KANKEN_GRADES = ["10", "9", "8", "7", "6", "5", "4", "3", "j2", "2", "j1", "1"]

    for i, p in enumerate(parts):
        p = p.strip()
        if p == "basic":
            for cat in BASIC_CATS:
                if cat in CHAR_SETS:
                    result_groups.append((cat, CHAR_SETS[cat]))
        elif p == "kanken":
            for g in KANKEN_GRADES:
                key = f"kanken_{g}"
                if key in CHAR_SETS:
                    result_groups.append((key, CHAR_SETS[key]))
        elif p in CHAR_SETS:
            result_groups.append((p, CHAR_SETS[p]))
        else:
            # プリセット名でなければ generic な名前でグループ化
            result_groups.append((f"custom_{i}", p))
            
    return result_groups

DEFAULT_CHARS = "basic"

@click.group()
def cli():
    """自作手書きフォント作成ツール"""
    pass

@cli.command()
@click.option("--output", "-o", default="template.png", help="出力ファイル名")
@click.option("--chars", "-c", default=DEFAULT_CHARS, help="対象とする文字（文字列またはプリセット名）")
def generate_template(output, chars):
    """書き込み用テンプレート画像を生成します"""
    groups = resolve_char_groups(chars)
    total_chars = sum(len(g[1]) for g in groups)
    click.echo(f"Generating template for {len(groups)} groups ({total_chars} characters)...")
    create_template(output_path=output, groups=groups)
    click.echo(f"Done! Templates generated.")

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

    # 古い一時ファイルをクリーンアップ
    if os.path.exists("extracted"):
        import shutil
        shutil.rmtree("extracted")
    os.makedirs("extracted")

    groups = resolve_char_groups(chars)
    char_data = []
    extractor = CharacterExtractor()
    
    # 事前にマッピングプランを表示
    click.echo("--- Build Plan ---")
    mapping_plan = []
    temp_idx = 0
    chars_per_page = 100
    for label, chars_str in groups:
        char_list = list(chars_str)
        num_pages = (len(char_list) + chars_per_page - 1) // chars_per_page
        for p in range(num_pages):
            if temp_idx < len(image_paths):
                mapping_plan.append((image_paths[temp_idx], label, p))
            temp_idx += 1
    
    for img, lbl, p in mapping_plan:
        click.echo(f"  Image: {img} -> Group: {lbl} (Page {p+1})")
    
    if len(image_paths) < temp_idx:
        click.echo(f"Warning: Missing {temp_idx - len(image_paths)} images for the specified characters.", err=True)
    elif len(image_paths) > temp_idx:
        click.echo(f"Warning: {len(image_paths) - temp_idx} extra images provided and will be ignored.", err=True)
    
    click.echo("------------------")

    image_idx = 0
    for label, chars_str in groups:
        char_list = list(chars_str)
        num_pages = (len(char_list) + chars_per_page - 1) // chars_per_page
        
        for p in range(num_pages):
            if image_idx >= len(image_paths):
                break
            
            image_path = image_paths[image_idx]
            if not os.path.exists(image_path):
                click.echo(f"  Warning: Image {image_path} not found. Skipping.", err=True)
                image_idx += 1
                continue

            click.echo(f"Processing {image_path} as {label} (Page {p+1})...")
            extractor.process(image_path, page=f"{label}_{p}")
            
            for y in range(10):
                for x in range(10):
                    char_idx_in_group = p * chars_per_page + y * 10 + x
                    if char_idx_in_group >= len(char_list):
                        break
                    
                    img_path = f"extracted/char_{label}_{p}_{y}_{x}.png"
                    if os.path.exists(img_path):
                        char_data.append({
                            'char': char_list[char_idx_in_group],
                            'image_path': img_path
                        })
            
            image_idx += 1
    
    if not char_data:
        click.echo("Error: No characters extracted. Check images and markers.", err=True)
        return

    click.echo(f"Building font '{name}' with {len(char_data)} glyphs...")
    builder = FontBuilderWrapper(font_name=name)
    builder.build(char_data, output_path=output)
    click.echo(f"Success! Font saved to {output}")

if __name__ == "__main__":
    cli()
