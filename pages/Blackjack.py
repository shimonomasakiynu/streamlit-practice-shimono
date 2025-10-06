import streamlit as st

from model.blackjack import BlackjackGame

st.title("ブラックジャック")

SUIT_LABELS = {
    "Spades": "スペード",
    "Hearts": "ハート",
    "Diamonds": "ダイヤ",
    "Clubs": "クラブ",
}

RANK_LABELS = {
    "A": "A (エース)",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "10": "10",
    "J": "J (ジャック)",
    "Q": "Q (クイーン)",
    "K": "K (キング)",
}

OUTCOME_MESSAGES = {
    "player_blackjack": "ブラックジャック！ あなたの勝利です。",
    "player_win": "あなたの勝ちです。",
    "dealer_bust": "ディーラーがバーストしました。あなたの勝ちです。",
    "push": "プッシュ（引き分け）。ベットは返却されます。",
    "player_bust": "あなたがバーストしました。",
    "dealer_win": "ディーラーの勝利です。",
    "dealer_blackjack": "ディーラーがブラックジャックです。",
}

OUTCOME_LABELS = {
    "player_blackjack": "ブラックジャック (勝ち)",
    "player_win": "勝ち",
    "dealer_bust": "勝ち (ディーラーがバースト)",
    "push": "引き分け",
    "player_bust": "負け (バースト)",
    "dealer_win": "負け",
    "dealer_blackjack": "負け (ディーラーのBJ)",
}

OUTCOME_STATUS = {
    "player_blackjack": st.success,
    "player_win": st.success,
    "dealer_bust": st.success,
    "push": st.info,
    "player_bust": st.error,
    "dealer_win": st.error,
    "dealer_blackjack": st.error,
}

ERROR_MESSAGES = {
    "Bet must be a positive integer": "ベット額は1以上の整数を入力してください。",
    "Bet cannot exceed current chips": "所持チップを超えるベットはできません。",
    "Round already in progress": "ラウンド進行中です。結果が出るまでお待ちください。",
    "Hit is only available during the player turn": "ヒットできるのはプレイヤーの手番だけです。",
    "Stand is only available during the player turn": "スタンドできるのはプレイヤーの手番だけです。",
    "Next round can only start after the current round ends": "現在のラウンドが終了してから次のラウンドを開始してください。",
}


def ensure_game() -> None:
    if "blackjack_game" not in st.session_state:
        st.session_state.blackjack_game = BlackjackGame()
        st.session_state.blackjack_message = None
    if "blackjack_message" not in st.session_state:
        st.session_state.blackjack_message = None


def translate_error(message: str) -> str:
    return ERROR_MESSAGES.get(message, message)


def card_label(card) -> str:
    suit = SUIT_LABELS.get(card.suit, card.suit)
    rank = RANK_LABELS.get(card.rank, card.rank)
    return f"{suit}の{rank}"


def to_japanese_label(label: str) -> str:
    if " of " not in label:
        return label
    rank, suit = label.split(" of ", 1)
    return f"{SUIT_LABELS.get(suit, suit)}の{RANK_LABELS.get(rank, rank)}"


def hand_text(cards) -> str:
    if not cards:
        return "なし"
    return "、".join(card_label(card) for card in cards)


def format_history_hand(card_labels, total: int) -> str:
    if not card_labels:
        return "なし"
    joined = "、".join(to_japanese_label(label) for label in card_labels)
    return f"{joined}（合計: {total}）"


ensure_game()
game: BlackjackGame = st.session_state.blackjack_game

col_chips, col_cards, col_reset = st.columns([1, 1, 1])
col_chips.metric("現在のチップ", f"{game.chips}")
col_cards.metric("山札の残り枚数", str(game.cards_remaining))
if col_reset.button("ゲームをリセット"):
    game.reset()
    st.session_state.blackjack_message = None
    st.rerun()

message = st.session_state.blackjack_message
if message:
    st.info(message)

if game.state == "BETTING":
    st.subheader("ベット額を決めてください")
    if game.is_bankrupt:
        st.error("チップがありません。ゲームをリセットして再挑戦してください。")
    else:
        max_bet = max(1, game.chips)
        default_bet = min(10, max_bet)
        with st.form("bet_form", clear_on_submit=True):
            bet_value = st.number_input(
                "ベット額",
                min_value=1,
                max_value=max_bet,
                value=default_bet,
                step=1,
                format="%d",
            )
            deal = st.form_submit_button("カードを配る")
        if deal:
            try:
                game.start_round(int(bet_value))
            except ValueError as exc:
                st.error(translate_error(str(exc)))
            else:
                st.session_state.blackjack_message = None
                st.rerun()

if game.state in {"PLAYER_TURN", "ROUND_OVER"}:
    st.subheader("ディーラー")
    if game.is_player_turn:
        upcard = game.dealer_upcard
        if upcard is None:
            st.write("-")
        else:
            st.write(f"{card_label(upcard)} と伏せ札1枚")
    else:
        st.write(hand_text(game.dealer_cards))
        st.caption(f"合計: {game.dealer_total}")

    st.subheader("あなたの手札")
    st.write(hand_text(game.player_cards))
    st.caption(f"合計: {game.player_total}")

if game.state == "PLAYER_TURN":
    action_hit, action_stand = st.columns(2)
    if action_hit.button("ヒット"):
        try:
            game.hit()
        except RuntimeError as exc:
            st.error(translate_error(str(exc)))
        st.rerun()
    if action_stand.button("スタンド"):
        try:
            game.stand()
        except RuntimeError as exc:
            st.error(translate_error(str(exc)))
        st.rerun()

if game.is_round_over:
    outcome = game.round_outcome
    status_fn = OUTCOME_STATUS.get(outcome, st.info)
    status_fn(OUTCOME_MESSAGES.get(outcome, "ラウンドが終了しました。"))

    record = game.last_record
    if record:
        delta = record["delta"]
        if delta > 0:
            delta_text = f"+{delta}"
        elif delta == 0:
            delta_text = "±0"
        else:
            delta_text = str(delta)
        st.write(
            f"ベット額: {record['bet']} / 収支: {delta_text} / 現在のチップ: {record['chips_after']}"
        )
        st.caption(
            f"あなた: {format_history_hand(record['player_cards'], record['player_total'])}"
            f" ｜ ディーラー: {format_history_hand(record['dealer_cards'], record['dealer_total'])}"
        )

    col_next, col_shuffle = st.columns([1, 1])
    if col_next.button("次のラウンドへ"):
        try:
            game.next_round()
        except RuntimeError as exc:
            st.error(translate_error(str(exc)))
        else:
            st.session_state.blackjack_message = None
            st.rerun()
    if col_shuffle.button("山札をリセット"):
        game.reset_shoe()
        st.session_state.blackjack_message = "次のディール時に山札をリセットします。"
        st.rerun()

if game.history:
    st.divider()
    st.subheader("プレイ履歴")
    history_rows = []
    for idx, entry in enumerate(game.history, start=1):
        history_rows.append(
            {
                "ラウンド": idx,
                "結果": OUTCOME_LABELS.get(entry["outcome"], entry["outcome"]),
                "ベット": entry["bet"],
                "収支": entry["delta"],
                "残りチップ": entry["chips_after"],
            }
        )
    st.table(history_rows)
