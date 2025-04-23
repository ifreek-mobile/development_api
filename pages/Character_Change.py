import streamlit as st
import fal_client
import base64
import imghdr  # 画像形式判定用
import os
from openai import OpenAI

# 環境変数からAPIキーを取得
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()


def translate_prompt_to_english(text: str) -> str:
    """
    日本語のプロンプトを英語に翻訳して返します。
    - text が空文字なら、翻訳処理をスキップしてそのまま空文字を返却します。
    - 文字列がある場合のみ GPT-4.1 Nano に問い合わせます。
    """
    if not text:
        return ""
    resp = client.chat.completions.create(
        model="gpt-4.1-nano-2025-04-14",
        messages=[
            {"role": "system", "content": "You are a helpful translator."},
            {"role": "user", "content": f"次の日本語を英語に翻訳してください: 「{text}」"}
        ],
        temperature=0
    )
    return resp.choices[0].message.content.strip()


def main():
    # ——— 補足情報表示セクション ———
    # ここでは「生成コスト」「使い方のヒント」などを非表示状態から展開して
    # 必要に応じて確認できるようにしています。
    with st.expander("✏️ 補足情報の表示（クリックで展開）", expanded=False):
        st.write("""
        - 1 回の画像生成あたり約 15 円です。
        - 日本語でプロンプトの入力が可能ですが、送信時に自動的に英訳されます。
        - プロンプトみ入力でもOK
        """)
    # ————————————————————————

    st.title("お人形風に変換 / 画像→画像生成")

    with st.form("plushify_form"):
        image_file = st.file_uploader(
            "画像をアップロード", type=["png", "jpg", "jpeg"],
            help="生成したい写真やイラストをアップロードしてください。"
        )
        prompt = st.text_input(
            "プロンプト（日本語）",
            value="猫の姿をしている",
            help="未入力の場合は空文字が渡され、翻訳はスキップされます。"
        )
        submit = st.form_submit_button("▶️ 生成開始")

    if not submit:
        return

    # プロンプトが空文字なら ""、そうでなければ英訳を実行
    translated_prompt = translate_prompt_to_english(prompt)
    # デバッグ用ログ（CLI やコンテナのログに出力されます）
    print(f"Translated Prompt: {translated_prompt}")

    logs_placeholder = st.empty()

    def on_queue_update(update):
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                logs_placeholder.text(log["message"])

    # 画像データを base64 に変換
    if image_file:
        image_bytes = image_file.read()
        img_type = imghdr.what(None, h=image_bytes)
        mime = f"image/{'jpeg' if img_type=='jpg' else img_type}"
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        image_url = f"data:{mime};base64,{b64}"
    else:
        image_url = ""

    with st.spinner("処理中…"):
        # fal-ai/plushify API に送信
        result = fal_client.subscribe(
            "fal-ai/plushify",
            arguments={
                "image_url": image_url,
                "prompt": translated_prompt,
                "enable_safety_checker": False,
            },
            with_logs=True,
            on_queue_update=on_queue_update,
        )

    # 生成結果の表示
    images = result.get("images", [])
    if images:
        st.success("画像生成が完了しました！")
        for i, img in enumerate(images):
            st.image(img["url"], caption=f"Image {i}", width=img.get("width"))
        st.write("### 画像データ（JSON）")
        st.json({"images": images})
    else:
        st.error("画像データが取得できませんでした。")


if __name__ == "__main__":
    main()
