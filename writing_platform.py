import streamlit as st
import time
from datetime import datetime
import pandas as pd
from io import BytesIO
from streamlit_autorefresh import st_autorefresh

# セッション初期化
default_states = {
    "step": 0,
    "name": "",
    "student_id": "",
    "brainstorm_text": "",
    "pretest_text": "",
    "wcf_text": "",
    "wl_text": "",
    "posttest_text": "",
    "finished": False,
    "brainstorm_timer_started": False,
    "pretest_timer_started": False,
    "posttest_timer_started": False,
    "brainstorm_start_time": None,
    "pretest_start_time": None,
    "posttest_start_time": None,
    "wl_start_time": None,
    "brainstorm_elapsed": 0,
    "pretest_elapsed": 0,
    "wl_elapsed": 0,
    "posttest_elapsed": 0
}
for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.set_page_config(layout="wide")
st.title("L2 Writing Platform")

# Step 0: 学習者情報入力
if st.session_state.step == 0:
    st.subheader("学習者情報を入力してください")
    st.session_state.name = st.text_input("名前：", value=st.session_state.name)
    st.session_state.student_id = st.text_input("学籍番号：", value=st.session_state.student_id)
    if st.button("次へ (① ブレインストーミング)"):
        if st.session_state.name.strip() and st.session_state.student_id.strip():
            st.session_state.step = 1
        else:
            st.warning("名前と学籍番号の両方を入力してください。")

# Step 1: ブレインストーミング
elif st.session_state.step == 1:
    st.subheader("① ブレインストーミング (10分)")
    st_autorefresh(interval=1000, key="refresh1")
    if not st.session_state.brainstorm_timer_started:
        if st.button("タイマーを開始 (10分)"):
            st.session_state.brainstorm_timer_started = True
            st.session_state.brainstorm_start_time = time.time()
    else:
        elapsed = time.time() - st.session_state.brainstorm_start_time
        remaining = max(0, 600 - int(elapsed))
        mins, secs = divmod(remaining, 60)
        st.info(f"⏳ 残り時間: {mins:02d}:{secs:02d}")
        st.session_state.brainstorm_elapsed = int(elapsed)

    st.session_state.brainstorm_text = st.text_area(
        "自由にアイデアを書いてください:",
        value=st.session_state.brainstorm_text,
        height=300,
        disabled=not st.session_state.brainstorm_timer_started
    )
    if st.button("次へ (② Pre-Test)"):
        st.session_state.step = 2

# Step 2: Pre-Test
elif st.session_state.step == 2:
    st.subheader("② Writing Pre-Test (30分)")
    
    # 自動リフレッシュ：30秒以内の実行ごとに再描画
    count = st_autorefresh(interval=1000, key="refresh2", limit=None)

    if not st.session_state.pretest_timer_started:
        if st.button("タイマーを開始 (30分)"):
            st.session_state.pretest_timer_started = True
            st.session_state.pretest_start_time = time.time()
    else:
        if st.session_state.pretest_start_time is not None:
            elapsed = time.time() - st.session_state.pretest_start_time
            remaining = max(0, 1800 - int(elapsed))
            mins, secs = divmod(remaining, 60)
            st.info(f"残り時間: {mins:02d}:{secs:02d}")
            st.session_state.pretest_elapsed = int(elapsed)

    # 横並び：左にブレインストーミング、右に英作文
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div style='
                font-weight: bold;
                font-size: 24px;
                margin-bottom: 31px;
                line-height: 1.3;
            '>ブレインストーミングの内容</div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style='
                height: 350px;
                padding: 0px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: white;
                overflow-y: auto;
                font-family: sans-serif;
                font-size: 16px;
                line-height: 1.5;
                white-space: pre-wrap;
                box-sizing: border-box;
            '>
                {st.session_state.brainstorm_text.replace('<', '&lt;').replace('>', '&gt;').replace('\n','<br>')}
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div style='
                font-weight: bold;
                font-size: 24px;
                margin-bottom: 4px;
                line-height: 1.3;
            '>英作文を書いてください：</div>
            """,
            unsafe_allow_html=True
        )
        st.session_state.pretest_text = st.text_area(
            label=" ",  # ラベル行の隙間をなくす
            value=st.session_state.pretest_text,
            height=350,
            disabled=not st.session_state.pretest_timer_started
        )
        st.markdown(
            f"<div style='margin-top: -4px;'>単語数: {len(st.session_state.pretest_text.split())} / 文字数: {len(st.session_state.pretest_text)}</div>",
            unsafe_allow_html=True
        )

    if st.button("次へ (③ Model text)"):
        st.session_state.step = 3

# Step 3: Model text
elif st.session_state.step == 3:
    st.subheader("③ Model text")

    # 固定の英語モデル文
    model_text = """Model Reformulation:

