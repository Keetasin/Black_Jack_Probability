### Import packages
import cv2
import os
import numpy as np
import matplotlib.pyplot as plt  # เพิ่มการแสดงผลทีละภาพ

### Constants ###
# Debugging
DEBUG_MODE = False
WRITE_IMAGES = False

# Card dimensions
CARD_MAX_AREA = 1000000
CARD_MIN_AREA = 70000

CARD_MAX_PERIM = 1000
CARD_MIN_PERIM = 200

RANK_HEIGHT = 125
RANK_WIDTH = 70

CARD_WIDTH = 200
CARD_HEIGHT = 300

# Polymetric approximation accuracy scaling factor
POLY_ACC_CONST = 0.02

# Matching algorithms
HU_MOMENTS = 0
TEMPLATE_MATCHING = 1
MAX_MATCH_SCORE = 3000

### Structures ###
class Rank:
    """Structure to store information about each card rank."""

    def __init__(self, name="", img=None, contour=None, value=0):
        self.name = name
        self.img = img if img is not None else []
        self.contour = contour if contour is not None else []
        self.value = value

class Card:
    """Structure to store information about cards in the camera image."""

    def __init__(self):
        self.contour = []  # Contour of card
        self.corner_pts = []  # Corner points of card
        self.center = []  # Center point of card
        self.img = []  # Top-down flattened image of the card
        self.rank_img = []  # Thresholded, sized image of card's rank
        self.rank_contour = []  # Contour of the rank
        self.best_rank_match = "Unknown"  # Best matched rank
        self.rank_score = 0  # Difference between rank image and best matched train rank image
        self.value = 0  # Numerical value of the rank

 

    def process_card(self, image):
        """Process and flatten the card image to extract rank."""
        x, y, w, h = cv2.boundingRect(self.contour)
        self.center = np.mean(self.corner_pts, axis=0).astype(int).tolist()[0]

        # Step 1: Flatten the card to a top-down view
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.img = flattener(gray, self.corner_pts, w, h)

        # Display the flattened card
        # plt.imshow(self.img, cmap='gray')
        # plt.title("Top-Down View of Card")
        # plt.show()

        # Step 2: Crop the top-left corner
        rank_img = self.img[0:55 , 0:35]         # cropppp
        pad_value = np.median(rank_img)
        rank_img_padded = np.pad(rank_img, 5, 'constant', constant_values=pad_value)

        _, thresh = cv2.threshold(rank_img_padded, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresh = cv2.bitwise_not(thresh)

        # Display the cropped and thresholded top-left corner
        # plt.imshow(thresh, cmap='gray')
        # plt.title("Cropped Top-Left Corner for Rank")
        # plt.show()

        # Step 3: Extract rank contour
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        if contours:
            self.rank_contour = contours[0]
            x1, y1, w1, h1 = cv2.boundingRect(contours[0])
            rank_crop = thresh[y1:y1 + h1, x1:x1 + w1]
            self.rank_img = cv2.resize(rank_crop, (RANK_WIDTH, RANK_HEIGHT))

            # Display the final rank image for matching
            # plt.imshow(self.rank_img, cmap='gray')
            # plt.title("Final Rank Image for Matching")
            # plt.show()



    def match_rank(self, all_ranks, match_method, last_cards):
        # Ensure the rank image is in grayscale format
        if isinstance(self.rank_img, np.ndarray):  # Check if rank_img is a NumPy array
            if len(self.rank_img.shape) == 3:  # If image is BGR
                self.rank_img = cv2.cvtColor(self.rank_img, cv2.COLOR_BGR2GRAY)
        else:
            print("Error: Rank image is not a NumPy array.")
            return  # Add a return statement to prevent further processing

        # Match the rank using templates or HU moments
        match_scores = []
        for rank in all_ranks:
            if not isinstance(rank.img, np.ndarray):
                raise ValueError("Rank images must be NumPy arrays.")
            
            # Ensure comparison images are grayscale
            rank_img_compare = rank.img  # Already in grayscale
            if rank_img_compare is None:
                continue
            
            if match_method == HU_MOMENTS:
                match_scores.append(cv2.matchShapes(self.contour, rank.contour, 1, 0.0))
            elif match_method == TEMPLATE_MATCHING:
                diff_img = cv2.absdiff(self.rank_img, rank_img_compare)
                match_scores.append(int(np.sum(diff_img) / 255))
        
        ind = np.argmin(match_scores)
        self.rank_score = match_scores[ind]

        if self.rank_score < MAX_MATCH_SCORE:
            self.best_rank_match = all_ranks[ind].name
            self.value = all_ranks[ind].value

        # Reduce flickering using last matched cards
        if self.best_rank_match == "Unknown" and last_cards:
            for last_card in last_cards:
                if np.allclose(self.center, last_card.center, atol=10):
                    self.best_rank_match = last_card.best_rank_match
                    self.value = last_card.value

def detect(image, rank_path, last_cards):
    """Detects cards in an image and returns a list of processed card objects."""
    ranks = load_ranks(rank_path)
    cards = find_cards(image)

    for card in cards:
        card.process_card(image)
        card.match_rank(ranks, TEMPLATE_MATCHING, last_cards)
    return cards

def display(image, cards):
    """Draw detected cards with their best rank matches and corner points on the image."""
    for card in cards:
        # Draw the main card contour
        color = (0, 255, 0) if card.best_rank_match != "Unknown" else (0, 0, 255)
        cv2.drawContours(image, [card.contour], 0, color, 2)
        
        # Draw the corner points
        for pt in card.corner_pts:
            cv2.circle(image, tuple(pt[0]), 5, (255, 0, 0), -1)

        # Draw the bounding box
        x, y, w, h = cv2.boundingRect(card.contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 255), 2)

        # Display the card rank
        text_pos = (card.center[0] - 20, card.center[1])
        cv2.putText(image, card.best_rank_match, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    return image

def find_cards(image):
    """Find potential card contours in the input image."""
    cards = []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        for cnt in sorted_contours:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, POLY_ACC_CONST * peri, True)
            if CARD_MIN_AREA < cv2.contourArea(cnt) < CARD_MAX_AREA and len(approx) == 4:
                new_card = Card()
                new_card.contour = cnt
                new_card.corner_pts = approx
                cards.append(new_card)
    return cards

