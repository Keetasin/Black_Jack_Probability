import random

# Create card 
def create_deck():
    deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4
    return deck

# HI-LO system
def update_running_count(card):
    
    global running_count
    high_card = [10, 'J', 'Q', 'K', 'A']
    if card in high_card:
        running_count -= 1
    elif card.isdigit() and 2 <= int(card) <= 6:
        running_count += 1
    
if __name__ == "__main__":
    
    running_count = 0 

    deck = create_deck()
    print(deck)
    for i in range(52):

        card = random.choice(deck)
        deck.pop(deck.index(card))
        print("Card :", card)
        print("Point :", running_count) 
        update_running_count(card)
        print("Point :", running_count)

        if running_count > 0:
            print(f"{running_count} high cards left in the deck, dealer's chance of busting when drawing additional cards.")
        elif running_count < 0:
            print(f"{running_count} low cards left in the deck, increasing Blackjack or a high hand, reducing the dealer's chance of busting.")    
        print("left card :", len(card))