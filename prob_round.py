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

def prob_blackjack(deck, dealer_total, player_total):
    left_card = len(deck)
    tie = 0
    dealer_win = 0
    player_win = 0
    dealer_pick_card = 0

    for i in range(left_card):
        card = deck[i]
        dealer_new_total = dealer_total + card
        
        # Blackjack
        if player_total == 21 or dealer_total == 21 or dealer_new_total == 21:
            if dealer_total == 21 and player_total == 21:
                tie = left_card
            elif dealer_total == 21:
                dealer_win += 1
            # ในกรณี dealer แต้มไม่ถึง 17 สามารถจั่วไพ่เพิ่มได้เรื่อยๆ
            elif dealer_new_total == 21:
                tie += 1
            else:
                player_win += 1

        # player bust
        elif player_total > 21:
            dealer_win += 1

        elif dealer_new_total >= 17 and dealer_new_total <= 21:
            if dealer_new_total > player_total:
                dealer_win += 1
            elif dealer_new_total < player_total:  
                player_win += 1
            else:
                tie += 1                
        
        elif dealer_new_total < 17:
            dealer_pick_card += 1
        
        # Dealer bust
        elif dealer_new_total > 21:
            player_win += 1

    # แสดงผลลัพธ์
    print(tie + dealer_win + player_win + dealer_pick_card, "/", left_card)
    return print(
        f"Tie: {tie}/{left_card}\nDealer win: {dealer_win}/{left_card}\n"
        f"Player win: {player_win}/{left_card}\nDealer pick card: {dealer_pick_card}/{left_card}"
    )

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


    prob_blackjack(deck, dealer_total, player_total)


    # แสดงจำนวนไพ่ในสำรับที่เหลือ
    print(dealer_total)
    print(player_total)
    print(f"จำนวนไพ่ในสำรับที่เหลือ: {len(deck)} : {deck}")