def load_ranks(path):
    """Load rank templates and store them as Rank objects."""
    rank_names = ['Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King']
    rank_values = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
    ranks = []

    for i, name in enumerate(rank_names):
        img_path = os.path.join(path, f"{name}.png")
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"Error loading rank image: {img_path}")  # Ensure grayscale loading
            continue  # Skip if the image is not found
        contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        ranks.append(Rank(name, img, contours[0], rank_values[i]))
    return ranks


def flattener(image, pts, w, h):
    """Flattens an image of a card into a top-down 200x300 perspective."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=2)
    rect[0], rect[2] = pts[np.argmin(s)], pts[np.argmax(s)]
    diff = np.diff(pts, axis=-1)
    rect[1], rect[3] = pts[np.argmin(diff)], pts[np.argmax(diff)]

    dst = np.array([[0, 0], [CARD_WIDTH - 1, 0], [CARD_WIDTH - 1, CARD_HEIGHT - 1], [0, CARD_HEIGHT - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (CARD_WIDTH, CARD_HEIGHT))

def is_card_inside_rect(card, rect):
    """ตรวจสอบว่าไพ่ตั้งอยู่ภายในกรอบสี่เหลี่ยมหรือไม่"""
    x1, y1, x2, y2 = rect  # (top-left-x, top-left-y, bottom-right-x, bottom-right-y)
    cx, cy = card.center  # ศูนย์กลางของไพ่
    return x1 <= cx <= x2 and y1 <= cy <= y2


def calculate_total_value(cards):
    """Calculate the total value of all detected cards."""
    total_value = sum(card.value for card in cards if card.value > 0)
    return total_value

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

def prob_blackjack(deck, dealer_total, player_total):
    left_card = len(deck)
    tie = 0
    dealer_win = 0
    player_win = 0
    dealer_pick_card_4 = 0

    for i in range(left_card):
        card = deck[i]
        dealer_new_total = dealer_total + card
        
        if card == 11 and dealer_new_total > 21:
            dealer_new_total = dealer_new_total - 10 

        # Blackjack
        if player_total == 21 or dealer_total == 21 or dealer_new_total == 21:
            if dealer_total == 21 and player_total == 21:
                tie += 1
            elif dealer_total == 21:
                dealer_win += 1
            # ในกรณี dealer แต้มไม่ถึง 17 สามารถจั่วไพ่เพิ่มได้เรื่อยๆ
            elif dealer_new_total == 21 and player_total == 21:
                tie += 1
            elif dealer_new_total == 21:
                dealer_win += 1    
            else:
                player_win += 1

        # player bust
        elif player_total > 21:
            dealer_win += 1

        elif 17 <= dealer_new_total <= 21:
            if dealer_new_total > player_total:
                dealer_win += 1
            elif dealer_new_total < player_total:  
                player_win += 1
            else:
                tie += 1                
        
        elif dealer_new_total < 17:
            dealer_pick_card_4 += 1
        
        # Dealer bust
        elif dealer_new_total > 21:
            player_win += 1

    return tie, dealer_win, player_win, dealer_pick_card_4
    


def process_folder(input_folder, output_folder, rank_path, last_cards=[]):
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Define rectangle for filtering (x1, y1, x2, y2)
    filter_rect_player = (500,600, 1500, 1100)  # กรอบสำหรับผู้เล่น
    filter_rect_dealer = (500,50, 1500, 520)  # กรอบสำหรับดีลเลอร์

    # สร้างสำรับไพ่
    deck = create_deck()

    # Loop through all images in the input folder
    for image_filename in os.listdir(input_folder):
        print('*' * 10)
        print(image_filename)
        image_path = os.path.join(input_folder, image_filename)

        # Read the input image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Cannot read image from {image_path}")
            continue
        

        # Detect cards in the image
        cards = detect(image, rank_path, last_cards)

        # Display the image with detected cards
        result_image = display(image, cards)
        
        if "round" in image_filename.lower():
            # Filter cards inside the rectangle
            filtered_cards_players = [card for card in cards if is_card_inside_rect(card, filter_rect_player)]
            filtered_cards_dealer = [card for card in cards if is_card_inside_rect(card, filter_rect_dealer)]
            
            # Calculate total value of filtered cards
            total_value_players = calculate_total_value(filtered_cards_players)
            total_value_dealer = calculate_total_value(filtered_cards_dealer)

            # Display the rectangle on the image
            cv2.rectangle(image, (filter_rect_player[0], filter_rect_player[1]), (filter_rect_player[2], filter_rect_player[3]), (255, 0, 0), 2)
            cv2.rectangle(image, (filter_rect_dealer[0], filter_rect_dealer[1]), (filter_rect_dealer[2], filter_rect_dealer[3]), (255, 0, 0), 2)

            # Add text showing total value of cards in each rectangle
            cv2.putText(image, f"Player: {total_value_players}", 
                        (filter_rect_player[2]-150, filter_rect_player[1] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(image, f"Dealer: {total_value_dealer}", 
                        (filter_rect_dealer[2]-150, filter_rect_dealer[1] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
            if "_0pre" in image_filename.lower():
                cv2.putText(image, "Player's turn", 
                            (1510,1000), cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 155, 250), 4)
                                
                dealer_cards_pre = [card.value for card in filtered_cards_dealer]
                player_cards_pre = [card.value for card in filtered_cards_players]

                for card_value in dealer_cards_pre + player_cards_pre:
                    if card_value in deck:
                        deck.remove(card_value)

                bust_player = calculate_bust_probability(player_cards_pre, deck, stop_at=21)  # ผู้เล่นหยุดจั่วที่ 21
                
                if sum(player_cards_pre) < 21:
                    cv2.putText(image, f"player will bust: {bust_player:.2%}", 
                                (filter_rect_player[2]-150, filter_rect_player[3] - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            
            if "_1post" in image_filename.lower():
                cv2.putText(image, "Dealere's turn", 
                            (1500,200), cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 155, 250), 4)
                
                if (total_value_dealer == total_value_players) or (total_value_players>21 and total_value_dealer>21):
                    cv2.putText(image, "Draw", (200,600),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 6)
                elif ((total_value_players > total_value_dealer)and total_value_players < 22) or (total_value_dealer>21):
                    cv2.putText(image, "Player Win", (10,600),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 6)
                elif ((total_value_dealer > total_value_players)and total_value_dealer < 22) or (total_value_players>21):
                    cv2.putText(image, "Dealer Win", (10,600),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 6)

                dealer_cards_post = [card.value for card in filtered_cards_dealer]
                # player_cards_post = [card.value for card in filtered_cards_players]
                
                open = [i for i in dealer_cards_post if i not in dealer_cards_pre]
                print(f'open: {open}')
                for card_value in open:
                    if card_value in deck:
                        deck.remove(card_value)


                bust_dealer = calculate_bust_probability(dealer_cards_post, deck, stop_at=17)  # ผู้เล่นหยุดจั่วที่ 21
                tie, dealer_win, player_win, dealer_pick_card_4 = prob_blackjack(deck, sum(dealer_cards_post), total_value_players)

                if sum(dealer_cards_post) < 17:
                    cv2.putText(image, f"dealer will bust: {bust_dealer:.2%}", 
                                (filter_rect_player[2]-150, filter_rect_player[1] - 500), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    
                left_card = len(deck)
                print(f"จำนวนไพ่ในสำรับที่เหลือ: {left_card} : {deck}") #ยังไม่ลบใบคว่ำ
                cv2.putText(image, f"result: {tie + dealer_win + player_win + dealer_pick_card_4} / {left_card}", 
                            (1520,500), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(image, f"Tie: {tie/left_card:.2%}", 
                            (1520,550), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(image, f"Dealer win: {dealer_win/left_card:.2%}", 
                            (1520,600), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(image, f"Player win: {player_win/left_card:.2%}", 
                            (1520,650), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(image, f"Dealer pick card: {dealer_pick_card_4/left_card:.2%}", 
                            (1520,700), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    


            if total_value_players == 21:
                    cv2.putText(image, "Black Jack", (10,900),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 6)
            if total_value_dealer == 21:
                    cv2.putText(image, "Black Jack", (10,200),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 6)

            if total_value_players > 21:
                    cv2.putText(image, "Bust", (10,900),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 6)
            if total_value_dealer > 21:
                    cv2.putText(image, "Bust", (10,200),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 6)



            # Save the result in the output folder
            output_path = os.path.join(output_folder, image_filename)
            cv2.imwrite(output_path, result_image)

            print(f"players: {total_value_players}")
            print(f"dealer: {total_value_dealer}")
            print([card.value for card in filtered_cards_players])
            print([card.value for card in filtered_cards_dealer])
        else:
            print('-'*5)


if __name__ == "__main__":
    input_folder = 'images'
    output_folder = 'images/detected'
    rank_path = 'template'  # Directory containing rank images (Ace.png, Two.png, etc.)
    process_folder(input_folder, output_folder, rank_path)


