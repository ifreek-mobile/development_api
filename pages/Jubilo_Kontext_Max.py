# app.py
import os
import tempfile
from pathlib import Path
import requests
import streamlit as st
import fal_client

###############################################################################
# Configuration
###############################################################################
MODEL_ID = "fal-ai/flux-pro/kontext/max/multi"

# スタイルごとに完全なプロンプトテンプレートを定義

STYLE_PROMPTS = {
    "アニメ": """Create a Japanese anime-style illustration of a scene of a child in a close-up uniform, resembling the face of the {gender} in the close-up, dribbling in soccer!
    The background is a soccer field.

    Uniform features
    - Three stars on the left shoulder
    - Emblem on the left chest
    - The word YAMAHA in the middle
    - Light blue, dark blue and white uniform""",
    "絵本": """Create a vibrant, distinctly two-dimensional children's picture-book style illustration depicting a cheerful scene of a child in a soccer uniform, closely resembling the face of the {gender} in the close-up, happily dribbling a soccer ball!

    The background features a brightly colored, simplified soccer field, with clear, flat, playful visuals typical of children's picture books.

    Uniform features:
    - Three stars clearly visible on the left shoulder
    - Simple emblem on the left chest
    - The word YAMAHA clearly readable in the center
    - Clearly defined uniform colors: light blue, dark blue, and white

    Illustration style strongly emphasizes:
    - Flat, vivid colors
    - Bold, simplified outlines
    - Whimsical, friendly expressions and movements
    - Clear, easily recognizable shapes ideal for children's book illustrations""",
    "クレヨン": """Create a joyful, two-dimensional **crayon-style** children's picture-book illustration showing a close-up scene of a child in a soccer uniform, closely resembling the face of the {gender} in the close-up, enthusiastically dribbling a soccer ball!

    The background is a colorful, simply drawn soccer field, illustrated as if by crayon strokes.

    Uniform features clearly illustrated with crayon textures:

    - Three stars prominently placed on the left shoulder
    - Simple emblem drawn on the left chest
    - The word "YAMAHA" written clearly in the center
    - Colors clearly presented in crayon strokes: light blue, dark blue, and white

    Illustration style strongly emphasizes:
    - Distinct crayon-textured lines and fills
    - Bright, playful, and slightly rough texture
    - Warm, handmade, and friendly visuals suitable for children's enjoyment""",
    "コミック": """Create a lively, two-dimensional **comic-style** children's picture-book illustration showing a dynamic close-up scene of a child in a soccer uniform, closely resembling the face of the {gender} in the close-up, energetically dribbling a soccer ball!

    The background is a bright, simplified soccer field with comic-style effects like action lines and expressive motion marks to emphasize movement and excitement.

    Uniform features clearly illustrated:
    - Three bold stars on the left shoulder
    - A stylized emblem on the left chest
    - The word "YAMAHA" prominently displayed in the center
    - Vivid uniform colors: light blue, dark blue, and white

    Illustration style emphasizes:
    - Clean, bold outlines and high contrast
    - Expressive facial features and exaggerated motion
    - Comic-style elements such as dynamic poses.""",
    "デフォルメ": """Create a charming, two-dimensional **deformed (chibi)-style** children's picture-book illustration featuring a close-up scene of a child in a soccer uniform, with an exaggeratedly cute face resembling the {gender} in the close-up, happily dribbling a soccer ball!

    The background is a cheerful, simplified soccer field with playful elements to match the chibi style.

    Uniform features are clearly visible in a cute, stylized form:
    - Three small stars on the left shoulder
    - A simplified emblem on the left chest
    - The word "YAMAHA" clearly written in a fun, rounded font at -he center
    - Light blue, dark blue, and white colors in a soft, vivid palette

    Illustration style emphasizes:
    - Oversized head and expressive, sparkling eyes
    - Small, rounded body proportions
    - Bright colors, soft shading, and an overall adorable, whimsical atmosphere perfect for young children""",
}

# ▼ ここを書き換えてローカル or URL を指定
PRESET_IMAGES = [
    "style/IMG_6900.jpg",
    "style/IMG_6902.jpeg",
]

###############################################################################
# API Key
###############################################################################
FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    st.error("環境変数 FAL_KEY が設定されていません。 export FAL_KEY=... してください。")
    st.stop()

os.environ["FAL_KEY"] = FAL_KEY  # fal_client uses env var

