# streamlit_app.py
import os
import streamlit as st
import fal_client
from openai import OpenAI

# -------------------------------------------------------
# 0. 事前チェック: API キー
# -------------------------------------------------------
if os.getenv("FAL_KEY") is None:
    st.error("環境変数 FAL_KEY が設定されていません。")
    st.stop()

# OpenAI 用クライアント（翻訳に使用）
openai_client = OpenAI()   # OPENAI_API_KEY は環境変数利用


def translate_prompt_to_english(text: str) -> str:
    """日本語プロンプトを英語に翻訳して返す。空文字ならそのまま返却。"""
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
# 1. ページ設定
# -------------------------------------------------------
st.set_page_config(page_title="絵本のイラスト学習モデル", page_icon="🖼️")
st.title("テキスト→画像生成 / イラスト学習モデルデモ")

# -------------------------------------------------------
# 2. Sidebar – 生成パラメータ
# -------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 生成オプション")

    prompt_ja = st.text_area(
        "プロンプト（日本語OK）",
        value="子供の男の子が寝る前にお母さんから絵本を読み聞かせられながら眠っている",
        height=150,
        help="日本語で自由に記述。送信時に自動英訳されます。",
    )
    with st.popover("ℹ️ プロンプトの説明"):
        st.markdown(
            "日本語・英語どちらでも入力できますが、送信前に英語へ変換されます。"
        )

    image_size = st.selectbox(
        "Image size",
        ["square_hd", "square", "portrait_4_3", "portrait_16_9",
         "landscape_4_3", "landscape_16_9"],
        index=4,
        help="出力アスペクト比を選択。HD はより高解像度。"
    )
    with st.popover("ℹ️ Image size の説明"):
        st.markdown("HD 付きは 1024×1024 相当。解像度が高いほど時間とクレジットを消費します。")

    steps = st.slider(
        "num_inference_steps", 10, 60, 28,
        help="ステップ数。多いほど高品質／遅延増。"
    )
    guidance_scale = st.slider(
        "guidance_scale (CFG)", 1.0, 10.0, 3.5, 0.1,
        help="大きいほどプロンプトへ忠実。3〜7 が目安。"
    )
    num_images = st.slider(
        "num_images", 1, 4, 1,
        help="一度に生成する枚数。最大4枚。"
    )
    seed = st.number_input(
        "Seed (0 でランダム)", value=0, step=1,
        help="同じ Seed と英訳後プロンプトで再現可能。"
    )
    safety = st.checkbox(
        "enable_safety_checker", value=True,
        help="不適切な画像を自動検閲します。"
    )

    st.markdown("---")
    st.header("🎨 LoRA（任意）")
    lora_url = st.text_input(
        "LoRA URL",
        value="https://v3.fal.media/files/elephant/pHuYWSCeoDmtmKuz5ewcm_pytorch_lora_weights.safetensors",
        help=".safetensors または diffusers 形式の公開 URL。"
    )
    lora_scale = st.slider(
        "LoRA scale", 0.1, 1.5, 1.0, 0.1,
        help="LoRA 適用度。1.0 = フル、0.7 = 控えめ。"
    )

# -------------------------------------------------------
# 3. 生成ボタン
# -------------------------------------------------------
if st.button("🚀 画像を生成する"):
    # -- プロンプトを英訳 --
    prompt_en = translate_prompt_to_english(prompt_ja)

    args = {
        "prompt": prompt_en,
        "image_size": image_size,
        "num_inference_steps": steps,
        "guidance_scale": guidance_scale,
        "num_images": num_images,
        "enable_safety_checker": safety,
        "sync_mode": True,
    }
    if seed:
        args["seed"] = int(seed)
    if lora_url:
        args["loras"] = [{"path": lora_url, "scale": float(lora_scale)}]

    with st.spinner("画像を生成中…"):
        result = fal_client.subscribe(
            "fal-ai/flux-lora",
            arguments=args,
            with_logs=False,
        )

    for i, img in enumerate(result["images"]):
        st.image(img["url"], caption=f"Image {i+1}")
