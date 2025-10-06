import streamlit as st

from model.High_and_Low import load_sample_game

st.title("High and Low")


def ensure_game() -> None:
    if "highlow_game" not in st.session_state:
        st.session_state.highlow_game = load_sample_game()
        st.session_state.game_started = False
        st.session_state.last_result = None


def reset_game() -> None:
    st.session_state.highlow_game.reset()
    st.session_state.game_started = False
    st.session_state.last_result = None
    st.rerun()


ensure_game()
game = st.session_state.highlow_game

if not st.session_state.game_started:
    st.write(f"開始前の所持チップ: {game.initial_chips}枚")
    st.info("Startボタンを押すとサンプルデータに従ってゲームが進行します。")
    if st.button("Start"):
        game.reset()
        st.session_state.game_started = True
        st.rerun()
    st.stop()

st.metric("所持チップ", f"{game.chips} 枚")

last_result = st.session_state.last_result
if last_result:
    delta = last_result["delta"]
    if delta > 0:
        notify = st.success
        delta_text = f"+{delta}"
    elif delta < 0:
        notify = st.error
        delta_text = str(delta)
    else:
        notify = st.info
        delta_text = "±0"

    notify(
        f"ラウンド{last_result['round']} 結果: {last_result['outcome'].upper()} "
        f"(結果カード: {last_result['result_card']})\n"
        f"チップ変動: {delta_text} → 現在: {last_result['chips_after']}枚"
    )

if game.is_finished:
    st.success("全3ラウンド終了！")
    st.write(f"最終所持チップ: {game.chips}枚")
    if game.history:
        st.dataframe(game.history, use_container_width=True)
    if st.button("リセット"):
        reset_game()
    st.stop()

if game.chips <= 0:
    st.error("チップが残っていません。リセットしてください。")
    if st.button("リセット", key="reset_no_chips"):
        reset_game()
    st.stop()

current_round = game.current_round
if current_round is None:
    st.stop()

st.subheader(f"ラウンド {game.round_number} / {game.total_rounds}")
base_card = game.expose_base_card()
st.write(f"ベースカード: {base_card}")
remaining_cards = ", ".join(map(str, game.deck)) if game.deck else "なし"
st.write(f"残り札: {remaining_cards}")

max_bet = int(game.chips)
default_bet = min(10, max_bet) if max_bet > 0 else 1

with st.form("round_form", clear_on_submit=False):
    bet_value = st.number_input(
        "ベットするチップ数",
        min_value=1,
        max_value=max(max_bet, 1),
        value=default_bet,
        step=1,
        format="%d",
    )
    choice = st.radio("HighかLowかを選んでください", ("High", "Low"), horizontal=True)
    submitted = st.form_submit_button("結果を見る")

if submitted:
    try:
        result = game.play_round(choice, int(bet_value))
    except ValueError as exc:
        st.error(str(exc))
    else:
        st.session_state.last_result = result
        st.rerun()

if game.history:
    st.divider()
    st.write("これまでの結果")
    st.dataframe(game.history, use_container_width=True)

if st.button("リセット", key="reset_bottom"):
    reset_game()