###############################################################################
# Helper: convert preset entries → HTTP URLs guaranteed
###############################################################################


@st.cache_resource(show_spinner=False)
def resolve_preset_urls(preset_entries):
    """Ensure every entry is an http/https URL accessible by fal.ai."""
    urls = []
    script_dir = Path(__file__).parent
    cwd_dir = Path.cwd()

    for entry in preset_entries:
        # 1) If already URL
        if str(entry).startswith("http"):
            try:
                if requests.head(entry, timeout=5).status_code == 200:
                    urls.append(entry)
                    continue
                st.warning(f"URL にアクセスできないためアップロードします: {entry}")
            except Exception:
                st.warning(f"URL チェック失敗、アップロードに切替: {entry}")

        # 2) Local file resolution
        raw_path = Path(entry)
        candidate_paths = [
            raw_path if raw_path.is_absolute() else None,
            (script_dir / raw_path) if not raw_path.is_absolute() else None,
            (script_dir.parent / raw_path) if not raw_path.is_absolute() else None,
            (cwd_dir / raw_path) if not raw_path.is_absolute() else None,
        ]
        path_found = None
        for cand in filter(None, candidate_paths):
            if cand.exists():
                path_found = cand
                break
        if path_found is None:
            st.error(
                "事前画像が見つかりません:\n  • 試したパス: " +
                ", ".join(str(p) for p in filter(None, candidate_paths))
            )
            st.stop()
        try:
            upload_result = fal_client.upload_file(str(path_found))
            url = upload_result.get("url") if isinstance(
                upload_result, dict) else str(upload_result)
            urls.append(url)
        except Exception as e:
            st.error(f"画像アップロードに失敗しました: {e}")
            st.stop()
    return urls


PRESET_IMAGE_URLS = resolve_preset_urls(PRESET_IMAGES)

###############################################################################
# UI
###############################################################################
st.set_page_config(page_title="ジュビロ用画像生成", page_icon="🖼️")
with st.expander("✏️ 補足情報の表示（クリックで展開）", expanded=False):
    st.write("""
    - 1 回の画像生成あたり約 12 円です。
    - 画像と性別、生成スタイルを選択して「生成する」を押すと、画像が生成されます。
    - 生成された画像はダウンロードできます。
    """)
st.title("画像生成デモ (fal.ai Kontext Max)")

uploaded_file = st.file_uploader(
    "顔画像をアップロード", type=["jpg", "jpeg", "png", "webp"])

gender_jp = st.radio("性別を選択してください", ["男の子", "女の子"], horizontal=True)
gender_en = "boy" if gender_jp == "男の子" else "girl"

style_choice = st.selectbox("生成スタイルを選択してください", list(STYLE_PROMPTS.keys()))

run = st.button("生成する", type="primary")

###############################################################################
# Inference
###############################################################################
if run:
    if uploaded_file is None:
        st.error("顔画像をアップロードしてください。")
        st.stop()

    # Upload user image
    with st.spinner("アップロード中…"):
        suffix = Path(uploaded_file.name).suffix or ".png"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name
        try:
            up_result = fal_client.upload_file(tmp_path)
            user_url = up_result["url"] if isinstance(
                up_result, dict) else str(up_result)
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    # Compose prompt (style template already includes {gender})
    prompt = STYLE_PROMPTS[style_choice].format(gender=gender_en)

    args = {
        "prompt": prompt,
        "image_urls": [user_url] + PRESET_IMAGE_URLS,
        "num_images": 1,
        "aspect_ratio": "9:16",
        "output_format": "jpeg",
    }

    with st.spinner("画像を生成しています…"):
        try:
            result = fal_client.subscribe(
                MODEL_ID, arguments=args, with_logs=True)
        except Exception as e:
            st.error(f"生成に失敗しました: {e}")
            st.stop()

    try:
        first_img = result["images"][0]
        gen_url = first_img["url"] if isinstance(
            first_img, dict) else first_img
        gen_data = requests.get(gen_url, timeout=30).content
    except Exception as e:
        st.error(f"生成結果の取得に失敗しました: {e}")
        st.stop()

    st.success("画像生成が完了しました！")
    st.image(gen_data, caption="生成結果", use_container_width=True)
    st.download_button("ダウンロード", gen_data,
                       file_name="generated.jpeg", mime="image/jpeg")
