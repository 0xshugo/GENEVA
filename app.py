"""Streamlit user interface for the GENEVA toolkit."""

from __future__ import annotations

from typing import List

from PIL import Image
import streamlit as st

from src import image_check, text_check

st.set_page_config(page_title="GENEVA – Generative Ethics Validator", layout="wide")
st.title("GENEVA – Generative Ethics Validator")

text_tab, image_tab = st.tabs(["Text Check", "Image Check"])

with text_tab:
    st.header("Textual Similarity & Repetition")
    st.write(
        "提供された文章と参照文の類似度をTF-IDFコサイン類似度で計測し、"
        "さらに繰り返し度合いを示すAIリピティションスコアを算出します。"
    )

    submission = st.text_area(
        "検査対象の文章",
        value="The quick brown fox jumps over the lazy dog. The quick brown fox repeats.",
        height=180,
    )
    reference_input = st.text_area(
        "参照文（空行で区切ると複数登録できます）",
        value=(
            "A fast brown fox leaps across a sleepy canine.\n\n"
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        ),
        height=180,
    )

    references: List[str] = [part.strip() for part in reference_input.split("\n\n") if part.strip()]

    with st.expander("詳細設定", expanded=False):
        ngram_min, ngram_max = st.slider(
            "TF-IDF n-gram範囲",
            min_value=1,
            max_value=5,
            value=(1, 2),
            help="ベクトル化に使用するn-gramの下限と上限を設定します。",
        )
        repetition_ngram = st.slider(
            "AIリピティション n-gram長",
            min_value=1,
            max_value=10,
            value=3,
            help="繰り返し検出に用いるトークン長を指定します。",
        )
        phrase_limit = st.slider(
            "繰り返しフレーズの最大表示件数",
            min_value=0,
            max_value=20,
            value=5,
            help="上位何件の繰り返しフレーズをJSONに含めるか選択します。0で非表示。",
        )
        show_all = st.checkbox("すべての繰り返しフレーズを表示", value=False)

    if submission.strip() and references:
        try:
            analysis = text_check.analyse_submission(
                submission,
                references,
                ngram_range=(ngram_min, ngram_max),
                repetition_ngram_size=repetition_ngram,
                repetition_phrase_limit=None if show_all else phrase_limit,
            )
        except ValueError as err:
            st.error(str(err))
        else:
            st.subheader("解析結果")
            st.json(analysis.to_dict())
            if analysis.repeated_phrases:
                st.markdown("#### 繰り返しフレーズ上位")
                st.table(analysis.repeated_phrases)
    else:
        st.info("文章と参照文を入力すると解析が行われます。")

with image_tab:
    st.header("Image pHash Similarity")
    st.write("2枚の画像をアップロードして、pHashベースの類似度を算出します。")

    col1, col2 = st.columns(2)
    with col1:
        file_a = st.file_uploader("画像A", type=["png", "jpg", "jpeg", "webp", "bmp"], key="image_a")
    with col2:
        file_b = st.file_uploader("画像B", type=["png", "jpg", "jpeg", "webp", "bmp"], key="image_b")

    if file_a and file_b:
        image_a = Image.open(file_a)
        image_b = Image.open(file_b)

        hash_a = image_check.phash(image_a)
        hash_b = image_check.phash(image_b)
        similarity = image_check.hash_similarity(hash_a, hash_b)
        result = {
            "similarity": similarity,
            "hash_a": image_check.hash_to_bits(hash_a),
            "hash_b": image_check.hash_to_bits(hash_b),
        }

        st.subheader("解析結果")
        st.json(result)

        preview_col1, preview_col2 = st.columns(2)
        with preview_col1:
            st.image(image_a, caption="画像A", use_column_width=True)
        with preview_col2:
            st.image(image_b, caption="画像B", use_column_width=True)
    else:
        st.info("両方の画像をアップロードすると類似度が表示されます。")
