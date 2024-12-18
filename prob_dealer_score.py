def create_deck():
    """สร้างสำรับไพ่ 1 สำรับในรูปแบบค่าตัวเลข"""
    deck = []
    for rank in range(2, 11):  # ไพ่เลข 2-10
        deck.extend([rank] * 4)
    deck.extend([10] * 12)  # ไพ่ J, Q, K มีค่าเท่ากับ 10 (12 ใบ)
    deck.extend([11] * 4)   # ไพ่ A มีค่าเริ่มต้นเป็น 11 (4 ใบ)
    return deck

def calculate_total(hand):
    """คำนวณแต้มรวมของไพ่ในมือ"""
    total = sum(hand)
    aces = hand.count(11)  # จำนวน A ที่มีค่า 11
    while total > 21 and aces:
        total -= 10  # ลดค่า A จาก 11 เป็น 1
        aces -= 1
    return total

def calculate_bust_probability(hand, deck, stop_at=int()):
    """
    คำนวณความน่าจะเป็นที่ไพ่ในมือจะ bust
    :param hand: ไพ่ในมือเป็นค่าตัวเลข (list)
    :param deck: สำรับไพ่ที่เหลืออยู่
    :param stop_at: แต้มที่หยุดจั่วไพ่ (default: 17)
    :return: ความน่าจะเป็นที่ bust
    """
    total = calculate_total(hand)
    
    # ตรวจสอบกรณีที่ไพ่ในมือเริ่มต้น bust
    if total > 21:
        return 1.0  # 100% ที่ bust
    if total >= stop_at:
        return 0.0  # ไม่จั่วไพ่เพิ่มเติม

    # คำนวณความน่าจะเป็น bust หากยังไม่ bust และแต้มไม่ถึง stop_at
    bust_count = 0
    for card_value in deck:
        if card_value == 11:  # ไพ่ Ace (มีค่าได้ทั้ง 11 และ 1)
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
    input_cards = input("กรุณากรอกแต้มเริ่มต้นของเจ้ามือ (เช่น '10 11' หรือ '11 5'): ")
    dealer_cards = list(map(int, input_cards.split()))  # แปลงแต้มไพ่เป็นตัวเลข

    # รับไพ่ของผู้เล่น
    player_cards_input = input("กรุณากรอกแต้มของผู้เล่น (เช่น '7 11' หรือปล่อยว่างถ้าไม่มี): ").strip()
    player_cards = list(map(int, player_cards_input.split())) if player_cards_input else []

    # สร้างสำรับไพ่
    deck = create_deck()

    # เอาไพ่เริ่มต้นของเจ้ามือและผู้เล่นออกจากสำรับ
    for card_value in dealer_cards + player_cards:
        if card_value in deck:
            deck.remove(card_value)  # ลบค่าทีละใบ

    # คำนวณแต้มรวมของเจ้ามือและผู้เล่น
    dealer_total = calculate_total(dealer_cards)
    player_total = calculate_total(player_cards)

    # ตรวจสอบ bust
    if dealer_total > 21:
        print("เจ้ามือ bust!")
    elif dealer_total == 21:
        print("เจ้ามือ blackjack!")
    else:
        bust_dealer = calculate_bust_probability(dealer_cards, deck, stop_at=17)
        print(f"ความน่าจะเป็นที่เจ้ามือจะ bust : {bust_dealer:.2%}")

    if player_total > 21:
        print("ผู้เล่น bust!")
    if player_total == 21:
        print("ผู้เล่น blackjack!")
    else:
        bust_player = calculate_bust_probability(player_cards, deck, stop_at=21)  # ผู้เล่นหยุดจั่วที่ 21
        print(f"ความน่าจะเป็นที่ผู้เล่นจะ bust : {bust_player:.2%}")

    # แสดงจำนวนไพ่ในสำรับที่เหลือ
    print(f"จำนวนไพ่ในสำรับที่เหลือ: {len(deck)} : {deck}")

