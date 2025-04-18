import os
import fal_client
import requests
from PIL import Image
from io import BytesIO


def generate_single_image(prompt: str) -> bytes:
    """
    fal.ai を使用して 1 枚の画像を生成し、画像バイトデータを返す関数。

    Args:
        prompt (str): 生成に使用するプロンプト文字列

    Returns:
        bytes: 生成された画像（PNG形式など）のバイトデータ
               生成に失敗した場合は None を返す
    """
    # 環境変数に FAL_KEY が設定されていることを前提とします
    fal_api_key = os.getenv("FAL_KEY")
    if not fal_api_key:
        print("エラー: FAL_KEY が環境変数に設定されていません。")
        return None

    # fal_client.subscribe 呼び出し時のログ表示を受け取るコールバック（必要なければ削除）
    def on_queue_update(update):
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                print(log["message"])  # ここではコンソール出力の例

    try:
        # fal_client を用いて画像生成 API をコール
        # aspect_ratio, num_images, output_format, safety_tolerance は例として固定値を指定
        result = fal_client.subscribe(
            "fal-ai/flux-pro/v1.1-ultra",
            arguments={
                "prompt": prompt,
                "aspect_ratio": "9:16",
                "num_images": 1,
                "output_format": "jpeg",
                "safety_tolerance": "5"
            },
            with_logs=True,
            on_queue_update=on_queue_update
        )
    except fal_client.auth.MissingCredentialsError:
        print("エラー: fal.ai の認証情報が不足しています。")
        return None
    except Exception as e:
        print(f"Fal AI 画像生成中にエラーが発生しました: {e}")
        return None

    if not result:
        print("Fal AI からの応答がありませんでした。")
        return None

    # 生成結果から画像URLを取得
    images_info = result.get('images', [])
    if not images_info:
        print("Fal AI で画像が生成されませんでした。")
        return None

    # 先頭の画像URLを取得
    image_url = images_info[0].get('url')
    if not image_url:
        print("Fal AI 画像URLが取得できませんでした。")
        return None

    # 画像データをダウンロード
    try:
        response = requests.get(image_url)
        if response.status_code != 200:
            print(f"Fal AI 画像ダウンロードに失敗しました。ステータスコード: {response.status_code}")
            return None
        # Pillow で開いてバイナリ化
        img = Image.open(BytesIO(response.content))
        img_bytes = BytesIO()
        # 必要に応じてフォーマットを "JPEG" や "PNG" に変更可能
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        return img_bytes.getvalue()
    except Exception as e:
        print(f"Fal AI 画像ダウンロード中にエラーが発生しました: {e}")
        return None


# メインのコードなどで呼び出す例
if __name__ == "__main__":
    prompt_text = "A futuristic cityscape with glowing neon lights."
    image_data = generate_single_image(prompt_text)

    if image_data:
        # 必要ならファイルに保存したり、PILで再度開いて加工したりできます
        with open("fal_generated.png", "wb") as f:
            f.write(image_data)
        print("画像を fal_generated.png として保存しました。")
    else:
        print("画像の生成に失敗しました。")
