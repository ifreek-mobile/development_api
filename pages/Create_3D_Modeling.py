import tempfile
import os
import io
import base64
import requests
import streamlit as st
import streamlit_3d as st3d
import fal_client

# ───────────────────────────────────
# 1. UI
# ───────────────────────────────────
with st.expander("✏️ 補足情報の表示（クリックで展開）", expanded=False):
    st.write("""
    - 1 回の3D生成あたり約 60 円です。
    - 生成時間が2分から3分程度かかります。画面の更新など行うと表示されません。
    """)

st.title("3Dモデル変換 / 画像→3D生成デモ")

quality = st.selectbox("品質",     [
                       "high", "medium", "low"], index=1, help="high: 高品質、medium: 中品質、low: 低品質")
material = st.selectbox("マテリアル", ["PBR", "Shaded"], index=0,
                        help="PBR: リアリスティックな質感・物理ベース表現、Shaded: 軽量レンダリング・シンプルな陰影表現")

uploaded_imgs = st.file_uploader(
    "参照画像（複数可、推奨: マルチビュー）",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
)

if st.button("3Dモデルを生成") and (uploaded_imgs):
    if "FAL_KEY" not in os.environ:
        st.error("環境変数 FAL_KEY が設定されていません")
        st.stop()

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
    st3d.streamlit_3d(model=glb_url, height=600)

    # テクスチャ表示（任意）
    if result.get("textures"):
        st.subheader("生成テクスチャ")
        for tex in result["textures"]:
            st.image(tex["url"], caption=tex["file_name"])
