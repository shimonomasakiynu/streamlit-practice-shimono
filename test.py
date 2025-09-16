import streamlit as st

qp = st.query_params
round_num = int(qp.get("round", "1"))  # なければ 1
st.write(f"現在のラウンド: {round_num}")

if st.button("次のラウンドへ"):
    round_num += 1
    st.query_params["round"] = str(round_num)  # URLを更新
    st.write(f"次のラウンドは {round_num} です")


# import streamlit as st

# # 初期化
# if "count" not in st.session_state:
#     st.session_state.count = 0

# # 更新
# if st.button("カウントアップ"):
#     st.session_state.count += 1

# # 表示
# st.write("カウント:", st.session_state.count)

# import streamlit as st
# count = 0
# if st.button("カウントアップ"):
#     count += 1
# st.write("カウント:", count)