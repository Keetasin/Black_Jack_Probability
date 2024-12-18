def create_deck():
    """สร้างสำรับไพ่ 1 สำรับ"""
    deck = []
    for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']:
        deck.extend([rank] * 4)  # ไพ่แต่ละใบมี 4 ใบ
    return deck

def card_to_value(card):
    """แปลงไพ่จากตัวอักษรให้เป็นค่าตัวเลข"""
    if card in ['J', 'Q', 'K']:
        return 10
    elif card == 'A':
        return 11
    else:
        return int(card)

def calculate_total(hand):
    """คำนวณแต้มรวมของไพ่ในมือ"""
    total = sum(hand)
    aces = hand.count(11)  # จำนวน A ที่มีค่า 11
    while total > 21 and aces:
        total -= 10  # ลดค่า A จาก 11 เป็น 1
        aces -= 1
    return total

def calculate_bust_probability(hand, deck, stop_at=17):
    """
    คำนวณความน่าจะเป็นที่ไพ่ในมือจะ bust
    :param hand: ไพ่ในมือเป็นค่าตัวเลข (list)
    :param deck: สำรับไพ่ที่เหลืออยู่
    :param stop_at: แต้มที่หยุดจั่วไพ่ (default: 17)
    :return: ความน่าจะเป็นที่ bust
    """
    total = calculate_total(hand)
    if total >= stop_at:
        return 0.0  # ไม่จั่วไพ่เพิ่มเติม

    bust_count = 0
    for card in deck:
        card_value = card_to_value(card)
        if card == 'A':
            # พิจารณากรณีที่ A สามารถเป็น 1 หรือ 11
            new_total_with_11 = total + 11
            new_total_with_1 = total + 1
            if new_total_with_11 > 21 and new_total_with_1 > 21:
                bust_count += 1
        else:
            new_total = total + card_value
            if new_total > 21:
                bust_count += 1

    return bust_count / len(deck)

if __name__ == "__main__":
    # รับไพ่เริ่มต้นของเจ้ามือ
    input_cards = input("กรุณากรอกไพ่เริ่มต้นของเจ้ามือ (เช่น 'K 5' หรือ 'A 8'): ")
    dealer_cards = input_cards.upper().split()

    # รับไพ่ของผู้เล่น
    player_cards_input = input("กรุณากรอกไพ่ของผู้เล่น (เช่น '10 7' หรือปล่อยว่างถ้าไม่มี): ").strip()
    player_cards = player_cards_input.upper().split() if player_cards_input else []
    dealer_prob = [card_to_value(card) for card in dealer_cards]
    player_prob = [card_to_value(card) for card in player_cards]

    # สร้างสำรับไพ่
    deck = create_deck()

    # เอาไพ่เริ่มต้นของเจ้ามือออกจากสำรับ
    for card in dealer_cards:
        deck.remove(card)  # ลบทีละใบ

    # เอาไพ่ของผู้เล่นออกจากสำรับ (ถ้ามี)
    for card in player_cards:
        deck.remove(card)  # ลบทีละใบ

    # คำนวณความน่าจะเป็นที่เจ้ามือและผู้เล่นจะ bust
    bust_dealer = calculate_bust_probability(dealer_prob, deck, stop_at=17)
    bust_player = calculate_bust_probability(player_prob, deck, stop_at=21)  # ผู้เล่นหยุดจั่วที่ 21

    print(f"ความน่าจะเป็นที่เจ้ามือจะ bust : {bust_dealer:.2%}")
    print(f"ความน่าจะเป็นที่ผู้เล่นจะ bust : {bust_player:.2%}")
    print(f"จำนวนไพ่ในสำรับที่เหลือ: {len(deck)} : {deck}")
