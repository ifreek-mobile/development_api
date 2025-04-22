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
    """日本語のプロンプトを英語に翻訳して返します。空文字ならそのまま返却。"""
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
    st.title("画像→画像生成 / お人形風に変換デモ")

    with st.form("plushify_form"):
        image_file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg"])
        prompt = st.text_input("プロンプト", value="猫の姿をしている", help="未入力なら空文字が送信されます。")
        submit = st.form_submit_button("▶️ 生成開始")

    if not submit:
        return

    # 追加：翻訳関数を呼び出して英語プロンプトを生成
    translated_prompt = translate_prompt_to_english(prompt)
    print(f"Translated Prompt: {translated_prompt}")

    logs_placeholder = st.empty()

    def on_queue_update(update):
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                logs_placeholder.text(log["message"])

    if image_file:
        image_bytes = image_file.read()
        img_type = imghdr.what(None, h=image_bytes)
        mime = f"image/{'jpeg' if img_type=='jpg' else img_type}"
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        image_url = f"data:{mime};base64,{b64}"
    else:
        image_url = ""

    with st.spinner("処理中…"):
        result = fal_client.subscribe(
            "fal-ai/plushify",
            arguments={
                "image_url": image_url,
                "prompt": translated_prompt,  # 翻訳後のプロンプトを渡す
                "enable_safety_checker": False,
            },
            with_logs=True,
            on_queue_update=on_queue_update,
        )

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
