import base64
import requests
import os
from openai import OpenAI
from function.disco_prompts import FACE_FEATURE_PROMPT, FACE_TO_ADULT_PROMPT

# テスト用
#from disco_prompts import FACE_FEATURE_PROMPT, FACE_TO_ADULT_PROMPT

# 環境変数からAPIキーを取得
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()


def encode_image(image_bytes):
    """画像バイトデータをbase64形式にエンコードする。"""
    return base64.b64encode(image_bytes).decode('utf-8')


# 画像をgpt-4.1-mini-2025-04-14で解析し、画像生成AI用の顔画像プロンプトを生成する。
def extract_face_features(uploaded_image, face_features_prompt):
    """
    画像をgpt-4.1-mini-2025-04-14で解析し、画像生成AI用の顔画像プロンプトを生成する。
    Args:
        uploaded_image: 画像データ
        face_features_prompt (str): プロンプト
    Returns:
        str: 生成されたプロンプト
    """
    base64_image = encode_image(uploaded_image)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4.1-mini-2025-04-14",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": face_features_prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 4000
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    response_data = response.json()

    if 'choices' in response_data and len(response_data['choices']) > 0:
        return response_data['choices'][0]['message']['content']
    else:
        raise Exception("gpt-4.1-mini-2025-04-14の応答が無効です。")


# テスト実行用コード
def main():
    """
    テスト実行コード。
    画像ファイルを読み込み、extract_face_features 関数を呼び出して結果を表示する。
    """

    # 画像ファイルへのパスを指定
    image_path = "画像素材/子供の顔画像/女の子2.png"

    if not os.path.isfile(image_path):
        print(f"[エラー] 画像ファイルが見つかりません: {image_path}")
        return

    # 画像を読み込み、バイトデータに変換
    with open(image_path, "rb") as f:
        uploaded_image = f.read()

    try:
        gender = "女の子"
        # 関数を呼び出して結果を取得
        result_prompt = extract_face_features(
            uploaded_image, FACE_FEATURE_PROMPT.format(gender=gender))
        print("ーーーーー 生成された子供の顔の特徴プロンプト ーーーーー")
        print(result_prompt)
        result_prompt2 = extract_face_features(
            uploaded_image, FACE_TO_ADULT_PROMPT.format(child_face_prompt=result_prompt))
        print("ーーーーー 生成された大人の顔の特徴プロンプト ーーーーー")
        print(result_prompt2)
    except Exception as e:
        print(f"[エラー] 処理中にエラーが発生しました: {e}")


if __name__ == "__main__":
    main()
