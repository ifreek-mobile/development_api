# streamlit_app.py
import streamlit as st
import base64
from openai import OpenAI

client = OpenAI()

st.title("アップロード画像 → 漫画アニメ変換")

# ──────────────────────────────
# イラスト用プロンプト
# ──────────────────────────────
child_image_prompt = """
入力された画像の構図を維持しつつ以下のプロンプトのように漫画アニメスタイルに変換してほしい。
ーーーーーー
[漫画的なアニメスタイル、鮮やかで彩度の高い色彩、ダイナミックな照明効果、小学生向けの漫画風イラスト],[顔の輪郭は幼い子供特有の滑らかで丸みを帯びており、柔らかく優しい顔立ちをしている。],[漫画のような表情、鮮やかで彩度の高い色彩、ダイナミックな照明効果など、子供向けの柔らかな美的感覚（小学生向き）を備えた漫画風のアニメスタイルで描かれている]。
ーーーーーー
"""

adult_image_prompt = """
・入力されたイラスト画像はユーザーの子供時代のイラストで、タッチのみ継承すること、子供や背景などの情報は一旦参照しなくて良い。
・あなたは入力された子供が大人になったイラストを、以下のプロンプトのように漫画アニメスタイルに変換してください。
・入力画像と比較して生成イラストの構図や背景は必ず変更すること(大人に変換することにフォーカスすること)
・イラストのタッチのスタイルを継承しつつ下記の「イラストスタイル」「イラストの内容」考慮して生成してください。

ーーーーーー
イラストスタイル
[漫画的なアニメスタイル、鮮やかで彩度の高い色彩、ダイナミックな照明効果、小学生向けの漫画風イラスト],[顔の輪郭は大人の特有の優しい顔立ちをしている。], [漫画のような表情、鮮やかで彩度の高い色彩、ダイナミックな照明効果など、子供向けの柔らかな美的感覚（小学生向き）を備えた漫画風のアニメスタイルで描かれている]

イラストの内容(構図/描写/ポーズ/シーン)
[太郎くんは大きくなって、世界中の高い所から景色を見るお仕事をしています。あの時の観覧車の気持ちを忘れず、いつも笑っているよ。]
ーーーーーー
"""

# ──────────────────────────────
# ストーリー用プロンプト
# ──────────────────────────────

# ──────────────────────────────
# 入力値項目
# ──────────────────────────────
name = st.text_input("名前 (15文字以内)", max_chars=15, key="name")
gender = st.selectbox("性別", ["男の子", "女の子"], key="gender")
memory_type = st.text_input("思い出の種類", key="memory_type")
memory_detail = st.text_area("思い出の内容", height=120, key="memory_detail")

uploaded = st.file_uploader("画像を選択", type=["png", "jpg", "jpeg"])
convert_btn = st.button("変換する", disabled=uploaded is None)

# ──────────────────────────────
# イラスト生成関数
# ──────────────────────────────


def generate_image(prompt: str, image_input) -> bytes:
    """
    image_input :
        • Streamlit UploadedFile(io.BufferedReader) もしくは
        • bytes (PNG/JPEG/WebP)
    """
    # 入力が bytes なら (filename, bytes, mime) 形式でラップ
    if isinstance(image_input, (bytes, bytearray)):
        image_param = ("input.png", image_input, "image/png")
    else:
        image_param = image_input   # UploadedFile はそのまま渡せる

    result = client.images.edit(
        model="gpt-image-1",
        image=image_param,
        prompt=prompt,
        size="1024x1536",
    )
    return base64.b64decode(result.data[0].b64_json)


# ──────────────────────────────
# ストーリー生成関数
# ──────────────────────────────


# ──────────────────────────────
# イラスト実行処理
# ──────────────────────────────
if convert_btn and uploaded:
    # ① 子供時代イラスト
    child_img_bytes = generate_image(child_image_prompt, uploaded)

    # ② その子が大人になったイラスト
    adult_img_bytes = generate_image(
        adult_image_prompt, child_img_bytes)

    # ─ 表示とダウンロード UI ─
    col1, col2 = st.columns(2)
    with col1:
        st.image(child_img_bytes, caption="子供時代イラスト", use_container_width=True)
        st.download_button(
            "子供イラストを保存",
            child_img_bytes,
            "child.png",
            "image/png",
            key="dl_child",
        )
    with col2:
        st.image(adult_img_bytes, caption="大人になったイラスト",
                 use_container_width=True)
        st.download_button(
            "大人イラストを保存",
            adult_img_bytes,
            "adult.png",
            "image/png",
            key="dl_adult",
        )
