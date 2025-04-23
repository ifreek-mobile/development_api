# streamlit_app.py  ★変更後

import os
import streamlit as st
import fal_client
from openai import OpenAI

# -------------------------------------------------------
# 0. 事前チェック
# -------------------------------------------------------
if os.getenv("FAL_KEY") is None:
    st.error("環境変数 FAL_KEY が設定されていません。")
    st.stop()

openai_client = OpenAI()        # 翻訳用


def translate_prompt_to_english(text: str) -> str:
    if not text:
        return ""
    resp = openai_client.chat.completions.create(
        model="gpt-4.1-nano-2025-04-14",
        messages=[
            {"role": "system", "content": "You are a helpful translator."},
            {"role": "user", "content": f"次の日本語を英語に翻訳してください: 「{text}」"}
        ],
        temperature=0
    )
    return resp.choices[0].message.content.strip()


# -------------------------------------------------------
# 1. UI
# -------------------------------------------------------
st.set_page_config(page_title="HiDream I1 画像生成", page_icon="🖼️")
with st.expander("✏️ 補足情報の表示（クリックで展開）", expanded=False):
    st.write("""
    - 1 回の画像生成あたり約 8 円です。
    - 日本語のプロンプトの入力が可能で、裏でイラスト風に生成されるようにプロンプト調整
    """)
st.title("テキスト→画像 / 最新モデル画像生成デモ")

with st.sidebar:
    st.header("⚙️ 生成オプション")
    prompt_ja_0 = st.text_area("プロンプト（日本語OK）", height=150,
                               value="子供の男の子が寝る前にお母さんから絵本を読み聞かせられながら眠っている")
    # prompt_jaにデフォルトで追加するプロンプト
    prompt_ja = "漫画風のアニメスタイル、鮮やかで飽和した色彩、ダイナミックな照明効果、小学生向けの漫画風イラスト" + prompt_ja_0 + \
        "漫画のような表現、鮮やかで彩度の高い色彩、ダイナミックな照明効果など、漫画にインスパイアされたアニメスタイルで描かれ、ソフトで子供向けの美的感覚（小学生向け）を備えている。"
    negative_prompt = st.text_input(
        "Negative prompt (任意)", "", help="生成したくない要素を指定")
    image_size = st.selectbox("Image size",
                              ["square_hd", "square", "portrait_4_3", "portrait_16_9",
                               "landscape_4_3", "landscape_16_9"], index=4, help="画像サイズ")
    steps = st.slider("num_inference_steps", 10, 60, 28, help="推論ステップ数")
    guidance_scale = st.slider(
        "guidance_scale (CFG)", 1.0, 10.0, 5.0, 0.1, help="モデルが画像を生成する際に、どの程度プロンプトに忠実に従うかを示す尺度です。デフォルト値：5")
    num_images = st.slider("num_images", 1, 4, 1, help="生成する画像の数")
    seed = st.number_input("Seed (0 でランダム)", value=0, step=1,
                           help="シード値を指定すると、同じプロンプトで同じ画像が生成されます。0 を指定するとランダムなシード値が使用されます。")
    safety = st.checkbox("enable_safety_checker", value=True,
                         help="生成された画像に対して安全性チェックを行うかどうかを指定します。")
    output_fmt = st.selectbox("output_format", ["jpeg", "png"], index=0)

# -------------------------------------------------------
# 2. 生成リクエスト
# -------------------------------------------------------
if st.button("🚀 画像を生成する"):
    prompt_en = translate_prompt_to_english(prompt_ja)

    args = {
        "prompt": prompt_en,
        "negative_prompt": negative_prompt,
        "image_size": image_size,
        "num_inference_steps": steps,
        "guidance_scale": guidance_scale,
        "num_images": num_images,
        "enable_safety_checker": safety,
        "output_format": output_fmt,
        "sync_mode": True,
    }
    if seed:
        args["seed"] = int(seed)

    with st.spinner("画像を生成中…"):
        result = fal_client.subscribe(
            "fal-ai/hidream-i1-full",      # ★エンドポイント変更
            arguments=args,
            with_logs=False,
        )

    for i, img in enumerate(result["images"]):
        st.image(img["url"], caption=f"Image {i+1}")
        st.download_button(
            label="Download",
            data=img["url"],
            file_name=f"image_{i+1}.{output_fmt}",
            mime=f"image/{output_fmt}",
        )
    st.success("画像生成完了！")
