import random

# Create card 
def create_deck():
    deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'K', 'Q', 'A'] * 4
    return deck

# HI-LO system
# def update_running_count(card):
    
#     global running_count
#     high_card = [10, 'J', 'Q', 'K', 'A']
#     if card in high_card:
#         running_count -= 1
#     elif card.isdigit() and 2 <= int(card) <= 6:
#         running_count += 1

def prob_card():
    global high_card
    global low_card
    global common_card

    set_high_card = [10, 'J', 'K', 'Q', 'A']
    if card in set_high_card:
        high_card -= 1
    elif 2 <= card <= 6:
        low_card -= 1
    else:
        common_card -= 1

    print(f" high card {high_card}/20 ({(high_card/52)*100})\n low card {low_card}/20 ({(low_card/52)*100})\n common card {common_card}/12 ({(common_card/52)*100}) ")
 
if __name__ == "__main__":
    
    running_count = 0 
    high_card = 20
    low_card = 20
    common_card = 12                

    deck = create_deck()
    print(deck)
    print(len(deck))
    for i in range(5):

        card = random.choice(deck)
        deck.pop(deck.index(card))
        print("Card :", card)
        prob_card()
    print(len(deck))

        # print("Point :", running_count) 
        # update_running_count(card)
        # print("Point :", running_count)

        # if running_count > 0:
        #     print(f"{running_count} high cards left in the deck, dealer's chance of busting when drawing additional cards.")
        # elif running_count < 0:
        #     print(f"{running_count} low cards left in the deck, increasing Blackjack or a high hand, reducing the dealer's chance of busting.")    
        # print("left card :", len(deck))