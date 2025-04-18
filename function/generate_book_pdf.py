from PIL import Image, ImageDraw
import random
from fpdf import FPDF
import tempfile
from PIL import Image
from io import BytesIO
from typing import List

def generate_pdf(illustration_data_list: List[bytes], background_data_list: List[bytes]) -> bytes:
    """
    イラスト画像と背景画像を1ページ内で左右に並べて合成し、
    各ペアを1ページとしてPDFファイルを生成。

    - 先頭ページとして表紙画像(画像素材/front-cover.png)を挿入。
    - 各画像は正方形のアスペクト比を想定し、左右に並べて横幅を2倍にして合成し、
      最終的に正方形 × 2(横に連結)のサイズとなる大きな画像を1ページに配置します。
    - 出力PDFはページサイズを (2250pt × 2048pt) の正方形に設定し、
      左半分(幅1125px)にイラスト、右半分(幅1125px)にテキスト背景をそれぞれリサイズ配置します。
      (※ 実際には 2250 ÷ 2 = 1125 という計算例)

    Args:
        illustration_data_list (list): イラスト画像のバイトデータのリスト（要素数 n）
        background_data_list (list): 背景画像のバイトデータのリスト（要素数 n）

    Returns:
        bytes: PDFデータをバイト列として返します
    """
    if len(illustration_data_list) != len(background_data_list):
        raise ValueError("イラスト画像と背景画像のリストは同じ数である必要があります。")

    # FPDF でページサイズを 2250×2048 pt に設定
    pdf_width = 2250
    pdf_height = 2048
    pdf = FPDF(unit="pt", format=[pdf_width, pdf_height])
    pdf.set_auto_page_break(auto=False)

    # ----------------------------
    # (1) 【追加】表紙画像を最初のページに挿入
    # ----------------------------
    front_cover_path = "disco/images/front-cover.png"  # 指定された表紙のパス
    try:
        cover_img = Image.open(front_cover_path).convert("RGB")
        cover_img = cover_img.resize((pdf_width, pdf_height), Image.LANCZOS)
    except Exception as e:
        raise ValueError(f"表紙画像を開けませんでした: {e}")

    pdf.add_page()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmpfile:
        cover_img.save(tmpfile, format='JPEG')
        tmpfile.seek(0)
        pdf.image(tmpfile.name, x=0, y=0, w=pdf_width, h=pdf_height)

    # ----------------------------
    # (2) 従来のイラスト+背景のページ生成処理
    # ----------------------------
    # 左右に分割して貼り付ける幅・高さ
    left_img_width = pdf_width // 2
    left_img_height = pdf_height
    right_img_width = pdf_width // 2
    right_img_height = pdf_height

    # 各イラスト＆背景画像のペアごとにページを追加
    for i, (illus_data, back_data) in enumerate(zip(illustration_data_list, background_data_list)):
        # 1. 左のイラスト画像を開いてリサイズ
        try:
            illus_img = Image.open(BytesIO(illus_data)).convert('RGB')
        except Exception as e:
            raise ValueError(f"{i+1}番目のイラスト画像を開けませんでした: {e}")

        illus_img = illus_img.resize((left_img_width, left_img_height), Image.LANCZOS)

        # 2. 右の背景画像を開いてリサイズ
        try:
            back_img = Image.open(BytesIO(back_data)).convert('RGB')
        except Exception as e:
            raise ValueError(f"{i+1}番目の背景画像を開けませんでした: {e}")

        back_img = back_img.resize((right_img_width, right_img_height), Image.LANCZOS)

        # 3. 新たな空イメージを作成
        combined_img = Image.new("RGB", (pdf_width, pdf_height), (255, 255, 255))
        combined_img.paste(illus_img, (0, 0))
        combined_img.paste(back_img, (left_img_width, 0))

        # 4. ページを追加し、合成画像を一時ファイルに保存→PDFに貼り付け
        pdf.add_page()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmpfile:
            combined_img.save(tmpfile, format='JPEG')
            tmpfile.seek(0)
            pdf.image(tmpfile.name, x=0, y=0, w=pdf_width, h=pdf_height)

    # PDFデータをバイト列として取得
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes

# テスト用コード
def main():
    """
    テスト実行時:
      1. まず「表紙画像 (front-cover.png)」を1ページ目に
      2. 続いてイラスト&背景ペアを3回分追加（合計4ページ）
    """
    illustration_data_list = []
    background_data_list = []

    # (1) ダミーのイラスト3枚 + 背景3枚を用意する (合計3ページ分)
    base_w, base_h = 900, 1600
    for i in range(3):
        # イラスト用ダミー画像
        illus_img = Image.new("RGB", (base_w, base_h), color=_random_color())
        draw_illus = ImageDraw.Draw(illus_img)
        draw_illus.text((50, 50), f"Illustration {i+1}", fill=(255, 255, 255))

        illus_bytes = BytesIO()
        illus_img.save(illus_bytes, format="PNG")
        illus_bytes.seek(0)
        illustration_data_list.append(illus_bytes.getvalue())

        # 背景用ダミー画像
        back_img = Image.new("RGB", (base_w, base_h), color=_random_color())
        draw_back = ImageDraw.Draw(back_img)
        draw_back.text((50, 50), f"Background {i+1}", fill=(255, 255, 255))

        back_bytes = BytesIO()
        back_img.save(back_bytes, format="PNG")
        back_bytes.seek(0)
        background_data_list.append(back_bytes.getvalue())

    # (2) PDF生成 (表紙 + 3ページ = 合計4ページ)
    pdf_data = generate_pdf(illustration_data_list, background_data_list)

    # (3) ファイルに書き出して確認
    output_filename = "sample_output.pdf"
    with open(output_filename, "wb") as f:
        f.write(pdf_data)

    print(f"[INFO] PDFを '{output_filename}' に出力しました。")

def _random_color():
    """背景色として適当なRGB値のタプルを返すヘルパー関数"""
    import random
    return tuple(random.randint(0, 255) for _ in range(3))

if __name__ == "__main__":
    main()