Many young people in the United States actively participate in volunteer work, 
often joining local community programs or school-based activities. 
In contrast, Japanese youth tend to have fewer opportunities to engage in volunteering, 
which may be due to differences in cultural expectations, educational systems, 
and the availability of volunteer organizations. 
This suggests that social and institutional factors play a major role in shaping 
how young people in different countries contribute to their communities."""

    # 初回だけセッションに保存
    if st.session_state.wcf_text == "":
        st.session_state.wcf_text = model_text

    st.markdown("#### Model text")
    st.markdown(
        f"""
        <div style='height:300px; overflow-y:auto; padding:10px;
        border:1px solid #ccc; border-radius:5px; background-color:white;'>
        {st.session_state.wcf_text.replace('\n','<br>')}
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("次へ (④ Written Language)"):
        st.session_state.step = 4


# Step 4: WL
elif st.session_state.step == 4:
    st.subheader("④ Written Language with Model text")
    st.markdown("### 振り返り")
    if st.session_state.wl_start_time is None:
        st.session_state.wl_start_time = time.time()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 元の文 (Pre-Test)")
        st.markdown(
            f"<div style='height:300px; overflow-y:auto; padding:10px; border:1px solid #ccc; border-radius:5px; background-color:white;'>{st.session_state.pretest_text.replace(chr(10), '<br>')}</div>",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown("#### Model text")
        st.markdown(
            f"<div style='height:300px; overflow-y:auto; padding:10px; border:1px solid #ccc; border-radius:5px; background-color:white;'>{st.session_state.wcf_text.replace(chr(10), '<br>')}</div>",
            unsafe_allow_html=True
        )
    st.markdown("#### 考えたこと・気づいたこと")
    st.session_state.wl_text = st.text_area(
        "フィードバックと自身の文を比較し、考えたことや気づいたことを書いてください。",
        value=st.session_state.wl_text,
        height=200,
        disabled=st.session_state.wl_start_time is None
    )
    st.session_state.wl_elapsed = int(time.time() - st.session_state.wl_start_time)
    if st.button("次へ (⑤ Post-Test)"):
        st.session_state.step = 5

# Step 5: Post-Test
elif st.session_state.step == 5 and not st.session_state.finished:
    st.subheader("⑤ Writing Post-Test (30分)")
    st_autorefresh(interval=1000, key="refresh5")
    if not st.session_state.posttest_timer_started:
        if st.button("タイマーを開始 (30分)"):
            st.session_state.posttest_timer_started = True
            st.session_state.posttest_start_time = time.time()
    else:
        elapsed = time.time() - st.session_state.posttest_start_time
        remaining = max(0, 1800 - int(elapsed))
        mins, secs = divmod(remaining, 60)
        st.info(f"残り時間: {mins:02d}:{secs:02d}")
        st.session_state.posttest_elapsed = int(elapsed)
    st.session_state.posttest_text = st.text_area(
        "英作文を書いてください：",
        value=st.session_state.posttest_text,
        height=300,
        disabled=not st.session_state.posttest_timer_started
    )
    st.markdown(f"単語数: {len(st.session_state.posttest_text.split())} / 文字数: {len(st.session_state.posttest_text)}")
    if st.button("完了"):
        st.session_state.finished = True

# 完了ページ
elif st.session_state.finished:
    st.success("すべてのステップが完了しました。お疲れ様でした！")

    def generate_excel():
        df = pd.DataFrame({
            "名前": [st.session_state.name],
            "学籍番号": [st.session_state.student_id],
            "① Brainstorming": [st.session_state.brainstorm_text],
            "② Pre-Test": [st.session_state.pretest_text],
            "③ Model text": [st.session_state.wcf_text],
            "④ Reflection": [st.session_state.wl_text],
            "⑤ Post-Test": [st.session_state.posttest_text],
            "Brainstorm(sec)": [st.session_state.brainstorm_elapsed],
            "Pre-Test(sec)": [st.session_state.pretest_elapsed],
            "Reflection(sec)": [st.session_state.wl_elapsed],
            "Post-Test(sec)": [st.session_state.posttest_elapsed],
            "Pre-Test(words)": [len(st.session_state.pretest_text.split())],
            "Post-Test(words)": [len(st.session_state.posttest_text.split())]
        })
        out = BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Writing Session")
        return out.getvalue()

    st.download_button(
        label="結果をExcelでダウンロード",
        data=generate_excel(),
        file_name=f"writing_result_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.caption("© 2025 Writing Platform by Atsushi Doi")