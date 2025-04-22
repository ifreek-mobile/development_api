import tempfile
import os
import io
import base64
import requests
import streamlit as st
import streamlit_3d as st3d
import fal_client
from openai import OpenAI                 # ★① 追加

# OpenAI 翻訳用クライアント           # ★② 追加
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI()


def translate_prompt_to_english(text: str) -> str:      # ★③ 追加
    """日本語 → 英語翻訳（空文字ならそのまま返す）"""
    if not text:
        return ""
    resp = client.chat.completions.create(
        model="gpt-4.1-nano-2025-04-14",
        messages=[
            {"role": "system", "content": "You are a helpful translator."},
            {"role": "user",
             "content": f"次の日本語を英語に翻訳してください: 「{text}」"}
        ],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()


# ───────────────────────────────────
# 1. UI
# ───────────────────────────────────
st.title("画像→3D / 3Dモデル生成デモ")

prompt_ja = st.text_input("プロンプト（日本語入力可）", "猫の着ぐるみを着た子ども")
quality = st.selectbox("品質",     ["high", "medium", "low"], index=1)
material = st.selectbox("マテリアル", ["PBR", "Shaded"],        index=0)

uploaded_imgs = st.file_uploader(
    "参照画像（複数可、推奨: マルチビュー）",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
)

if st.button("3Dモデルを生成") and (prompt_ja or uploaded_imgs):
    if "FAL_KEY" not in os.environ:
        st.error("環境変数 FAL_KEY が設定されていません")
        st.stop()

    # ★④ 変更: 日本語→英語翻訳
    prompt_en = translate_prompt_to_english(prompt_ja)

    with st.spinner("3D変換リクエスト送信中…"):
        # 2‑A. 画像アップロード
        image_urls = []
        for img in uploaded_imgs:
            with tempfile.NamedTemporaryFile(delete=False,
                                             suffix=os.path.splitext(img.name)[1]) as tmp:
                tmp.write(img.getbuffer())
                url = fal_client.upload_file(tmp.name)
            image_urls.append(url)

        # 2‑B. Rodin へリクエスト
        args = {
            "prompt": prompt_en,           # ← 英語化済みを渡す
            "input_image_urls": image_urls,
            "geometry_file_format": "glb",
            "quality": quality,
            "material": material,
            "tier": "Regular",
        }

        def _log(update):
            if isinstance(update, fal_client.InProgress):
                for l in update.logs:
                    st.write(l["message"])

        result = fal_client.subscribe(
            "fal-ai/hyper3d/rodin",
            arguments=args,
            with_logs=True,
            on_queue_update=_log,
        )

    # ───────────────────────────────────
    # 3. Viewer へ表示
    # ───────────────────────────────────
    glb_url = result["model_mesh"]["url"]
    st.success(f"GLB 生成完了: {glb_url.split('/')[-1]}")

    st.info("モデルを読み込み中…")
    bin_data = requests.get(glb_url).content
    data_uri = "data:model/gltf-binary;base64," + \
        base64.b64encode(bin_data).decode()
    st3d.streamlit_3d(model=data_uri, height=600)

    # テクスチャ表示（任意）
    if result.get("textures"):
        st.subheader("生成テクスチャ")
        for tex in result["textures"]:
            st.image(tex["url"], caption=tex["file_name"])
