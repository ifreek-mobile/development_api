import streamlit as st
import fal_client
import base64
import imghdr  # 画像形式判定用


def main():
    st.title("画像→画像生成 / ジブリ風スタイル変換")

    # 画像アップロードだけのフォーム
    with st.form("plushify_form"):
        image_file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg"])
        submit = st.form_submit_button("▶️ 生成開始")

    if not submit:
        return

    logs_placeholder = st.empty()

    def on_queue_update(update):
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                logs_placeholder.text(log["message"])

    # 画像を Data URI に変換
    if image_file:
        image_bytes = image_file.read()
        img_type = imghdr.what(None, h=image_bytes)
        mime = f"image/{'jpeg' if img_type=='jpg' else img_type}"
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        image_url = f"data:{mime};base64,{b64}"
    else:
        image_url = ""

    # fal-ai/ghiblify モデルで変換
    with st.spinner("処理中…"):
        result = fal_client.subscribe(
            "fal-ai/ghiblify",
            arguments={
                "image_url": image_url,
            },
            with_logs=True,
            on_queue_update=on_queue_update,
        )

    # 生成画像を表示
    img = result.get("image")
    if img:
        st.success("画像生成が完了しました！")
        # 画像表示
        st.image(
            img["url"],
            caption=img.get("file_name", ""),
            width=img.get("width")
        )
        # JSON データ表示
        st.write("### 画像データ（JSON）")
        st.json({"image": img})
    else:
        st.error("画像データが取得できませんでした。")


if __name__ == "__main__":
    main()
